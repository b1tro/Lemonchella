import asyncio
from asyncio import sleep as asleep
import datetime
from typing import Tuple

import telethon
import time
import aiogram
from decimal import Decimal

import config
from logger import logger
from aiogram.types import (
    InputFile,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
    Message,
)
from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
)
from pymongo import ASCENDING, DESCENDING
from aiogram.types.base import UNSET_DISABLE_WEB_PAGE_PREVIEW, UNSET_PARSE_MODE
from telethon.tl.functions.messages import CreateChatRequest, ExportChatInviteRequest, AddChatUserRequest, \
    EditChatAdminRequest, MigrateChatRequest
from telethon.tl.functions.channels import InviteToChannelRequest, TogglePreHistoryHiddenRequest, EditAdminRequest
from telethon.tl.types import ChatAdminRights, Updates
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.types import InputPeerChat, InputUser, InputChannel
from beanie.operators import Set
from config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    OKLINK_API_KEY,
    CONFIG_CACHE_TIME,
)
from bot.types import ChainName, TokenName, WalletAddressLike
from telethon.tl.functions.folders import EditPeerFoldersRequest
from telethon.tl.types import InputFolderPeer
from models import User, Product, Category, UserCache, HotConfig, Order, Addon, AddonCustomer, Customer
from config import USER_CACHE_TIME, ACTIVE_PRODUCTS_DIR, ARCHIVED_PRODUCTS_DIR, GOOGLE_SERVICE_KEY_PATH, \
    GOOGLE_SHEET_URL, GOOGLE_SHEETS_ENABLED
from models.order import OrderItem
from redis.asyncio import Redis
from models.payment import BalancePayment, CryptoTransaction
from . import controllers
from ..bot import redis, bot, loop, userbot, buyer_bot, userbot_group
from .payment import address_equals, CryptoCore
from .sheets import GoogleSheets

crypto_core = CryptoCore(
    binance_api_key=BINANCE_API_KEY,
    binance_api_secret=BINANCE_API_SECRET,
    oklink_api_key=OKLINK_API_KEY
)
sheets = GoogleSheets(
    service_key_path=str(GOOGLE_SERVICE_KEY_PATH)
) if GOOGLE_SHEETS_ENABLED else None
redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
)

admin_rights = ChatAdminRights(
    change_info=True,
    post_messages=True,
    edit_messages=True,
    delete_messages=True,
    ban_users=True,
    invite_users=True,
    pin_messages=True,
    add_admins=True,
    anonymous=None,
    manage_call=True,
    other=True,
    manage_topics=True,
    post_stories=True,
    edit_stories=True,
    delete_stories=True
)


async def get_user(user_id: int) -> User:
    """Find's a user in database by ID, returns None if not found."""
    user = await User.find_one({User.id: user_id})
    return user


async def get_customer(user_id: int) -> Customer:
    """Find's a user in database by ID, returns None if not found."""
    customer = await Customer.find_one({Customer.id: user_id})
    return customer


async def get_user_referrals_quantity(user_id: int) -> int:
    return await User.find_one({User.referrer_id: user_id}).count()


async def get_user_order(user_id: int, order_id) -> Order:
    return await Order.find_one({Order.user_id: user_id, Order.id: order_id})


async def get_users_count() -> int:
    return await User.count()


async def get_all_users() -> list:
    return await User.all().to_list()


async def get_items_count() -> int:
    return await Product.count()


async def get_user_order_history(user_id: int, limit: int = 10) -> list[Order]:
    return [
        order async for order in Order.find_many(
            {Order.user_id: user_id},
            limit=limit,
            sort=[('created_at', DESCENDING)]
        )
    ]


async def get_customers(min_sum: int = 0) -> list[Customer]:
    return [
        customer async for customer in Customer.find_many(
            {
                Customer.minimum_sum: {"$lte": min_sum},
                Customer.is_blocked: False,
            },
        )
    ]


async def get_orders(status: str = None, customer_sum: int = 0) -> list[Order]:
    return [
        order async for order in Order.find_many(
            {
                Order.status: status,
                Order.total_customer: {"$gte": customer_sum}},
            sort=[('created_at', DESCENDING)]
        )
    ]


async def update_user_balance(user_id: int, value: float, popup_type: str) -> int:
    user_id = int(user_id)
    user = await controllers.get_user(user_id)
    if user is None:
        raise ValueError(f'Could not find User(id={user_id})')
    r = 0
    if popup_type == '1':
        user.balance += Decimal(value)
        r = user.balance
    elif popup_type == '2':
        user.referral_balance += Decimal(value)
        user.earned_by_referrals += Decimal(value)
        r = user.referral_balance
    elif popup_type == '3':
        user.referral_balance -= Decimal(value)
        r = user.referral_balance
    popup_types = {'1': 'balance', '2': 'referral_balance', '3': 'earned_by_refferals'}
    logger.info(f'Adding {value} to {user_id} to {popup_types[popup_type]}')
    await user.save()
    return r


async def get_user_cache(user_id: int) -> UserCache:
    """Find's a user's cache in redis database."""
    key = f'UserCache(id={user_id})'
    value = await redis.get(key)
    if value is None:
        return UserCache()
    return UserCache.model_validate_json(value)


async def set_user_cache(user_id: int, cache: UserCache | str):
    """Sets the user's cache to redis database."""
    key = f'UserCache(id={user_id})'
    if type(cache) is UserCache:
        cache = cache.model_dump_json()
    await redis.set(
        key,
        value=cache,
        ex=USER_CACHE_TIME,
    )


async def get_product(product_id: int, ignore_cache: bool = False) -> Product:
    """Find's a product in database by ID, returns None if not found."""
    product_id = int(product_id)
    key = f'Product(id={product_id})'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            result = Product.model_validate_json(result)

            _value = {}

            for k in result.price.keys():
                _value[int(k)] = result.price[k]

            result.price = _value

            return result
    result = await Product.find_one({Product.id: product_id})
    if result is None:
        raise ValueError(f'Could not find Product(id={product_id})')


async def get_order(order_id: int, ignore_cache: bool = False) -> Order:
    """Find's an order in database by telegram_chat_id, returns None if not found."""
    order_id = int(order_id)
    key = f'Order(id={order_id})'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            return Order.model_validate_json(result)
    result = await Order.find_one({Order.id: order_id})

    async def set_result():
        dumped_result = Order.model_dump_json(result)
        await redis.set(key, dumped_result, ex=CONFIG_CACHE_TIME)

    if result is not None:
        asyncio.get_running_loop().create_task(set_result())
    return result


async def get_order_by_telegram_chat_id(telegram_chat_id: int, ignore_cache: bool = False) -> Order:
    """Find's an order in database by telegram_chat_id, returns None if not found."""
    telegram_chat_id = int(telegram_chat_id)
    key = f'Order(telegram_chat_id={telegram_chat_id})'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            return Order.model_validate_json(result)
    result = await Order.find_one({Order.telegram_chat_id: telegram_chat_id})

    async def set_result():
        dumped_result = Order.model_dump_json(result)
        await redis.set(key, dumped_result, ex=CONFIG_CACHE_TIME)

    if result is not None:
        asyncio.get_running_loop().create_task(set_result())
    return result


async def get_hotconfig(ignore_cache: bool = False) -> HotConfig:
    """Find's a bot config in database, returns None if not found."""
    key = 'HotConfig(id=1)'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            return HotConfig.model_validate_json(result)
    result = await HotConfig.find_one({HotConfig.id: 1})
    if result is None:
        raise ValueError('Could not find HotConfig(id=1)')

    async def set_result():
        dumped_result = HotConfig.model_dump_json(result)
        await redis.set(key, dumped_result, ex=CONFIG_CACHE_TIME)

    asyncio.get_running_loop().create_task(set_result())
    return result


async def get_category(category_id: int, ignore_cache: bool = False) -> Category:
    """Find's a category in database by ID, returns None if not found."""
    category_id = int(category_id)
    key = f'Category(id={category_id})'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            return Category.model_validate_json(result)
    result = await Category.find_one({Category.id: category_id})
    if result is None:
        raise ValueError(f'Could not find Category(id={category_id})')

    async def set_result():
        dumped_result = Category.model_dump_json(result)
        await redis.set(key, dumped_result, ex=CONFIG_CACHE_TIME)

    asyncio.get_running_loop().create_task(set_result())
    return result


async def create_user(
        user_telegram: aiogram.types.User, referrer_id: int = None
) -> User:
    """Creates a new user in database if not exists."""
    user_referrer_id = None
    if referrer_id and referrer_id != user_telegram.id:
        referrer = await User.find_one({User.id: referrer_id})
        if referrer and not referrer.is_blocked:
            user_referrer_id = referrer.id
    user = User(
        id=user_telegram.id,
        telegram=user_telegram,
        lang=None,
        referrer_id=user_referrer_id,
    )
    await User.find_one({User.id: user_telegram.id}).upsert(
        Set(user.model_dump()), on_insert=user
    )
    return user


async def create_customer(
        user_telegram: aiogram.types.User
) -> Customer:
    """Creates a new customer in database if not exists."""
    customer = Customer(
        id=user_telegram.id,
        username=user_telegram.username,
        language='ru' if user_telegram.language_code == 'ru' else 'en',
    )
    await Customer.find_one({Customer.id: Customer.id}).upsert(
        Set(customer.model_dump()), on_insert=customer
    )
    return customer


async def fetch_user(
        user_telegram: aiogram.types.User, referrer_id: int = None
) -> User:
    """Finds user in database, or creates and returns if not exists."""
    user = await controllers.get_user(user_telegram.id)
    if user is None:
        user = await controllers.create_user(user_telegram, referrer_id)
    return user


async def send_message(
        chat_id: int,
        text: str,
        photo: InputFile | str = None,
        document: InputFile | str = None,
        parse_mode: str = UNSET_PARSE_MODE,
        reply_markup: (
                InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | list
        ) = None,
        disable_web_page_preview: bool = UNSET_DISABLE_WEB_PAGE_PREVIEW,
        reply_to_message_id: int = None
) -> Message:
    base_args = dict(
        chat_id=chat_id,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
        reply_to_message_id=reply_to_message_id
    )
    if type(reply_markup) is list:
        reply_markup = InlineKeyboardMarkup(inline_keyboard=reply_markup)
    if photo:
        return await bot.send_photo(
            **base_args,
            photo=photo,
            caption=text,
        )
    elif document:
        return await bot.send_document(
            **base_args,
            document=document,
            caption=text,
        )
    else:
        return await bot.send_message(
            **base_args,
            text=text,
            disable_web_page_preview=disable_web_page_preview,
        )


async def find_incoming_transaction(
        chain: ChainName,
        token: TokenName,
        to_wallet: WalletAddressLike,
        amount: Decimal,
        from_time: float,
        timeout: int,
) -> CryptoTransaction:
    def tx_filter(tx: CryptoTransaction):
        if all((
                tx.received_at.timestamp() >= from_time,
                address_equals(tx.to_wallet, to_wallet,
                               chain) if chain != 'BP' else tx.to_wallet == config.BINANCE_USER_ID,
                tx.token == token,
                tx.amount == amount
        )):
            return True
        return False

    start = time.time()
    while time.time() < (start + timeout):
        found_transactions = await crypto_core.get_transactions_history(
            chain=chain,
            wallet=to_wallet,
            tx_filter=tx_filter
        )
        if len(found_transactions) != 0:
            return found_transactions[0]
        else:
            await asyncio.sleep(5)
    return False


def take_product_copies(product_id: int, quantity: int) -> list[str]:
    product_id_string = str(product_id)
    product_copies = []

    for product_file in ACTIVE_PRODUCTS_DIR.iterdir():
        if product_file.suffix == '.txt' and product_file.stem.split(':', maxsplit=1)[0].strip() == product_id_string:
            all_lines = [
                line.strip()
                for line in product_file.read_text(encoding='utf-8').split('\n')
                if line.strip() != ''
            ]
            taken_lines = all_lines[:quantity]
            if len(taken_lines) > 0:
                remaining_lines = all_lines[quantity:]
                if len(remaining_lines) > 0:
                    product_file.write_text(data='\n'.join(remaining_lines), encoding='utf-8')
                else:
                    product_file.unlink()
                archiced_products_file = ARCHIVED_PRODUCTS_DIR / product_file.name
                try:
                    archiced_products_file_text = archiced_products_file.read_text(encoding='utf-8') + '\n'
                except FileNotFoundError:
                    archiced_products_file_text = ''
                archiced_products_file.write_text(
                    data=archiced_products_file_text + '\n'.join(taken_lines),
                    encoding='utf-8'
                )
            product_copies += taken_lines
            quantity -= len(taken_lines)
            if quantity == 0:
                break
    return product_copies


async def charge_balance_payment(balance_payment: BalancePayment):
    return await User.find_one({User.id: balance_payment.user_id}).inc(
        {User.balance: -balance_payment.amount}
    )


async def create_telegram_chat(order: Order) -> tuple[str, int, str, int]:
    # User`s group create
    async with userbot:
        invited_users: telethon.types.messages.InvitedUsers = await userbot(CreateChatRequest(
            users=['me'],
            title=f"Заказ #{order.pid}"
        ))
        chat_user = invited_users.updates.chats[0]
        chat_invite_user: telethon.types.ChatInviteExported = await userbot(
            ExportChatInviteRequest(
                peer=InputPeerChat(chat_id=chat_user.id),
            )
        )
        me_bot = await buyer_bot.get_me()
        bot_entity = await userbot.get_entity(me_bot.username)
        try:
            await userbot(AddChatUserRequest(chat_id=chat_user.id, user_id=bot_entity, fwd_limit=10))
        except Exception as error:
            logger.error(f"Cannot add bot {bot.id} to chat, error: {error}")

        result: Updates = await userbot(
            MigrateChatRequest(chat_id=chat_user.id)
        )
        channel_user = result.chats[0].migrated_to
        try:
            await userbot(EditAdminRequest(
                channel=channel_user,
                user_id=bot_entity,
                admin_rights=admin_rights,
                rank='Исполнитель'
            ))
            await userbot(EditAdminRequest(
                channel=channel_user,
                user_id=5609806336,
                admin_rights=admin_rights,
                rank='Менеджер'
            ))
        except Exception as error:
            logger.error(f"Cannot add title to bot: {error}")
        try:
            await userbot(TogglePreHistoryHiddenRequest(
                channel=channel_user,
                enabled=False
            ))
        except Exception as error:
            logger.error(f"Cannot make messages visible: {error}")
        await asleep(2)

    # Manager`s group create
    async with userbot_group:
        bot_entity = await userbot_group.get_entity(me_bot.username)
        invited_users: telethon.types.messages.InvitedUsers = await userbot_group(CreateChatRequest(
            users=['me'],
            title=f"Заказ #{order.pid} - Manager"
        ))
        try:
            chat_manager = invited_users.updates.chats[0]
            chat_invite_manager: telethon.types.ChatInviteExported = await userbot_group(
                ExportChatInviteRequest(
                    peer=InputPeerChat(chat_id=chat_manager.id),
                )
            )
        except Exception as error:
            logger.error(f"Cannot create manager chat: {error}")
        try:

            await userbot_group(AddChatUserRequest(chat_id=chat_manager.id, user_id=bot_entity, fwd_limit=10))
        except Exception as error:
            logger.error(f"Cannot add bot {bot.id} to chat, error: {error}")
        result: Updates = await userbot_group(
            MigrateChatRequest(chat_id=chat_manager.id)
        )
        channel_manager = result.chats[0].migrated_to

        await asleep(2)

        try:
            await userbot_group(EditAdminRequest(
                channel=channel_manager,
                user_id=bot_entity,
                admin_rights=admin_rights,
                rank='Покупатель'
            ))
        except Exception as error:
            logger.error(f"Cannot add title to bot: {error}")
        try:
            await userbot_group(TogglePreHistoryHiddenRequest(
                channel=channel_manager,
                enabled=False
            ))
        except Exception as error:
            logger.error(f"Cannot make messages visible: {error}")
        try:
            peer = await userbot_group.get_input_entity(channel_manager.channel_id)
            await userbot_group(LeaveChannelRequest(
                channel=peer
            ))
        except Exception as e:
            logger.info(f"Error while archiving chat: {e}")
    return chat_invite_user.link, int(f'-100{channel_user.channel_id}'), chat_invite_manager.link, int(
        f'-100{channel_manager.channel_id}')


async def new_order(
        user_id: int,
        order_items: list[OrderItem],
        total: Decimal,
        total_customer: Decimal,
        addons_answers: list,
        referrer_id: int = None,
        referral_amount: Decimal = None,
        user_username: str = None,
        payment: CryptoTransaction = None,
        balance_payment: BalancePayment = None,
        answers: dict = None,
        deadline: datetime = None,
):
    delivered_order_items = []
    for order_item in order_items:
        product = await get_product(product_id=order_item.product_id)
        delivered_copies = take_product_copies(order_item.product_id, order_item.quantity)
        new_order_item = OrderItem(
            product_id=order_item.product_id,
            product_name=product.name,
            quantity=order_item.quantity,
            delivered_copies=delivered_copies if delivered_copies else None,
            delivered_quantity=len(delivered_copies) if len(delivered_copies) else 0
        )
        delivered_order_items.append(new_order_item)
    order = Order(
        status='Confirmed',
        user_id=user_id,
        order_items=delivered_order_items,
        addon_answers=addons_answers,
        total=total,
        total_customer=total_customer,
        payment=payment,
        balance_payment=balance_payment,
        referrer_id=referrer_id,
        referral_amount=referral_amount,
        added_to_sheet=False,
        answers=answers,
        deadline=deadline,
    )
    logger.info('Created order')
    if order.order_items[0].delivered_quantity != order.order_items[0].quantity:
        telegram_chat_link, telegram_chat_id, telegram_chat_link_manager, telegram_chat_id_manager = await create_telegram_chat(
            order=order)
        order.telegram_chat_link, order.telegram_chat_id, order.telegram_chat_link_manager, order.telegram_chat_id_manager = telegram_chat_link, telegram_chat_id, telegram_chat_link_manager, telegram_chat_id_manager
    if GOOGLE_SHEETS_ENABLED:
        tries = 0
        while tries < 3:
            try:
                order_spreadsheet_url = sheets.create_order_table(order, user_username)
                order.order_sheet_url = order_spreadsheet_url
                break
            except Exception as error:
                logger.error(f'Error while creating order #{order.id} spreadsheet: {error}')
                await asleep(2)
                tries += 1
    if order.balance_payment:
        await charge_balance_payment(balance_payment)
        order.balance_payment.status = 'Success'
        order.balance_payment.received_at = datetime.datetime.now(datetime.timezone.utc)
    await Order.insert_one(order)
    product = await get_product(order.order_items[0].product_id)
    if GOOGLE_SHEETS_ENABLED:
        try:
            sheets.add_order(GOOGLE_SHEET_URL, order, user_username, product_name=product.name)
            order.added_to_sheet = True
        except Exception as error:
            logger.error(f'Error while adding order to google sheet: {error}')
    return order


async def get_addon(addon_id: int, ignore_cache: bool = False) -> Addon:
    """Find`s an addon in database by ID, returns None if not found"""
    addon_id = int(addon_id)
    key = f'Addon(id={addon_id})'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            result = Addon.model_validate_json(result)
            for option in result.options.keys():
                if isinstance(result.options[option], (int, float)):
                    result.options[option] = round(result.options[option], 2)
            return result
    result = await Addon.find_one({Addon.id: addon_id})
    if result is None:
        raise ValueError(f'Could not find Addon(id={addon_id})')

    async def set_result():
        dumped_result = Addon.model_dump_json(result)
        await redis.set(key, dumped_result, ex=CONFIG_CACHE_TIME)

    asyncio.get_running_loop().create_task(set_result())

    for option in result.options.keys():
        if isinstance(result.options[option], (int, float)):
            result.options[option] = round(result.options[option], 2)

    return result


async def get_addon_customer(addon_id: int, ignore_cache: bool = False) -> AddonCustomer:
    """Find`s an addon in database by ID, returns None if not found"""
    addon_id = int(addon_id)
    key = f'AddonCustomer(id={addon_id})'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            result = AddonCustomer.model_validate_json(result)
            for option in result.options.keys():
                if isinstance(result.options[option], (int, float)):
                    result.options[option] = round(result.options[option], 2)
            return result
    result = await AddonCustomer.find_one({AddonCustomer.id: addon_id})
    if result is None:
        raise ValueError(f'Could not find AddonCustomer(id={addon_id})')

    async def set_result():
        dumped_result = AddonCustomer.model_dump_json(result)
        await redis.set(key, dumped_result, ex=CONFIG_CACHE_TIME)

    asyncio.get_running_loop().create_task(set_result())

    for option in result.options.keys():
        if isinstance(result.options[option], (int, float)):
            result.options[option] = round(result.options[option], 2)

    return result


async def get_order_by_managers_link(telegram_chat_id_manager: int, ignore_cache: bool = False) -> Order:
    """Find's an order in database by telegram_chat_id_manager, returns None if not found."""
    telegram_chat_id_manager = int(telegram_chat_id_manager)
    key = f'Order(telegram_chat_id_manager={telegram_chat_id_manager})'
    if not ignore_cache:
        result = await redis.get(key)
        if result is not None:
            return Order.model_validate_json(result)
    result = await Order.find_one({Order.telegram_chat_id_manager: telegram_chat_id_manager})
    if result is None:
        raise ValueError(f'Could not find Order(telegram_chat_id_manager={telegram_chat_id_manager})')

    async def set_result():
        dumped_result = Order.model_dump_json(result)
        await redis.set(key, dumped_result, ex=CONFIG_CACHE_TIME)

    asyncio.get_running_loop().create_task(set_result())
    return result


async def update_google_sheets(order: Order):
    if not GOOGLE_SHEETS_ENABLED:
        return

    hotconfig = await get_hotconfig(ignore_cache=True)

    gid = hotconfig.SHEET_GID if not order.is_special else hotconfig.SHEET_GID_SPECIAL

    user = await get_user(order.user_id)
    customer = await get_customer(order.manager)

    row_id = sheets.find_row_by_order_id(gid=gid, order=order)

    referral = None
    if user.referrer_id is not None:
        referral = await get_user(user.referrer_id)

    if referral is not None:
        try:
            referral = referral.telegram.username
        except:
            referral = ''
    else:
        referral = ''

    sheets.update_google_sheets(
        order=order,
        gid=gid,
        username=user.telegram.username,
        customer=customer.username if customer is not None else '',
        referral=referral,
        exact_row=row_id
    )
