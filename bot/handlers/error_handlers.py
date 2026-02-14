import traceback
from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.enums import ParseMode
from config import TELEGRAM_LOGS_USER_ID
from logger import logger
from ..bot import logs_bot


def register_handlers(router: Router):
    router.error.register(log_error)


async def log_error(error: ErrorEvent):
    traceback_str = traceback.format_exc()
    logger.exception(traceback_str)
    query = error.update.message if error.update.message else error.update.callback_query
    user = '<b>User(' + (
        f'@{query.from_user.username}'
        if query.from_user.username
        else f'id={query.from_user.id}'
    ) + ')</b>'
    text = f'<b>CUSTOMER - </b>{user}\n<pre class="log"><code>{traceback_str[-1000:]}</code></pre>'
    await logs_bot.send_message(
        chat_id=TELEGRAM_LOGS_USER_ID,
        text=text,
        parse_mode=ParseMode.HTML,
    )
