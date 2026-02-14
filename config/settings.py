import datetime
from pathlib import Path
from yarl import URL
from . import dotenv

ROOT_DIR = Path(__file__).parents[1]
LOG_FILES_DIR = ROOT_DIR / 'logs'
SESSIONS_DIR = ROOT_DIR / 'sessions'
PRODUCTS_DIR = ROOT_DIR / 'products'
ACTIVE_PRODUCTS_DIR = PRODUCTS_DIR / 'active'
ARCHIVED_PRODUCTS_DIR = PRODUCTS_DIR / 'archived'
CACHED_PRODUCTS_DIR = PRODUCTS_DIR / 'cached'

ADMINS_LIST = [958288901, 946348839, 5609806336, ]

CONFIG_CACHE_TIME = datetime.timedelta(seconds=120)
USER_CACHE_TIME = datetime.timedelta(days=3)
TOKEN_CONTRACTS = {
    'USDT': {
        'ARBITRUM': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        'BSC': '0x55d398326f99059ff775485246999027b3197955',
        'TRON': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
        'SOLANA': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
        'POLYGON': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'OPTIMISM': '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58'
    },
    'USDC': {
        'ARBITRUM': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831|0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        'BSC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
        'TRON': 'TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8',
        'SOLANA': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        'POLYGON': '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
        'OPTIMISM': '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85'
    },
    'BUSD': {
        'BSC': '0xe9e7cea3dedca5984780bafc599bd69add087d56'
    },
}
PAYMENT_METHODS = [
    # USDT
    # {
    #     'token': 'USDT',
    #     'chain': 'BP',
    #     'chain_title': 'Binance Pay',
    #     'wallet_address': dotenv.BINANCE_PAY_ID,
    #     'picture': 'https://telegra.ph/pej-06-19#BP'
    # },
    {
        'token': 'USDT',
        'chain': 'ARBITRUM',
        'chain_title': 'Arbitrum One',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/QNsvnSt'
    },
    {
        'token': 'USDT',
        'chain': 'BSC',
        'chain_title': 'BSC (BEP20)',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/wpmq62G'
    },
    {
        'token': 'USDT',
        'chain': 'TRON',
        'chain_title': 'TRON (TRC20)',
        'wallet_address': dotenv.TRON_WALLET_ADDRESS,
        'picture': 'https://ibb.co/MGzQX8c'
    },
    {
        'token': 'USDT',
        'chain': 'POLYGON',
        'chain_title': 'POLYGON',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/wpmq62G'
    },
    {
        'token': 'USDT',
        'chain': 'OPTIMISM',
        'chain_title': 'OPTIMISM',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/wpmq62G'
    },
    # USDC
    # {
    #     'token': 'USDC',
    #     'chain': 'BP',
    #     'chain_title': 'Binance Pay',
    #     'wallet_address': dotenv.BINANCE_PAY_ID,
    #     'picture': 'https://telegra.ph/pej-06-19#BP'
    # },
    {
        'token': 'USDC',
        'chain': 'ARBITRUM',
        'chain_title': 'Arbitrum One',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/wpmq62G'
    },
    {
        'token': 'USDC',
        'chain': 'BSC',
        'chain_title': 'BSC (BEP20)',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/wpmq62G'
    },
    {
        'token': 'USDC',
        'chain': 'POLYGON',
        'chain_title': 'POLYGON',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/wpmq62G'
    },
    {
        'token': 'USDC',
        'chain': 'OPTIMISM',
        'chain_title': 'OPTIMISM',
        'wallet_address': dotenv.EVM_WALLET_ADDRESS,
        'picture': 'https://ibb.co/wpmq62G'
    },
    # BUSD
    # {
    #     'token': 'BUSD',
    #     'chain': 'BP',
    #     'chain_title': 'Binance Pay',
    #     'wallet_address': dotenv.BINANCE_PAY_ID,
    #     'picture': 'https://telegra.ph/pej-06-19#BP'
    # },
    # {
    #     'token': 'BUSD',
    #     'chain': 'BSC',
    #     'chain_title': 'BSC (BEP20)',
    #     'wallet_address': dotenv.EVM_WALLET_ADDRESS,
    #     'picture': 'https://telegra.ph/file/535d8c12850663c8912ae.jpg#EVM'
    # },
]
