from beanie import Document
from typing import Optional
from pydantic import BaseModel
from .base import TimestampedDocument


class CategoryItem(BaseModel):
    """Item identifier for category."""

    product_id: Optional[int] = None
    """int, Product identifier, if set, item will be product."""
    category_id: Optional[int] = None
    """int, Category identifier, if set, item will be category."""
    button_text: Optional[dict | str] = None
    """optional, str, text to display on button, will be attribute name if not passed."""
    position: Optional[str] = None
    """optional, str, buttons will be sorted by this parameter example: "1:1"."""


class Category(TimestampedDocument):
    """Category model."""

    id: int
    """int, category unique identifier."""
    name: str
    """str, category name to identify it easier, or use as default button text."""
    button_text: Optional[dict | str] = None
    """optional, str, text to display on button, will be attribute name if unset."""
    title: Optional[dict | str] = None
    """optional, str, main text to display in this category."""
    picture: Optional[str] = None
    """optional, str, image url."""
    category_items: list[CategoryItem]
    """list, CategoryItem, list of items in this category."""

    class Settings:
        name = "categories"
