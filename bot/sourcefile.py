import config
from models import HotConfig, Order, Product, User, UserCache
from bot.bot import Bot
from decimal import Decimal


def popup_type(popup_id: str):
    return {'1': 'balance', '2': 'referral balance'}[popup_id]


def popup_type_ru(popup_id: str):
    return {'1': 'основной баланс', '2': 'реферальный баланс'}[popup_id]


def popup_type_en(popup_id: str):
    return {'1': 'main balance', '2': 'referral balance'}[popup_id]


def popup_type_uk(popup_id: str):
    return {'1': 'основний баланс', '2': 'реферальний баланс'}[popup_id]


class links:
    RULES = "https://teletype.in/@dim1562/Bot_guide"
    GUIDES = "https://t.me/Multi_farmer"
    FILTRATION = "google.com"
    MIN_SUM = "google.com"
    FIND_ORDER = "https://teletype.in/@dim1562/Bot_guide#iDv7"


class pictures:
    WELCOME = ""
    CATALOG = "https://ibb.co/5698bsZ"
    PARTNER = "https://ibb.co/xC2nGZ5"


class texts:
    class ru:
        YOU_WERE_BLOCKED = """Вы были заблокированы."""
        CANT_FIND_CUSTOMER = f"<b>К сожалению, вы не были добавлены администратором\n\nПожалуйста, отпишите - @Dim1253</b>"
        WELCOME = f"<b>Добро пожаловать! Я Лемон, и это мой бот с возможностью для заработка на продаже KYC❤️\n\nПравила - <a href=\'{links.RULES}\'>линк</a>\nГайды - <a href=\'{links.GUIDES}\'>линк</a></b>"
        SETTINGS = f"<b>Этот раздел предназначен для <a href=\'{links.FILTRATION}\'>фильтрации</a> ордеров</b>"
        INVALID_INPUT = "<b>⛔️Попробуйте еще раз</b>"
        SEND_WALLET = "<b>Напишите USDT bep20👇</b>"
        SUCCESS_WALLET = "<b>Ваш адрес успешно сохранен</b>"
        SEND_SUM = f"<b>Введите минимальную сумму заказа (<a href='{links.MIN_SUM}'>объяснение</a>)</b>"
        ORDER_ALREADY_TAKEN = "⚠️ Этот заказ уже взял другой менеджер"
        MANAGER_JOINED_TO_CHAT = "<b>Исполнитель принял заказ и зашел в группу🤖</b>"
        MANAGER_LEFT_CHAT = "<b>Исполнитель вышел из заказа🤖</b>"
        CHANGE_PRICE_REQUEST = "<b>🔄Напишите новую цену на заказ</b>"
        SUCCESS_REQUEST = "<b>Ваш запрос был успешно отправлен менеджерам✅</b>"
        SUCCESS_ORDER_REQUEST = "Заявка на заказ была отправлена."
        ALREADY_ORDER_REQUEST = "Вы уже записаны в заявку."
        MANAGER_LOST_ROLL = "<b>❗️К сожалению, на заказ был выбран другой исполнитель</b>"
        INVALID_WALLET = "Для корректной работы нужно заполнить кошелек в настройках."
        ALREADY_IN_QUEUE = "<b>На данный заказ уже подали заявку</b>"
        YOUR_SPECIAL_ORDER_TAKEN = "<b>Ваш заказ принял исполнитель👇</b>"
        ORDER_UNPAYED = "<b>ЗАКАЗ НЕ ОПЛАЧЕН❗️\n\nОбговорите условия сделки, если обе стороны устраивают все условия, то покупатель может написать /menu и создать безопасную сделку</b>"

        def manager_chat_order_private(order: Order):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price_customer) == str and price_customer.startswith('skip'):
                    price_customer = Decimal(price_customer.split(':')[1])
                else:
                    price_customer = Decimal(price_customer)
                addons += f'<b>{question}:</b> {answer} ({price_customer:+}$/аккаунт)\n'

            text = f"""{f"<b>❗️Новый заказ #{order.pid}</b>" if not order.is_special else f"<b>📕️Новый ОСОБЕННЫЙ заказ #{order.pid}</b>"}

<b>Товар:</b> {order.order_items[0].product_name}
<b>Цена</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кол-во:</b> {order.order_items[0].quantity} шт.
{f"<b>Оплачено:</b> {order.total_customer} $USDT" if not order.is_special else f"<b>Сумма:</b> {order.total_customer} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>"}

<b>Ссылка на чат:</b> {order.telegram_chat_link_manager}

{addons}
<b>Дедлайн заказа:</b> {order.deadline}

{f'<b>📗 Ссылка на google sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""

            return text

        def manager_wait(config: HotConfig):
            return f"""<b>Здравствуйте, в ближайшее время в группу присоединится исполнитель и выполнит ваш заказ🖐</b>

<i>Пожалуйста не используйте ответы на сообщения/эмодзи, а так же эта группа автоматически удалится через 60 дней❗</i>️

<i>/menu - доп функции </i><b>(вызов саппорта, гайды)</b>

<b>Если у вас есть вопросы - отпишите (@{config.MANAGER_USERNAME})</b>"""

        def manager_chat_order(order: Order, referrer: User = None, username: str = None):
            if referrer is not None:
                ref_text = f'{referrer.id} (@{referrer.telegram.username if referrer.telegram is not None else None})'
            else:
                ref_text = 'None'

            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/аккаунт)\n'

            text = f"""{f"<b>❗️Новый заказ #{order.pid}</b>" if not order.is_special else f"<b>📕️Новый ОСОБЕННЫЙ заказ #{order.pid}</b>"}

<b>Товар:</b> {order.order_items[0].product_name}
<b>Цена</b>: {round(order.total / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кол-во:</b> {order.order_items[0].quantity} шт.
<b>Скидка:</b> {order.balance_payment.amount if order.balance_payment != None else 0}$
{f"<b>Оплачено:</b> {order.total} $USDT" if not order.is_special else f"<b>Сумма:</b> {order.total} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>"}

<b>ID покупателя:</b> {order.user_id}
<b>@ покупателя:</b> @{username}
<b>Ссылка на чат:</b> {order.telegram_chat_link}
<b>Транзакция</b>: {order.payment.transaction_link if order.payment is not None else None}
<b>Реферер:</b> {ref_text}

{addons}
<b>Дедлайн заказа:</b> {order.deadline}

{f'<b>📗 Ссылка на google sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""
            return text

        def special_order_summary(order: Order):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/аккаунт)\n'

            text = f"""<b>📕️Новый ОСОБЕННЫЙ заказ #{order.pid}</b>

<b>Товар:</b> {order.order_items[0].product_name}
<b>Цена</b>: {round(order.total / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кол-во:</b> {order.order_items[0].quantity} шт.
<b>Скидка:</b> {order.balance_payment.amount if order.balance_payment != None else 0}$
<b>Сумма:</b> {order.total} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>

<b>Ссылка на чат:</b> {order.telegram_chat_link}

{addons}
<b>Дедлайн заказа:</b> {order.deadline}

{f'<b>📗 Ссылка на google sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""
            return text

        def withdraw_wallet(wallet: str):
            return f"""Ваш кошелек USDT (bep 20):\n\n<pre>{wallet if wallet != '' else '-'}</pre>"""

        def approve_order_claim(order_id: str):
            return f"Вы уверены, что готовы взять #{order_id} заказ?"

        def manager_chat_order_private(order: Order):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price_customer) == str and price_customer.startswith('skip'):
                    price_customer = Decimal(price_customer.split(':')[1])
                else:
                    price_customer = Decimal(price_customer)
                addons += f'<b>{question}:</b> {answer} ({price_customer:+}$/аккаунт)\n'

            text = f"""{f"<b>❗️Новый заказ #{order.pid}</b>" if not order.is_special else f"<b>📕️Новый ОСОБЕННЫЙ ЗАКАЗ #{order.pid}</b>"}

<b>Товар:</b> {order.order_items[0].product_name}
<b>Цена</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кол-во:</b> {order.order_items[0].quantity} шт.
{f"<b>Оплачено:</b> {order.total_customer} $USDT" if not order.is_special else f"<b>Сумма:</b> {order.total_customer} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>"}

<b>Ссылка на чат:</b> {order.telegram_chat_link_manager}

{addons}
<b>Дедлайн заказа:</b> {order.deadline}

{f'<b>📗 Ссылка на google sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""

            return text

        def manager_chat_order_short(order: Order, product: Product):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price_customer) == str and price_customer.startswith('skip'):
                    price_customer = Decimal(price_customer.split(':')[1])
                else:
                    price_customer = Decimal(price_customer)
                addons += f'<b>{question}:</b> {answer} ({price_customer:+}$/аккаунт)\n'

            text = f"""{f"<b>❗️Новый заказ #{order.pid}</b>" if not order.is_special else f"<b>📕️Новый ОСОБЕННЫЙ ЗАКАЗ #{order.pid}</b>"}

<b>Товар:</b> {order.order_items[0].product_name}
<b>Цена</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кол-во:</b> {order.order_items[0].quantity} шт.
{f"<b>Оплачено:</b> {order.total_customer} $USDT" if not order.is_special else f"<b>Сумма:</b> {order.total_customer} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>"}

{addons}
<b>Дедлайн заказа:</b> {order.deadline}"""

            return text

        def new_price_request(order_id: int, new_price: float, customer_username: str):
            return f"<b>#{order_id}\n\n@{customer_username}\nГотов взять заказ за {new_price}$</b>"

        def generate_opened_orders(orders: list[Order], customer_id: int):
            if len(orders) == 0:
                return "<b>На данный момент нету актуальных заказов📒</b>"
            text = "Актуальные заказы:\n\n"

            for order in orders:
                text += f'- {order.order_items[0].quantity}шт {order.order_items[0].product_name} - {order.total_customer}$\n'

            return '<b>' + text + f'\n\nКак найти нужный заказ - <a href=\'{links.FIND_ORDER}\'>Гайд</a></b>'

        def admins_chat_order(order: Order, username: str = None):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/аккаунт)\n'

            text = f"""{f"<b>❗️Новый заказ #{order.pid}</b>" if not order.is_special else f"<b>📕️Новый ОСОБЕННЫЙ ЗАКАЗ #{order.pid}</b>"}

<b>Товар:</b> {order.order_items[0].product_name}
<b>Цена</b>: {round(order.total / order.order_items[0].quantity, 2)}$/аккаунт
<b>Цена исполнителя</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кол-во:</b> {order.order_items[0].quantity} шт.
<b>Скидка:</b> {order.balance_payment.amount if order.balance_payment != None else 0}$
{f"<b>Оплачено:</b> {order.total} $USDT" if not order.is_special else f"<b>Сумма:</b> {order.total} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>"}

<b>ID покупателя:</b> {order.user_id}
<b>@ покупателя:</b> @{username}
<b>Ссылка на чат покупателя:</b> {order.telegram_chat_link}
<b>Ссылка на чат исполнителя:</b> {order.telegram_chat_link_manager}
<b>Транзакция</b>: {order.payment.transaction_link if order.payment is not None else None}

{addons}
<b>Дедлайн заказа:</b> {order.deadline}

{f'<b>📗 Ссылка на google sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""
            return text

    class en:
        YOU_WERE_BLOCKED = """You were blocked."""
        CANT_FIND_CUSTOMER = f"<b>Unfortunately, you have not been added by the administrator\n\nPlease write to - @Dim1253</b>"
        WELCOME = f"<b>Welcome! I'm Lemon and this is my bot with the ability to earn money by selling KYC❤️\n\nRules - <a href=\"{links.RULES}\">link</a>\nGuides - <a href=\"{links.GUIDES}\">link</a></b>"
        SETTINGS = f"<b>This section is intended for <a href=\'{links.FILTRATION}\'>filtering</a> orders</b>"
        INVALID_INPUT = "<b>⛔️Try again</b>"
        SEND_WALLET = "<b>Send USDT bep20👇</b>"
        SUCCESS_WALLET = "<b>Your address has been saved successfully</b>"
        SEND_SUM = f"<b>Send minimum order sum (<a href='{links.MIN_SUM}'>description</a>)</b>"
        ORDER_ALREADY_TAKEN = "<b>⚠️ This order has already been taken by another manager</b>"
        MANAGER_JOINED_TO_CHAT = "<b>The performer accepted the order and joined the group🤖</b>"
        MANAGER_LEFT_CHAT = "<b>The performer has left the order🤖</b>"
        CHANGE_PRICE_REQUEST = "<b>🔄Write a new price for the order</b>"
        SUCCESS_REQUEST = "<b>Your request has been successfully sent to managers✅</b>"
        SUCCESS_ORDER_REQUEST = "The order request has been sent."
        ALREADY_ORDER_REQUEST = "You are already registered in the order roll."
        MANAGER_LOST_ROLL = "<b>❗️Unfortunately, another contractor was selected for the order.</b>"
        INVALID_WALLET = "For correct work, you need to fill in the wallet in the settings."
        ALREADY_IN_QUEUE = "<b>This order has already been applied for.</b>"
        YOUR_SPECIAL_ORDER_TAKEN = "<b>Your order has been accepted by the performer👇</b>"
        ORDER_UNPAYED = "<b>ORDER NOT PAID❗️\n\nDiscuss the terms of the deal, if both parties are satisfied with all the conditions, then the buyer can write /menu and create a secure deal</b>"

        def manager_wait(config: HotConfig):
            return f"""<b>Hello, a worker will join the group soon and will complete your order🖐</b>

<i>Please do not use message replies/emoji and also this group will be automatically deleted after 60 days❗️</i>

<i>/menu - additional functions</i><b>(call support, guides)</b>

<b>If you have any questions, write - (@{config.MANAGER_USERNAME})</b>"""

        def manager_chat_order(order: Order, referrer: User = None, username: str = None):
            if referrer is not None:
                ref_text = f'{referrer.id} (@{referrer.telegram.username if referrer.telegram is not None else None})'
            else:
                ref_text = 'None'

            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/account)\n'

            text = f"""{f"<b>❗️New order #{order.pid}</b>" if not order.is_special else f"<b>📕️New special order #{order.pid}</b>"}

<b>Product:</b> {order.order_items[0].product_name}
<b>Price</b>: {round(order.total / order.order_items[0].quantity, 2)}$/account
<b>Qty:</b> {order.order_items[0].quantity} pcs.
<b>Discount:</b> {order.balance_payment.amount if order.balance_payment != None else 0}$
{f"<b>Paid:</b> {order.total} $USDT" if not order.is_special else f"<b>Total:</b> {order.total} $USDT <b>(NO PAY❗)</b>"}

<b>ID buyer:</b> {order.user_id}
<b>@ buyer:</b> @{username}
<b>Chat link:</b> {order.telegram_chat_link}
<b>Transaction</b>: {order.payment.transaction_link if order.payment is not None else None}
<b>Referrer:</b> {ref_text}

{addons}
<b>Order deadline:</b> {order.deadline}

{f'<b>📗 Link on google sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""
            return text

        def special_order_summary(order: Order):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/аккаунт)\n'

            text = f"""<b>📕️New SPECIAL order #{order.pid}</b>

<b>Product:</b> {order.order_items[0].product_name}
<b>Price</b>: {round(order.total / order.order_items[0].quantity, 2)}$/account
<b>Quantity:</b> {order.order_items[0].quantity} pcs.
<b>Discount:</b> {order.balance_payment.amount if order.balance_payment != None else 0}$
<b>Paid:</b> {order.total} $USDT <b>(NOT PAID❗)</b>

<b>Chat link:</b> {order.telegram_chat_link}

{addons}
<b>Order deadline:</b> {order.deadline}

{f'<b>📗 Google sheets link:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""
            return text

        def withdraw_wallet(wallet: str):
            return f"""Your wallet USDT (bep 20):\n\n<pre>{wallet if wallet != '' else '-'}</pre>"""

        def approve_order_claim(order_id: str):
            return f"Are you sure you are ready to take order #{order_id}?"

        def manager_chat_order_private(order: Order):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price_customer) == str and price_customer.startswith('skip'):
                    price_customer = Decimal(price_customer.split(':')[1])
                else:
                    price_customer = Decimal(price_customer)
                addons += f'<b>{question}:</b> {answer} ({price_customer:+}$/account)\n'

            text = f"""{f"<b>❗️New order #{order.pid}</b>" if not order.is_special else f"<b>📕️New SPECIAL order #{order.pid}</b>"}

<b>Product:</b> {order.order_items[0].product_name}
<b>Price</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/account
<b>Qty:</b> {order.order_items[0].quantity} pcs.
<b>Paid:</b> {order.total_customer} $USDT {"" if not order.is_special else f"<b>(NO PAY❗)</b>"}

<b>ID buyer:</b> {order.user_id}
<b>Chat link</b> {order.telegram_chat_link_manager}

{addons}
<b>Order deadline:</b> {order.deadline}

{f'<b>📗 Link on google sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""

            return text

        def manager_chat_order_short(order: Order, product: Product):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price_customer) == str and price_customer.startswith('skip'):
                    price_customer = Decimal(price_customer.split(':')[1])
                else:
                    price_customer = Decimal(price_customer)
                addons += f'<b>{question}:</b> {answer} ({price_customer:+}$/account)\n'

            text = f"""{f"<b>❗️New order #{order.pid}</b>" if not order.is_special else f"<b>📕️New SPECIAL order #{order.pid}</b>"}

<b>Product:</b> {order.order_items[0].product_name}
<b>Price</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/account
<b>Qty:</b> {order.order_items[0].quantity} pcs.
<b>Paid:</b> {order.total_customer} $USDT {"" if not order.is_special else f"<b>(NO PAY❗)</b>"}

{addons}
<b>Order deadline:</b> {order.deadline}"""

            return text

        def generate_opened_orders(orders: list[Order], customer_id: int):
            if len(orders) == 0:
                return "<b>There are currently no current orders📒</b>"
            text = "Available orders:\n\n"

            for order in orders:
                text += f'- {order.order_items[0].quantity}шт {order.order_items[0].product_name} - {order.total_customer}$\n'

            return '<b>' + text + f'\n\nHow to find order - <a href=\'{links.FIND_ORDER}\'>Guide</a></b>'

    class uk:
        YOU_WERE_BLOCKED = """Вас заблоковано."""
        CANT_FIND_CUSTOMER = f"<b>На жаль, вас не додав адміністратор\n\nБудь ласка, напишіть - @Dim1253</b>"
        WELCOME = f"<b>Ласкаво просимо! Я Лемон, і це мій бот із можливістю заробітку на продажі KYC❤️\n\nПравила - <a href='{links.RULES}'>лінк</a>\nГайди - <a href='{links.GUIDES}'>лінк</a></b>"
        SETTINGS = f"<b>Цей розділ призначений для <a href='{links.FILTRATION}'>фільтрації</a> замовлень</b>"
        INVALID_INPUT = "<b>⛔️ Спробуйте ще раз</b>"
        SEND_WALLET = "<b>Введіть адресу гаманця USDT BEP20 👇</b>"
        SUCCESS_WALLET = "<b>Вашу адресу успішно збережено</b>"
        SEND_SUM = f"<b>Введіть мінімальну суму замовлення (<a href='{links.MIN_SUM}'>пояснення</a>)</b>"
        ORDER_ALREADY_TAKEN = "⚠️ Це замовлення вже взяв інший менеджер"
        MANAGER_JOINED_TO_CHAT = "<b>Виконавець прийняв замовлення і приєднався до групи🤖</b>"
        MANAGER_LEFT_CHAT = "<b>Виконавець вийшов з замовлення🤖</b>"
        CHANGE_PRICE_REQUEST = "<b>🔄 Введіть нову ціну для замовлення</b>"
        SUCCESS_REQUEST = "<b>Ваш запит успішно надіслано менеджерам✅</b>"
        SUCCESS_ORDER_REQUEST = "Заявка на замовлення відправлена."
        ALREADY_ORDER_REQUEST = "Ви вже подали заявку."
        MANAGER_LOST_ROLL = "<b>❗️На жаль, для замовлення було обрано іншого виконавця</b>"
        INVALID_WALLET = "Для коректної роботи потрібно вказати гаманець у налаштуваннях."
        ALREADY_IN_QUEUE = "<b>На це замовлення вже подано заявку</b>"
        YOUR_SPECIAL_ORDER_TAKEN = "<b>Ваше спеціальне замовлення прийняв виконавець👇</b>"
        ORDER_UNPAYED = "<b>ЗАМОВЛЕННЯ НЕ ОПЛАЧЕНО❗\n\nОбговоріть умови угоди, якщо обидві сторони задоволені, покупець може написати /menu і створити безпечну угоду</b>"

        def manager_chat_order_private(order: Order):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price_customer) == str and price_customer.startswith('skip'):
                    price_customer = Decimal(price_customer.split(':')[1])
                else:
                    price_customer = Decimal(price_customer)
                addons += f'<b>{question}:</b> {answer} ({price_customer:+}$/аккаунт)\n'

            text = f"""{f'<b>❗️Нове замовлення #{order.pid}</b>' if not order.is_special else f'<b>📕️Нове СПЕЦІАЛЬНЕ замовлення #{order.pid}</b>'}\n
<b>Товар:</b> {order.order_items[0].product_name}
<b>Ціна</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кількість:</b> {order.order_items[0].quantity} шт.
{f'<b>Оплачено:</b> {order.total_customer} $USDT' if not order.is_special else f'<b>Сума:</b> {order.total_customer} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>'}\n
<b>Посилання на чат:</b> {order.telegram_chat_link_manager}

{addons}
<b>Дедлайн замовлення:</b> {order.deadline}

{f'<b>📗 Посилання на Google Sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""

            return text

        def manager_wait(config: HotConfig):
            return f"""<b>Вітаємо, найближчим часом до групи приєднається виконавець і виконає ваше замовлення🖐</b>\n
<i>Будь ласка, не використовуйте відповіді на повідомлення/емодзі, також ця група автоматично видалиться через 60 днів❗</i>️\n
<i>/menu - додаткові функції </i><b>(зв'язок із сапортом, гайди)</b>\n
<b>Якщо у вас є питання - напишіть (@{config.MANAGER_USERNAME})</b>"""

        def manager_chat_order(order: Order, referrer: User = None, username: str = None):
            if referrer is not None:
                ref_text = f'{referrer.id} (@{referrer.telegram.username if referrer.telegram is not None else None})'
            else:
                ref_text = 'None'

            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/аккаунт)\n'

            text = f"""{f'<b>❗️Нове замовлення #{order.pid}</b>' if not order.is_special else f'<b>📕️Нове СПЕЦІАЛЬНЕ замовлення #{order.pid}</b>'}\n
<b>Товар:</b> {order.order_items[0].product_name}
<b>Ціна</b>: {round(order.total / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кількість:</b> {order.order_items[0].quantity} шт.
<b>Знижка:</b> {order.balance_payment.amount if order.balance_payment is not None else 0}$
{f'<b>Оплачено:</b> {order.total} $USDT' if not order.is_special else f'<b>Сума:</b> {order.total} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>'}\n
<b>ID покупця:</b> {order.user_id}
<b>@ покупця:</b> @{username}
<b>Посилання на чат:</b> {order.telegram_chat_link}
<b>Транзакція</b>: {order.payment.transaction_link if order.payment is not None else None}
<b>Реферер:</b> {ref_text}

{addons}
<b>Дедлайн замовлення:</b> {order.deadline}

{f'<b>📗 Посилання на Google Sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""

            return text

        def special_order_summary(order: Order):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/аккаунт)\n'

            text = f"""<b>📕️Нове СПЕЦІАЛЬНЕ замовлення #{order.pid}</b>\n
<b>Товар:</b> {order.order_items[0].product_name}
<b>Ціна</b>: {round(order.total / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кількість:</b> {order.order_items[0].quantity} шт.
<b>Знижка:</b> {order.balance_payment.amount if order.balance_payment is not None else 0}$
<b>Сума:</b> {order.total} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>\n
<b>Посилання на чат:</b> {order.telegram_chat_link}

{addons}
<b>Дедлайн замовлення:</b> {order.deadline}

{f'<b>📗 Посилання на Google Sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""

            return text

        def withdraw_wallet(wallet: str):
            return f"Ваш гаманець USDT (BEP20):\n\n<pre>{wallet if wallet != '' else '-'}</pre>"

        def approve_order_claim(order_id: str):
            return f"Ви впевнені, що готові взяти замовлення #{order_id}?"

        def manager_chat_order_short(order: Order, product: Product):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price_customer) == str and price_customer.startswith('skip'):
                    price_customer = Decimal(price_customer.split(':')[1])
                else:
                    price_customer = Decimal(price_customer)
                addons += f'<b>{question}:</b> {answer} ({price_customer:+}$/аккаунт)\n'

            text = f"""{f'<b>❗️Нове замовлення #{order.pid}</b>' if not order.is_special else f'<b>📕️Нове СПЕЦІАЛЬНЕ замовлення #{order.pid}</b>'}\n
<b>Товар:</b> {order.order_items[0].product_name}
<b>Ціна</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кількість:</b> {order.order_items[0].quantity} шт.
{f'<b>Оплачено:</b> {order.total_customer} $USDT' if not order.is_special else f'<b>Сума:</b> {order.total_customer} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>'}

{addons}
<b>Дедлайн замовлення:</b> {order.deadline}"""

            return text

        def new_price_request(order_id: int, new_price: float, customer_username: str):
            return f"<b>#{order_id}\n\n@{customer_username}\nГотовий взяти замовлення за {new_price}$</b>"

        def generate_opened_orders(orders: list[Order], customer_id: int):
            if len(orders) == 0:
                return "<b>Наразі немає актуальних замовлень📒</b>"
            text = "Актуальні замовлення:\n\n"

            for order in orders:
                text += f'- {order.order_items[0].quantity}шт {order.order_items[0].product_name} - {order.total_customer}$\n'

            return '<b>' + text + f'\n\nЯк знайти потрібне замовлення - <a href=\'{links.FIND_ORDER}\'>Гайд</a></b>'

        def admins_chat_order(order: Order, username: str = None):
            addons = ''

            for question, answer, price, price_customer in order.addon_answers:
                if type(price) == str and price.startswith('skip'):
                    price = Decimal(price.split(':')[1])
                else:
                    price = Decimal(price)
                addons += f'<b>{question}:</b> {answer} ({price:+}$/аккаунт)\n'

            text = f"""{f'<b>❗️Нове замовлення #{order.pid}</b>' if not order.is_special else f'<b>📕️Нове СПЕЦІАЛЬНЕ замовлення #{order.pid}</b>'}\n
<b>Товар:</b> {order.order_items[0].product_name}
<b>Ціна</b>: {round(order.total / order.order_items[0].quantity, 2)}$/аккаунт
<b>Ціна виконавця</b>: {round(order.total_customer / order.order_items[0].quantity, 2)}$/аккаунт
<b>Кількість:</b> {order.order_items[0].quantity} шт.
<b>Знижка:</b> {order.balance_payment.amount if order.balance_payment != None else 0}$
{f'<b>Оплачено:</b> {order.total} $USDT' if not order.is_special else f'<b>Сума:</b> {order.total} $USDT <b>(НЕ ОПЛАЧЕНО❗)</b>'}\n
<b>ID покупця:</b> {order.user_id}
<b>@ покупця:</b> @{username}
<b>Посилання на чат покупця:</b> {order.telegram_chat_link}
<b>Посилання на чат виконавця:</b> {order.telegram_chat_link_manager}
<b>Транзакція</b>: {order.payment.transaction_link if order.payment is not None else None}

{addons}
<b>Дедлайн замовлення:</b> {order.deadline}

{f'<b>📗 Посилання на Google Sheets:</b> {order.order_sheet_url}' if order.order_sheet_url else ''}"""

            return text

    def __call__(self, lang: str):
        if lang == 'ru':
            return self.ru
        elif lang == 'en':
            return self.en
        elif lang == 'uk':
            return self.uk
        return self.en
