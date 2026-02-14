from aiogram import Router
from . import (
    error_handlers,
    customer_handlers
)


def register_handlers(router: Router):
    error_handlers.register_handlers(router=router)
    customer_handlers.register_handlers(router=router)
