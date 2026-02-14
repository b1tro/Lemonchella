from envparse import env

env.read_envfile()

TELEGRAM_BOT_TOKEN: str = env.str('TELEGRAM_BOT_TOKEN')
BUYER_BOT_TOKEN: str = env.str('BUYER_BOT_TOKEN')
TELEGRAM_LOGS_BOT_TOKEN: str = env.str('TELEGRAM_LOGS_BOT_TOKEN')
TELEGRAM_LOGS_USER_ID: int = env.int('TELEGRAM_LOGS_USER_ID')
TELEGRAM_ADMINS_CHAT_ID: int = env.int('TELEGRAM_ADMIN_CHAT_ID')

TELEGRAM_PROXY: str | None = env.str('TELEGRAM_PROXY', default=None)
"""this is only a proxy string, won't work with telethon.TelegramClient in raw format"""
TELEGRAM_API_ID: int = env.int('TELEGRAM_API_ID', default=2040)
TELEGRAM_API_HASH: str = env.str('TELEGRAM_API_HASH', default='b18441a1ff607e10a989891a5462e627')
TELEGRAM_DEVICE_MODEL: str = env.str('TELEGRAM_DEVICE_MODEL', default='MacBook Air M1')
TELEGRAM_SYSTEM_VERSION: str = env.str('TELEGRAM_SYSTEM_VERSION', default='macOS 14.4.1')
TELEGRAM_APP_VERSION: str = env.str('TELEGRAM_APP_VERSION', default='4.16.8 arm64')

REDIS_HOST: str = env.str('REDIS_HOST', default='localhost')
REDIS_PORT: int = env.int('REDIS_PORT', default=6379)
REDIS_DB: int = env.int('REDIS_DB', default=0)
REDIS_PASSWORD: str | None = env.str('REDIS_PASSWORD', default=None)

MONGODB_URI: str = env.str('MONGODB_URI', default='mongodb://localhost')

BINANCE_PAY_ID: int = env.int('BINANCE_PAY_ID')
BINANCE_USER_ID: int = env.int('BINANCE_USER_ID')
BINANCE_API_KEY: str = env.str('BINANCE_API_KEY')
BINANCE_API_SECRET: str = env.str('BINANCE_API_SECRET')
OKLINK_API_KEY: str = env.str('OKLINK_API_KEY')
EVM_WALLET_ADDRESS: str = env.str('EVM_WALLET_ADDRESS')
TRON_WALLET_ADDRESS: str = env.str('TRON_WALLET_ADDRESS')

GOOGLE_SHEETS_ENABLED: bool = env.bool('GOOGLE_SHEETS_ENABLED', default=True)
GOOGLE_SERVICE_KEY_PATH: str = env.str('GOOGLE_SERVICE_KEY_PATH', default='./key.json')
GOOGLE_SHEET_URL: str = env.str('GOOGLE_SHEET_URL', default='')
MAX_PRODUCT_QUANTITY: int = env.int('MAX_PRODUCT_QUANTITY', default=10000)
PAYMENT_MINUTES_TIMEOUT: int = env.int('PAYMENT_MINUTES_TIMEOUT', default=15)
DEFAULT_UNDEFINED_LINK: str = env.str('DEFAULT_UNDEFINED_LINK', default='https://httpstat.us/404')
DUPLICATE_SPREADSHEET_URL: str = env.str('DUBLICATE_SPREADSHEET_URL',
                                         default='https://docs.google.com/spreadsheets/d/1cU8tjHBnT5T1QKSAjMritptPpskJ2PSdB2nxvwpV9z0/edit')

SUMMARY_SHEET_URL: str = env.str('SUMMARY_SHEET_URL', default='')
SPECIAL_SHEET_URL: str = env.str('SPECIAL_SHEET_URL', default='')
