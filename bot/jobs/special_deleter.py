import datetime
import traceback
from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.enums import ParseMode

import config
from bot.keyboards.buttons import buttons
from config import TELEGRAM_LOGS_USER_ID
from logger import logger
from asyncio import sleep as asleep
from bot.bot import logs_bot
from bot import controllers
from tqdm import tqdm

from bot.sourcefile import pictures, texts
from bot import bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

texts = texts()
buttons = buttons()


async def delete_old_special_orders():
    confirmed_orders = await controllers.get_orders(status='Confirmed')
    deleted_orders = await controllers.get_orders(status='UserDeleted')

    now = datetime.datetime.now().timestamp()

    orders = [order for order in confirmed_orders + deleted_orders if
              order.is_special and now - order.created_at.timestamp() >= 8 * 60 * 60]

    for order in orders:
        user = await controllers.get_user(order.user_id)
        keyboard = [[buttons(user.lang).NewMenu]]

        try:
            await bot.bot.delete_message(
                chat_id=config.TELEGRAM_ADMINS_CHAT_ID,
                message_id=order.admins_message_id
            )
            await bot.bot.send_message(
                chat_id=order.user_id,
                text=texts(user.lang).order_deleted(order.order_items[0].product_name, order.order_items[0].quantity),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        except:
            pass

        if order.status == 'UserDeleted':
            await controllers.update_google_sheets(order)
            await asleep(3)
            order.status = 'Deleted'
        else:
            order.status = 'CustomerDeleted'
        await order.save()
