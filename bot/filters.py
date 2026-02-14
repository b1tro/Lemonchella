import re
import aiogram
from aiogram.types import CallbackQuery, Message
from aiogram import types
from bot.controllers import controllers
from .bot import bot
from aiogram.filters import Filter


class CallbackDataFilter(Filter):

    def __init__(self, text: str) -> None:
        self.text = text

    async def __call__(self, callback_query: CallbackQuery) -> bool:
        return bool(re.match(f'(?:.*/)?{self.text}$', callback_query.data))


class IsGroupFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in ('group', 'supergroup')
