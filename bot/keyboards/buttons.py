from aiogram.types import InlineKeyboardButton
from bot import callbacks
from models import Category, Product, Order
from bot.types import ChainName, NavigationHistory, TokenName


class buttons:

    def __call__(self, lang: str):
        if lang == 'ru':
            return self.ru
        elif lang == 'en':
            return self.en
        # elif lang == 'uk':
        #     return self.uk
        return self.ru

    class ru:
        class InlineButton(InlineKeyboardButton):
            position: str = None

            def __call__(self, history: NavigationHistory = (), url: str = None) -> 'InlineButton':
                copy = self.model_copy()
                if history:
                    if self.callback_data:
                        history += (self.callback_data,)
                    copy.callback_data = callbacks.pack_history(history)
                elif url:
                    copy.url = url
                return copy

        def keyboard_from_buttons(buttons: list[InlineButton]) -> list[list[InlineButton]]:
            positional_buttons = []
            other_buttons = []
            for button in buttons:
                if getattr(button, 'position', None):
                    positional_buttons.append(button)
                else:
                    other_buttons.append(button)
            positional_buttons.sort(key=lambda x: x.position)

            keyboard = []
            for button in positional_buttons:
                button_row = int(button.position.split(':')[0])
                while len(keyboard) < button_row:
                    keyboard.append([])
                keyboard[button_row - 1].append(button)

            keyboard = (
                    [row for row in keyboard if len(row) != 0] +
                    [[button] for button in other_buttons]
            )
            return keyboard

        def organize_buttons(buttons: list):
            if len(buttons) % 2 == 0:
                return [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            return [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

        class MinimumOrderPrice(InlineButton):
            def __init__(self, min_price: int):
                super().__init__(text=f'Минимальная сумма ({min_price})',
                                 callback_data=f'{callbacks.MINIMUM_ORDER}')

        class SpecialOrders(InlineButton):
            def __init__(self, current_state: bool):
                state_text = "Да" if current_state else "Нет"
                super().__init__(text=f'Получать особенные заказы? ({state_text})',
                                 callback_data=f'{callbacks.SPECIAL_ORDERS}')

        class ApproveOrderClaim(InlineButton):
            def __init__(self, telegram_chat_id: str, telegram_message_id: str):
                super().__init__(text='Да✅',
                                 callback_data=f'{callbacks.APPROVE_ORDER_CLAIM}:{telegram_chat_id}:{telegram_message_id}')

        class DeclineOrderClaim(InlineButton):
            def __init__(self, telegram_chat_id: str, telegram_message_id: str):
                super().__init__(text='Нет❌',
                                 callback_data=f'{callbacks.DECLINE_ORDER_CLAIM}:{telegram_chat_id}:{telegram_message_id}')

        class RemoveOrderManager(InlineButton):
            def __init__(self, telegram_chat_id: str, telegram_manager_id: str):
                super().__init__(text='Снять менеджера⚠️',
                                 callback_data=f'{callbacks.REMOVE_ORDER_MANAGER}:{telegram_chat_id}:{telegram_manager_id}')

        class ClaimOrder(InlineButton):
            def __init__(self, telegram_chat_id: str):
                super().__init__(text='✅Взять заказ', callback_data=f'{callbacks.CLAIM_ORDER}:{telegram_chat_id}')

        class ChangePrice(InlineButton):
            def __init__(self, telegram_chat_id: int):
                super().__init__(text='🔄Смена цены', callback_data=f'{callbacks.CHANGE_PRICE}:{telegram_chat_id}')

        class WithdrawWallet(InlineButton):
            def __init__(self, is_set: bool):
                wallet_text = "Выставлен" if is_set else "Не выставлен"
                super().__init__(text=f'Кошелек ({wallet_text})',
                                 callback_data=callbacks.WITHDRAW_WALLET)

        class RemoveSelfOrder(InlineButton):
            def __init__(self, order_id: str, telegram_manager_id: str):
                super().__init__(text='Снять себя с заказа⚠️',
                                 callback_data=f'{callbacks.REMOVE_SELF_ORDER}:{order_id}:{telegram_manager_id}')

        MyOrders = InlineButton(text='Мои заказы', callback_data=callbacks.MY_ORDERS)
        Settings = InlineButton(text='Настройки', callback_data=callbacks.SETTINGS)
        OpenedOrders = InlineButton(text='Свободные заказы', callback_data=callbacks.OPENED_ORDERS)
        Support = InlineButton(text='Саппорт', url='https://t.me/rezerv_lim')
        Back = InlineButton(text='«назад')
        ChangeWallet = InlineButton(text='Изменить📗', callback_data=callbacks.CHANGE_WALLET)
        NewMenu = InlineButton(text='🍋 меню', callback_data=callbacks.NEW_MENU)

    class en:
        class InlineButton(InlineKeyboardButton):
            position: str = None

            def __call__(self, history: NavigationHistory = (), url: str = None) -> 'InlineButton':
                copy = self.model_copy()
                if history:
                    if self.callback_data:
                        history += (self.callback_data,)
                    copy.callback_data = callbacks.pack_history(history)
                elif url:
                    copy.url = url
                return copy

        def keyboard_from_buttons(buttons: list[InlineButton]) -> list[list[InlineButton]]:
            positional_buttons = []
            other_buttons = []
            for button in buttons:
                if getattr(button, 'position', None):
                    positional_buttons.append(button)
                else:
                    other_buttons.append(button)
            positional_buttons.sort(key=lambda x: x.position)

            keyboard = []
            for button in positional_buttons:
                button_row = int(button.position.split(':')[0])
                while len(keyboard) < button_row:
                    keyboard.append([])
                keyboard[button_row - 1].append(button)

            keyboard = (
                    [row for row in keyboard if len(row) != 0] +
                    [[button] for button in other_buttons]
            )
            return keyboard

        def organize_buttons(buttons: list):
            if len(buttons) % 2 == 0:
                return [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            return [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

        class MinimumOrderPrice(InlineButton):
            def __init__(self, min_price: int):
                super().__init__(text=f'Minimun sum ({min_price})',
                                 callback_data=f'{callbacks.MINIMUM_ORDER}')

        class SpecialOrders(InlineButton):
            def __init__(self, current_state: bool):
                state_text = "Yes" if current_state else "No"
                super().__init__(text=f'Receive special orders? ({state_text})',
                                 callback_data=f'{callbacks.SPECIAL_ORDERS}')

        class ApproveOrderClaim(InlineButton):
            def __init__(self, telegram_chat_id: str, telegram_message_id: str):
                super().__init__(text='Yes✅',
                                 callback_data=f'{callbacks.APPROVE_ORDER_CLAIM}:{telegram_chat_id}:{telegram_message_id}')

        class DeclineOrderClaim(InlineButton):
            def __init__(self, telegram_chat_id: str, telegram_message_id: str):
                super().__init__(text='No❌',
                                 callback_data=f'{callbacks.DECLINE_ORDER_CLAIM}:{telegram_chat_id}:{telegram_message_id}')

        class RemoveOrderManager(InlineButton):
            def __init__(self, telegram_chat_id: str, telegram_manager_id: str):
                super().__init__(text='Remove manager⚠️',
                                 callback_data=f'{callbacks.REMOVE_ORDER_MANAGER}:{telegram_chat_id}:{telegram_manager_id}')

        class RemoveSelfOrder(InlineButton):
            def __init__(self, telegram_chat_id: str, telegram_manager_id: str):
                super().__init__(text='Remove yourself from the order⚠️',
                                 callback_data=f'{callbacks.REMOVE_SELF_ORDER}:{telegram_chat_id}:{telegram_manager_id}')

        class ClaimOrder(InlineButton):
            def __init__(self, telegram_chat_id: str):
                super().__init__(text='✅Take order', callback_data=f'{callbacks.CLAIM_ORDER}:{telegram_chat_id}')

        class ChangePriceRequest(InlineButton):
            def __init__(self, telegram_chat_id: int):
                super().__init__(text='🔄Change price',
                                 callback_data=f'{callbacks.CHANGE_PRICE_REQUEST}:{telegram_chat_id}')

        class WithdrawWallet(InlineButton):
            def __init__(self, is_set: bool):
                wallet_text = "Filled" if is_set else "Unfilled"
                super().__init__(text=f'Wallet ({wallet_text})',
                                 callback_data=callbacks.WITHDRAW_WALLET)

        MyOrders = InlineButton(text='My orders', callback_data=callbacks.MY_ORDERS)
        Settings = InlineButton(text='Settings', callback_data=callbacks.SETTINGS)
        OpenedOrders = InlineButton(text='Opened orders', callback_data=callbacks.OPENED_ORDERS)
        Support = InlineButton(text='Support', url='https://t.me/rezerv_lim')
        Back = InlineButton(text='«back')
        ChangeWallet = InlineButton(text='Change📗', callback_data=callbacks.CHANGE_WALLET)
        NewMenu = InlineButton(text='🍋 menu', callback_data=callbacks.NEW_MENU)
