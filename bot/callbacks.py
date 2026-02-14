from typing import Iterable


def unpack_history(callback_data: str) -> tuple[str]:
    return tuple(callback_data.split('/'))


def pack_history(history: Iterable[str]) -> str:
    return '/'.join(history)


MY_ORDERS = "MO"
SETTINGS = "S"
OPENED_ORDERS = "OO"

MINIMUM_ORDER = "MnO"
SPECIAL_ORDERS = "SO"

WITHDRAW_WALLET = "WW"

MENU = 'Menu'
NEW_MENU = 'Menun'
CHANGE_WALLET = "CW"
APPROVE_ORDER_CLAIM = 'A_CO'
DECLINE_ORDER_CLAIM = 'D_CO'
CLAIM_ORDER = 'CO'
CHANGE_PRICE_REQUEST = "CPR"
REMOVE_ORDER_MANAGER = 'ROM'
CHANGE_PRICE = "CP"
REMOVE_SELF_ORDER = "RSO"


COMPLETE_FAILED = "CFail"
COMPLETE_PART = "CPart"
COMPLETE_FULL = "CFull"