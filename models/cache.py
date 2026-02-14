from typing import Optional
from pydantic import BaseModel, Field
from .order import CachedOrder
from bot.types import NavigationHistory
from aiogram.types import Message


class UserCache(BaseModel):
    """Cached data for user."""

    cached_order: Optional[CachedOrder] = None
    """Currently processing user's order."""
    cached_product_id: Optional[int] = Field(None, ge=1)
    """Currently selected product identifier."""
    cached_payment_token: Optional[str] = None
    """Currently selected payment token."""
    last_message_id: Optional[int] = Field(None, ge=1)
    """Last message, to be beleted on new message."""
    history: Optional[NavigationHistory] = None
    """Callbacks history of user."""
    question_answers: Optional[dict] = {}
    """Answers to questions in dict."""
    spam_destination: Optional[list] = []
    """List of all IDs to send spam."""
    spam_message_ru: Optional[Message] = None
    spam_message_en: Optional[Message] = None
    spam_message_uk: Optional[Message] = None
    """Message object of spam to send."""
    money_destination: Optional[list] = []
    """List of all destinations for money send."""
    withdraw_amount: Optional[int] = None
    """Amount of money to withdraw from referral balance."""
    deadline: Optional[str] = None
    """Deadline for KYC account creating."""
    addons: Optional[list] = []
    """List of all addons"""
    skip_addons: Optional[list] = []
    """List of addons to skip"""
    quantity: Optional[int] = 0
    """Quantity of accounts"""
