from typing import Literal


NavigationHistory = tuple[str, ...]
PaymentStatusLike = Literal['Success', 'Pending', 'Cached']
TokenName = Literal['USDT', 'USDC', 'BUSD', 'ARBUSDCE'] | str
"""List of available tokens:

USDT -> Tether USDT
USDC -> Coinvase USDC
BUSD -> Binance BUSD
ARBUSDCE -> Bridged USDC in ARBITRUM
"""
ChainName = Literal['TRON', 'BP', 'BSC', 'ARBITRUM', 'OPTIMISM', 'POLYGON'] | str
"""List of available chains:

TRON -> TRON
BP -> Binance Pay (not real blockchain)
BSC -> BNB CHAIN
ARBITRUM -> Arbitrum One blockchain
OPTIMISM -> OPTIMISM
POLYGON -> Polygon PoS Chain
"""
WalletAddressLike = str | int