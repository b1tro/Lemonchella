from datetime import datetime
from typing import Annotated, Callable, Coroutine, Iterable, Literal, Optional
from pydantic import BaseModel, Field
from beanie import DecimalAnnotation

from bot.types import ChainName, TokenName, WalletAddressLike, PaymentStatusLike


class PaymentMethod(BaseModel):
    token: TokenName
    """Name of the token."""
    chain: ChainName
    """Name of the chain."""
    wallet_address: Callable | WalletAddressLike
    """Wallet addres or callable to which returns it."""
    token_title: Optional[str] = None
    """Displayed text of the token. Text on the token button."""
    chain_title: Optional[str] = None
    """Displayed text of the chain. Text on the chain button."""
    picture: Optional[str] = None
    """Payment photo url. (useful for qr code picture)"""
    @property
    def primary_token(self):
        if isinstance(self.token, tuple):
            return self.token[0]
        return self.token
    
    def get_token_title(self):
        return self.token_title if self.token_title else self.primary_token
    
    def get_chain_title(self):
        return self.chain_title if self.chain_title else self.chain

    def has_token(self, token: TokenName):
        if isinstance(self.token, Iterable):
            return token in self.token
        return token == self.token
    
    async def get_wallet_address(self):
        if isinstance(self.wallet_address, Callable):
            address = self.wallet_address()
            if isinstance(address, Coroutine):
                return await address
            return address
        return self.wallet_address


class BasePayment(BaseModel):
    
    status: PaymentStatusLike = 'Pending'
    """Payment status"""
    received_at: Optional[datetime] = None
    """date and time while the payment was received."""


class BalancePayment(BasePayment):
    """Payment from internal user's balance."""
    
    user_id: int
    """Identifier of user who made the payment."""
    amount: Annotated[DecimalAnnotation, Field(gt=0)]
    """Amount of the payment."""

    
class CryptoTransaction(BasePayment):

    token: TokenName
    """Token id of transaction."""
    chain: ChainName
    """Chain of transaction."""
    to_wallet: WalletAddressLike
    """Wallet address of transaction reciever."""
    amount: Annotated[DecimalAnnotation, Field(gt=0)]
    """Amount of the payment transaction."""
    from_wallet: Optional[WalletAddressLike] = None
    """From wallet. May be None only if status is "Cached" """
    transaction_id: Optional[str] = None
    """TransactionId"""
    note: Optional[str] = None
    """Memo/note of transaction."""
    token_contract: Optional[str] = None
    """Token contract"""
    transaction_link: Optional[str] = None
    """Link to the transaction. optional."""
    additional_info: Optional[str] = None
    """Any text that you want. optional."""
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.token}, {self.chain}, {self.to_wallet}, {self.amount})"