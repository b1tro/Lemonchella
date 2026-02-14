from decimal import Decimal
from typing import Annotated, Optional
from beanie import DecimalAnnotation, Document
from pydantic import Field
from config import DEFAULT_UNDEFINED_LINK


class HotConfig(Document):
    """HotConfig document."""

    id: int = 1
    """int: Doc id, must be 1 because it's single document collection."""
    MANAGER_USERNAME: Optional[str] = 'username'
    """str: telegram username of manager"""
    DEFAULT_REFERRAL_PERCENT: Annotated[DecimalAnnotation, Field(ge=0, le=100)] = Decimal(5)
    """Decimal: Referral percent for users with unset value."""
    HELP_BUTTON_URL: Optional[str] = DEFAULT_UNDEFINED_LINK
    """str: link when you press the help button."""
    FEEDBACK_BUTTON_URL: Optional[str] = DEFAULT_UNDEFINED_LINK
    """str: link when you press the feedback button."""
    RULES_BUTTON_URL: Optional[str] = DEFAULT_UNDEFINED_LINK
    """str: link when you press the rules button."""
    MANAGERS: Optional[dict] = None
    """dict: filters for defining manager in group"""
    WITHDRAW_MANAGER: Optional[str] = None
    """str: manager, who handles withdraw requests"""
    CUSTOMER_FEE: Optional[int] = 15
    """int: fee of customer"""
    SHEET_GID: Optional[int] = 0
    """int: id of sheet"""
    SHEET_GID_SPECIAL: Optional[int] = 0
    """int: id of special sheet"""

    class Settings:
        name = 'hotconfig'
