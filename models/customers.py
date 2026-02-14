import aiogram
from decimal import Decimal
from typing import Annotated, Optional
from beanie import DecimalAnnotation
from pydantic import BaseModel, Field
from .base import TimestampedDocument
from .order import CachedOrder
from bot.types import NavigationHistory


class Customer(TimestampedDocument):
    """Customer document."""

    id: int
    username: str
    taken_orders_number: int = 0
    total_money_received: int = 0
    language: str = 'ru'
    minimum_sum: int = 0
    special_orders: bool = False
    is_blocked: bool = False
    rank: int = 0
    wallet: str = ''

    class Settings:
        name = "customers"

    async def save(self, **kwargs):
        data = self.model_dump(exclude={"_id"})
        await self.get_motor_collection().update_one({"_id": self.id}, {"$set": data}, upsert=True, **kwargs)
        return self
