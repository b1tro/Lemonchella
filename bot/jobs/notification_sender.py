import datetime
import traceback
from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.enums import ParseMode

import config
from config import TELEGRAM_LOGS_USER_ID
from logger import logger
from asyncio import sleep as asleep
from bot.bot import logs_bot
from bot import controllers
from tqdm import tqdm

from bot.sourcefile import pictures, texts
from bot import bot

texts = texts()

