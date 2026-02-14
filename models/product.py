import datetime
from decimal import Decimal
from typing import Annotated, Optional
from beanie import DecimalAnnotation
from pydantic import Field, field_serializer, field_validator
from .base import TimestampedDocument
from bson.decimal128 import Decimal128


class Product(TimestampedDocument):
    """Catalog product model."""

    id: int
    """int, category unique identifier."""
    name: str
    """str, product name to identify it easier, or use as default button text."""
    description: dict
    """str, product description."""
    addons: Optional[list[int]] = []
    """list, ids of all addons"""
    show_tos: bool = True
    """bool, if True, then button to faq will be displayed."""
    button_text: Optional[str] = None
    """optional, str, text to be displayed on button, will be attribute name if unset."""
    min_quantity: Optional[int] = None
    """optional, int, minimal quantity to purchase for this product, 1 by default."""
    price: Optional[dict] = None
    """optional, Decimal, product price, product will be unable to purchase if unset."""
    customer_price: Annotated[DecimalAnnotation, Field()] = None
    """optional, Decimal, product price, product will be unable to purchase if unset."""
    linked_options: Optional[list[int]] = None
    """optional, ids of available options for this product."""
    picture: Optional[str] = None
    """optional, str, product picture url."""
    finish_picture: Optional[str] = None
    """optional, str, picture url to show while purchased."""
    data_format: Optional[str] = None

    min_deadline: Optional[int] = 0
    """int, minimal deadline in hours"""

    class Settings:
        name = "products"
