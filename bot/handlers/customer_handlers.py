import asyncio
import random
from decimal import Decimal
import inspect
import time
import datetime

import config
from bot.controllers import controllers
from logger import logger
from typing import Callable, Coroutine
from aiogram import Router, F
from aiogram.fsm.context import FSMContext, StorageKey
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, Message, FSInputFile, ReplyKeyboardRemove
from bot.filters import CallbackDataFilter
from asyncio import sleep as asleep
from models import (
    UserCache,
    User,
    OrderItem,
    CachedOrder,
    BalancePayment,
    CryptoTransaction,
    PaymentMethod,
    Order, Customer, order
)
from config import MAX_PRODUCT_QUANTITY, PAYMENT_MINUTES_TIMEOUT, ARCHIVED_PRODUCTS_DIR
from ..bot import loop, bot, payment_methods, dp, buyer_bot
from bot import states
from bot.keyboards import buttons
from bot import funcs, pictures, states, callbacks
from bot.sourcefile import pictures, texts
from bot.types import NavigationHistory
from telethon import events
import re
from telethon.types import InputUser
from telethon.tl.functions.messages import CreateChatRequest, ExportChatInviteRequest, AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest

texts = texts()
buttons = buttons.buttons()

roll_queue = {}

change_price_requests = {}


def register_handlers(router: Router):
    # message handlers
    router.message.register(
        handler_wrapper(menu_event),
        F.text.regexp("/start$"),
    )
    router.message.register(
        handler_wrapper(wallet_handler), states.change_wallet
    )
    router.message.register(
        handler_wrapper(sum_handler), states.min_sum
    )
    router.message.register(
        handler_wrapper(new_price_handler), states.change_price
    )
    # callback handlers
    router.callback_query.register(
        handler_wrapper(menu_event, delete_query_message=True),
        CallbackDataFilter(callbacks.MENU),
    )
    router.callback_query.register(
        handler_wrapper(settings_event, delete_query_message=True),
        CallbackDataFilter(callbacks.SETTINGS),
    )
    router.callback_query.register(
        handler_wrapper(withdraw_wallet_event, delete_query_message=True),
        CallbackDataFilter(callbacks.WITHDRAW_WALLET),
    )
    router.callback_query.register(
        handler_wrapper(change_wallet_event, delete_query_message=True),
        CallbackDataFilter(callbacks.CHANGE_WALLET),
    )
    router.callback_query.register(
        handler_wrapper(change_special_orders, delete_query_message=True),
        CallbackDataFilter(callbacks.SPECIAL_ORDERS)
    )
    router.callback_query.register(
        handler_wrapper(min_sum_event, delete_query_message=True),
        CallbackDataFilter(callbacks.MINIMUM_ORDER)
    )
    router.callback_query.register(
        handler_wrapper(claim_order),
        CallbackDataFilter(f"{callbacks.CLAIM_ORDER}:-?\\d+")
    )
    router.callback_query.register(
        handler_wrapper(claim_order_approve, delete_query_message=True),
        CallbackDataFilter(f"{callbacks.APPROVE_ORDER_CLAIM}:.+")
    )
    router.callback_query.register(
        handler_wrapper(claim_order_decline, delete_query_message=True),
        CallbackDataFilter(f"{callbacks.DECLINE_ORDER_CLAIM}:.+")
    )
    router.callback_query.register(
        handler_wrapper(change_price_request),
        CallbackDataFilter(f"{callbacks.CHANGE_PRICE_REQUEST}:.+")
    )
    router.callback_query.register(
        handler_wrapper(opened_orders_event),
        CallbackDataFilter(callbacks.OPENED_ORDERS)
    )
    router.callback_query.register(
        handler_wrapper(remove_self_from_order),
        CallbackDataFilter(f"{callbacks.REMOVE_SELF_ORDER}:.+")
    )


def handler_wrapper(
        callback: Callable[..., Coroutine],
        delete_query_message: bool = False,
):
    annotations = inspect.get_annotations(callback)

    async def wrapper(call: CallbackQuery | Message, state: FSMContext):
        user_id = call.from_user.id
        if Customer in annotations.values():
            customer = await controllers.get_customer(user_id=user_id)
            if customer is None:
                text = (
                    f"<b>{texts('ru').CANT_FIND_CUSTOMER}</b>"
                    if type(call) is Message
                    else texts('ru').CANT_FIND_CUSTOMER
                )
                await call.answer(text)
                return
            if customer.is_blocked:
                text = (
                    f"<b>{texts(customer.language).YOU_WERE_BLOCKED}</b>"
                    if type(call) is Message
                    else texts(customer.language).YOU_WERE_BLOCKED
                )
                await call.answer(text)
                return
            if not validate_wallet(customer.wallet):
                text = (
                    f"<b>{texts('ru').INVALID_WALLET}</b>"
                    if type(call) is Message
                    else texts('ru').INVALID_WALLET
                )
                await call.answer(text)
                return

        args = {}
        query = call if type(call) is CallbackQuery else None
        for arg_name, arg_type in annotations.items():
            if arg_type is Customer:
                args[arg_name] = customer
            elif arg_type is FSMContext:
                args[arg_name] = state
            elif arg_type is Message:
                args[arg_name] = call if type(call) is Message else None
            elif arg_type is CallbackQuery:
                args[arg_name] = query

        await callback(**args)
        if delete_query_message and query:
            try:
                await query.message.delete()
            except:
                pass

    return wrapper


async def cache_event(message: Message, cache: UserCache):
    await message.answer(
        text=f'<pre><code class="language-json">{cache.model_dump_json(indent=2)}</code></pre>'
    )


def validate_wallet(wallet: str):
    return wallet.startswith('0x') and len(wallet) == 42


async def menu_event(customer: Customer, state: FSMContext):
    keyboard = [[buttons(customer.language).MyOrders, buttons(customer.language).Settings],
                [buttons(customer.language).OpenedOrders, buttons(customer.language).Support]]

    await controllers.send_message(
        chat_id=customer.id,
        text=texts(customer.language).WELCOME,
        photo=pictures.CATALOG,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


async def settings_event(customer: Customer):
    keyboard = [[buttons(customer.language).MinimumOrderPrice(min_price=customer.minimum_sum)],
                [buttons(customer.language).SpecialOrders(current_state=customer.special_orders)],
                [buttons(customer.language).WithdrawWallet(is_set=validate_wallet(customer.wallet))],
                [buttons(customer.language).Back(callbacks.MENU)]
                ]

    await controllers.send_message(
        chat_id=customer.id,
        text=texts(customer.language).SETTINGS,
        photo=pictures.PARTNER,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


async def opened_orders_event(customer: Customer, state: FSMContext):
    orders = await controllers.get_orders(status='Confirmed', customer_sum=customer.minimum_sum)

    orders = [order for order in orders if str(customer.id) in order.message_id_direct.keys()]

    text = texts(customer.language).generate_opened_orders(orders, str(customer.id))

    await bot.send_message(
        chat_id=customer.id,
        text=text
    )


async def change_special_orders(customer: Customer):
    customer.special_orders = not customer.special_orders

    await customer.save()

    await settings_event(customer)


async def withdraw_wallet_event(customer: Customer):
    text = texts(customer.language).withdraw_wallet(customer.wallet)

    keyboard = [[buttons(customer.language).ChangeWallet],
                [buttons(customer.language).Back(callbacks.SETTINGS)]
                ]

    await controllers.send_message(
        chat_id=customer.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


async def change_wallet_event(customer: Customer, context: FSMContext):
    await context.set_state(states.change_wallet)

    await controllers.send_message(
        chat_id=customer.id,
        text=texts(customer.language).SEND_WALLET,
    )


async def wallet_handler(message: Message, customer: Customer, context: FSMContext):
    wallet = message.text

    if not validate_wallet(wallet):
        await controllers.send_message(
            chat_id=customer.id,
            text=texts(customer.language).INVALID_INPUT,
        )
        return

    await context.set_state()

    customer.wallet = wallet

    await customer.save()

    await controllers.send_message(
        chat_id=customer.id,
        text=texts(customer.language).SUCCESS_WALLET,
    )

    await withdraw_wallet_event(customer)


async def min_sum_event(customer: Customer, context: FSMContext):
    await context.set_state(states.min_sum)

    await controllers.send_message(
        chat_id=customer.id,
        text=texts(customer.language).SEND_SUM,
    )


async def sum_handler(message: Message, customer: Customer, context: FSMContext):
    try:
        order_sum = int(message.text)
    except:
        await controllers.send_message(
            chat_id=customer.id,
            text=texts(customer.language).INVALID_INPUT,
        )
        return

    await context.set_state()

    customer.minimum_sum = order_sum

    await customer.save()

    await settings_event(customer)


async def claim_order(query: CallbackQuery, customer: Customer):
    telegram_chat_id = query.data.split(':')[1]

    order = await controllers.get_order_by_telegram_chat_id(int(telegram_chat_id))

    if order.id in roll_queue.keys() and customer.id in roll_queue[order.id]:
        await query.answer(texts(customer.language).ALREADY_ORDER_REQUEST)
        return

    text = texts(customer.language).approve_order_claim(order.pid)

    keyboard = [[buttons(customer.language).ApproveOrderClaim(telegram_chat_id, str(query.message.message_id))],
                [buttons(customer.language).DeclineOrderClaim(telegram_chat_id, str(query.message.message_id))]]

    await controllers.send_message(
        chat_id=query.from_user.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


async def claim_order_approve(query: CallbackQuery, customer: Customer):
    telegram_chat_id, telegram_message_id = query.data.split(':')[1:]

    order = await controllers.get_order_by_telegram_chat_id(int(telegram_chat_id), ignore_cache=True)

    if order.manager is not None:
        await controllers.send_message(
            chat_id=customer.id,
            text=texts(customer.language).ORDER_ALREADY_TAKEN
        )
        return

    if order.id not in roll_queue.keys():
        roll_queue[order.id] = [customer.id]
        asyncio.create_task(choose_winner(order.id))
        logger.info(f'{customer.id} started roll {telegram_chat_id}')
    else:
        roll_queue[order.id].append(customer.id)
        logger.info(f'{customer.id} added to roll {telegram_chat_id}')

    await query.answer(texts(customer.language).SUCCESS_ORDER_REQUEST)


async def choose_winner(order_id: int):
    global roll_queue
    await asleep(60)

    order = await controllers.get_order(order_id, ignore_cache=True)

    user = await controllers.get_user(order.user_id)

    customers = [await controllers.get_customer(user_id=user_id) for user_id in roll_queue[order.id]]

    customer = random.choices(customers,
                              weights=[customer.rank for customer in
                                       customers], k=1)[0]

    print(customer.id)
    order.manager = customer.id
    order.status = 'Taken'
    order.sent_messages = []
    await order.save()

    await asleep(0.5)

    keyboard = [[buttons(customer.language).RemoveSelfOrder(order.id, str(customer.id))]]

    first_take = False

    if order.telegram_chat_id == order.id:
        first_take = True
        telegram_chat_link, telegram_chat_id, telegram_chat_link_manager, telegram_chat_id_manager = await controllers.create_telegram_chat(
            order=order)
        order.telegram_chat_link, order.telegram_chat_id, order.telegram_chat_link_manager, order.telegram_chat_id_manager = telegram_chat_link, telegram_chat_id, telegram_chat_link_manager, telegram_chat_id_manager
        await order.save(ignore_revision=True)
        await asleep(0.5)

    referrer = await controllers.get_user(user.referrer_id)

    hotconfig = await controllers.get_hotconfig()

    if order.is_special:
        if first_take:
            try:
                await buyer_bot.send_message(
                    chat_id=order.telegram_chat_id,
                    text=texts(user.lang).manager_chat_order(order=order, referrer=referrer,
                                                             username=user.telegram.username)
                )
                await buyer_bot.send_message(
                    chat_id=order.telegram_chat_id,
                    text=texts(user.lang).manager_wait(config=hotconfig)
                )
                await buyer_bot.send_message(
                    chat_id=order.telegram_chat_id,
                    text=texts(user.lang).ORDER_UNPAYED
                )
            except Exception as error:
                logger.error(f'Failed to send message to group: {error}')

        try:
            message_manager = await buyer_bot.send_message(
                chat_id=order.telegram_chat_id_manager,
                text=texts('ru').manager_chat_order_private(order)
            )
            await buyer_bot.send_message(
                chat_id=order.telegram_chat_id_manager,
                text=texts('ru').ORDER_UNPAYED
            )
            order.message_id_manager_group = message_manager.message_id
            await order.save()
        except Exception as error:
            logger.error(f'Unable to send message to manager`s group: {error}')

    await buyer_bot.send_message(
        chat_id=order.telegram_chat_id,
        text=texts(user.lang).MANAGER_JOINED_TO_CHAT
    )

    try:
        await controllers.send_message(
            chat_id=customer.id,
            text=texts(customer.language).manager_chat_order_private(order),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
    except Exception as error:
        logger.error(f'Unable to send message to manager: {error}')

    for _customer in order.message_id_direct.keys():
        if int(_customer) in roll_queue[order.id] and int(_customer) != customer.id:
            await bot.send_message(
                chat_id=_customer,
                text=texts(customer.language).MANAGER_LOST_ROLL
            )
        try:
            await bot.delete_message(
                chat_id=_customer,
                message_id=order.message_id_direct[_customer]
            )
        except Exception as e:
            logger.error(f'Error while deleting order message: {e}')

    if order.is_special:
        await buyer_bot.send_message(
            chat_id=order.user_id,
            text=texts(user.lang).YOUR_SPECIAL_ORDER_TAKEN
        )
        keyboard = [
            [buttons(user.lang).NewMenu()]
        ]
        await buyer_bot.send_message(
            chat_id=order.user_id,
            text=texts(user.lang).special_order_summary(order),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )

    buyer = await controllers.get_user(order.user_id)

    del roll_queue[order.id]

    text = texts('ru').admins_chat_order(order, buyer.telegram.username)

    text = f"""<b>Заказ был принят в работу @{customer.username}</b>

<s>{text}</s>"""

    keyboard = [[buttons('ru').RemoveOrderManager(order.id, str(customer.id))]]

    await controllers.update_google_sheets(order)

    try:
        await buyer_bot.edit_message_text(
            text=text,
            chat_id=config.TELEGRAM_ADMINS_CHAT_ID,
            message_id=order.admins_message_id,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    except:
        await buyer_bot.send_message(
            text=text,
            chat_id=config.TELEGRAM_ADMINS_CHAT_ID,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )


async def claim_order_decline():
    return


async def change_price_request(query: CallbackQuery, customer: Customer, context: FSMContext):
    telegram_chat_id = query.data.split(':')[1]

    order = await controllers.get_order_by_telegram_chat_id(int(telegram_chat_id))

    if order.id in roll_queue.keys() and roll_queue[order.id] == []:
        await bot.send_message(
            chat_id=customer.id,
            text=texts(customer.language).ALREADY_IN_QUEUE,
        )
        return

    await context.set_state(states.change_price)

    message = await bot.send_message(
        chat_id=customer.id,
        text=texts(customer.language).CHANGE_PRICE_REQUEST,
    )

    change_price_requests[customer.id] = [order.id, message.message_id]


async def new_price_handler(message: Message, customer: Customer, context: FSMContext):
    try:
        new_price = float(message.text)
    except Exception as error:
        await controllers.send_message(
            chat_id=customer.id,
            text=texts(customer.language).INVALID_INPUT,
        )
        return

    await context.set_state()

    await bot.send_message(
        chat_id=customer.id,
        text=texts(customer.language).SUCCESS_REQUEST,
    )

    await message.delete()

    await buyer_bot.send_message(
        chat_id=config.TELEGRAM_ADMINS_CHAT_ID,
        text=texts('ru').new_price_request(change_price_requests[customer.id][0], new_price, message.from_user.username)
    )

    await bot.delete_message(
        chat_id=customer.id,
        message_id=change_price_requests[customer.id][1],
    )


async def remove_self_from_order(query: CallbackQuery, customer: Customer):
    order_id, telegram_manager_id = query.data.split(':')[1:]

    order = await controllers.get_order(int(order_id), ignore_cache=True)

    buyer = await controllers.get_user(order.user_id)

    user_client = await controllers.get_user(order.user_id)

    order.status = 'Confirmed'
    order.manager = None
    await order.save()

    await buyer_bot.send_message(
        chat_id=order.telegram_chat_id,
        text=texts(user_client.lang).MANAGER_LEFT_CHAT
    )

    keyboard = [[buttons('ru').ChangePrice(order.telegram_chat_id)]]

    product = await controllers.get_product(order.order_items[0].product_id)

    short_text = texts(customer.language).manager_chat_order_short(order, product)

    try:
        await buyer_bot.ban_chat_member(
            chat_id=int(order.telegram_chat_id_manager),
            user_id=int(telegram_manager_id)
        )
    except Exception as error:
        logger.error(
            f'Unable to ban manager {order.manager}({telegram_manager_id}) from group {order_id}: {error}')

    message_short = await buyer_bot.send_message(
        chat_id=config.TELEGRAM_ADMINS_CHAT_ID,
        text=texts('ru').admins_chat_order(order, buyer.telegram.username),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )

    order.admins_message_id = message_short.message_id
    customers = await controllers.get_customers(min_sum=int(order.total_customer))

    for _customer in customers:
        try:
            keyboard = [[buttons(_customer.language).ClaimOrder(order.telegram_chat_id)],
                        [buttons(_customer.language).ChangePrice(order.telegram_chat_id)]]
            message_short = await bot.send_message(
                chat_id=_customer.id,
                text=short_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            )
            await bot.pin_chat_message(
                chat_id=_customer.id,
                message_id=message_short.message_id,
                disable_notification=True
            )
            order.message_id_direct[str(_customer.id)] = message_short.message_id
            await order.save()
        except Exception as e:
            logger.error(f'Error while resending order: {e}')
            continue

    await controllers.update_google_sheets(order)

    await query.message.delete()
