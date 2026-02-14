import asyncio
from redis.asyncio import Redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import telethon
from yarl import URL
from config import (
    PAYMENT_METHODS,
    SESSIONS_DIR,
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_LOGS_BOT_TOKEN,
    TELEGRAM_PROXY,
    TELEGRAM_APP_VERSION,
    TELEGRAM_DEVICE_MODEL,
    TELEGRAM_SYSTEM_VERSION,
    BUYER_BOT_TOKEN
)
from models import PaymentMethod
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import socks  # necessary package for telethon proxy work

loop = asyncio.get_event_loop()
payment_methods = [
    PaymentMethod.model_validate(obj)
    for obj in PAYMENT_METHODS
]
redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD
)
storage = RedisStorage(redis)
dp = Dispatcher(storage=storage)
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True
)
buyer_bot = Bot(
    token=BUYER_BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True
)
logs_bot = Bot(
    token=TELEGRAM_LOGS_BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True
)
scheduler = AsyncIOScheduler()
proxy = TELEGRAM_PROXY
userbot = telethon.TelegramClient(
    session=str(SESSIONS_DIR / 'userbot'),
    api_id=TELEGRAM_API_ID,
    api_hash=TELEGRAM_API_HASH,
    proxy=proxy,
    device_model=TELEGRAM_DEVICE_MODEL,
    system_version=TELEGRAM_SYSTEM_VERSION,
    app_version=TELEGRAM_APP_VERSION,
)
userbot_group = telethon.TelegramClient(
    session=str(SESSIONS_DIR / 'userbot_group'),
    api_id=TELEGRAM_API_ID,
    api_hash=TELEGRAM_API_HASH,
    proxy=proxy,
    device_model=TELEGRAM_DEVICE_MODEL,
    system_version=TELEGRAM_SYSTEM_VERSION,
    app_version=TELEGRAM_APP_VERSION,
)
