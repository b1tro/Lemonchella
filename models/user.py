import aiogram
from decimal import Decimal, ROUND_HALF_UP
from bson.decimal128 import Decimal128
from typing import Annotated, Optional
from beanie import DecimalAnnotation
from pydantic import BaseModel, Field, field_validator
from .base import TimestampedDocument
from .order import CachedOrder
from bot.types import NavigationHistory


def round_two_decimals(value) -> Decimal:
    if isinstance(value, Decimal128):
        value = value.to_decimal()
    elif not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class User(TimestampedDocument):
    """User document."""

    id: int
    """int, User's unique udentifier."""
    lang: Optional[str]
    """str: Language code of the user."""
    telegram: Optional[aiogram.types.User] = None
    """aiogram.types.User: User telegram model."""
    is_admin: bool = False
    """bool: Is user's role aministrator."""
    is_blocked: bool = False
    """bool: Is user's access restricted."""
    is_whitelist: bool = False
    """bool: Is user's access to whitelist."""
    cooldown: Optional[int] = 0
    """int: cooldown to take order"""
    balance: Annotated[DecimalAnnotation, Field(le=100000)] = Decimal("0")
    """Decimal: User's profile balance."""
    referral_balance: Annotated[DecimalAnnotation, Field(le=100000)] = Decimal("0")
    """Decimal: User's profile balance."""
    referral_bonus: Annotated[DecimalAnnotation, Field(le=100000)] = Decimal("0")
    """Decimal: User`s bonus for referrers"""
    earned_by_referrals: Annotated[DecimalAnnotation, Field(le=100000)] = Decimal("0")
    """Decimal: User's earnings."""
    amount_of_purchases: Annotated[DecimalAnnotation, Field(le=100000)] = Decimal("0")
    """Decimal: Amount of purchases."""
    referral_percent: Optional[Annotated[DecimalAnnotation, Field(ge=0, le=100)]] = None
    """*Optional*, Decimal: User's referral percent, may be None, so user will get default value."""
    referrer_id: Optional[int] = None
    """*Optional*, int: unique udentifier for the user's referrer."""

    class Settings:
        name = "users"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"

    @field_validator("balance", "referral_balance", "referral_bonus", "earned_by_referrals", mode="before")
    @classmethod
    def round_decimal_fields(cls, value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        return round_two_decimals(value)
