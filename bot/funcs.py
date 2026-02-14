import functools
import random
from typing import Callable
from beanie.odm.operators.update.general import Inc

import aiohttp


def pass_exception(coro: Callable, *exceptions):
    @functools.wraps(coro)
    async def wrapper():
        try:
            return await coro
        except exceptions:
            pass

    return wrapper()


def id_factory(digits: int = 10):
    return random.randint(10 ** (digits - 1), (10 ** digits) - 1)
