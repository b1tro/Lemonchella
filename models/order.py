import datetime
from typing import Literal, Optional
from .base import TimestampedDocument
from .payment import BalancePayment, CryptoTransaction
from pydantic import BaseModel, Field, conlist
from beanie import DecimalAnnotation


class OrderItem(BaseModel):
    product_id: int
    """int, Unique identifier of ordered product."""
    quantity: int = Field(gt=0)
    """int, Quantity of this products, Must be greater than 0."""
    product_name: Optional[str] = None
    """int, Name of ordered product."""
    delivered_copies: Optional[conlist(str, min_length=1)] = None
    """delivered copies of product"""
    delivered_quantity: Optional[int] = None
    """delivered quantity of product"""
    deadline: Optional[datetime.datetime] = None
    """deadline of order"""

    def __str__(self) -> str:
        product = self.product_name if self.product_name else f'Product(id={self.product_id})'
        return f"({product}, quantity={self.quantity})"


class CachedOrder(BaseModel):
    """Cached order model."""

    order_items: list[OrderItem] = []
    """List of bought items."""
    total: DecimalAnnotation = Field(gt=0)
    """Total price of the order."""
    total_customer: DecimalAnnotation = Field(gt=0)
    """Total price of the order."""
    payment: Optional[CryptoTransaction] = None
    """Order payment."""
    balance_payment: Optional[BalancePayment] = None
    """Order payment."""

    @property
    def remaining_amount(self):
        rest = self.total
        if self.balance_payment:
            rest -= self.balance_payment.amount
        return rest


class Order(TimestampedDocument):
    """Order document."""

    id: int
    """Order unique identifier."""
    user_id: int
    """User id of the buyer."""
    order_items: conlist(OrderItem, min_length=1)
    """List of bought items."""
    total: DecimalAnnotation = Field(gt=0)
    """Total price of the order."""
    total_customer: Optional[DecimalAnnotation] = None
    """Total price of the order."""
    manager: Optional[int | str] = None
    """Manager of the order."""
    payment: Optional[CryptoTransaction] = None
    """order payment."""
    balance_payment: Optional[BalancePayment] = None
    """order payment from user balance."""
    status: Literal['Confirmed', 'Pending', 'Taken', 'Completed', 'UserDeleted', 'CustomerDeleted', 'Deleted'] = 'Pending'
    """Order status."""
    telegram_chat_link: Optional[str] = ''
    """Link to telegram group of the order."""
    telegram_chat_id: Optional[int] = None
    """Id of telegram group of the order."""
    telegram_chat_link_manager: Optional[str] = ''
    """Link to telegram group of the order."""
    telegram_chat_id_manager: Optional[int] = None
    """Id of telegram group of the order."""
    message_id_direct: Optional[dict] = {}
    """id for message in manager group"""
    referrer_id: Optional[int] = None
    """Id of referrer"""
    addon_answers: Optional[list] = []
    """Answers for addons"""
    message_id_manager_group: Optional[int] = -1
    """id for message in manager group"""
    is_special: Optional[bool] = False
    """Order is special"""
    complete_status: Optional[str] = ''
    """Status of completing order"""
    total_summary: Optional[float] = 0
    total_balance_summary: Optional[float] = 0
    total_customer_summary: Optional[float] = 0

    referral_amount: Optional[DecimalAnnotation] = None

    added_to_sheet: Optional[bool] = False
    """bool, has order row benn added to orders google sheet."""

    answers: Optional[dict] = {}
    """dict, answers to manager questions"""

    order_sheet_url: Optional[str] = None
    """str, url of spreadsheet with information about order"""

    deadline: Optional[datetime.datetime] = None
    """datetime, deadline for order"""

    admins_message_id: Optional[int] = None
    """int, message_id of group message"""

    sent_messages: Optional[list[int]] = []
    """list, list of all ids of send messages"""

    class Settings:
        name = "orders"

    @property
    def whole_quantity(self):
        return sum([order_item.quantity for order_item in self.order_items])

    @property
    def delivered_quantity(self):
        return sum([
            order_item.delivered_quantity
            for order_item in self.order_items
            if order_item.delivered_quantity
        ])

    @property
    def pid(self):
        """pretty small id"""
        return int(str(self.id).zfill(6)[:6])
