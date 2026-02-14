import aiogram
from decimal import Decimal
from typing import Annotated, Optional
from beanie import DecimalAnnotation
from pydantic import BaseModel, Field
from .base import TimestampedDocument
from .order import CachedOrder
from bot.types import NavigationHistory


class Addon(TimestampedDocument):
    """Addon document."""

    id: int
    """int, addon's unique identifier."""
    question: dict
    """str, question to ask"""
    options: dict
    """dict, options with prices"""
    skip_addons: Optional[list] = []
    """list, ids of addons to skip"""
    sum_filter: Optional[float] = None
    """float, total amount to apply filter"""

    class Settings:
        name = "addons"
