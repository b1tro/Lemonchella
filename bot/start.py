from . import database, handlers, jobs
from logger import logger
from .bot import dp, loop, bot, userbot_group, userbot, scheduler


@dp.startup()
async def startup():
    await database.init()
    logger.info("Concecting to group session...")
    async with userbot: pass
    async with userbot_group: pass
    jobs.setup_jobs()
    scheduler.start()
    # await jobs.special_deleter.delete_old_special_orders()
    handlers.register_handlers(router=dp)
    logger.info("Starting pooling...")


@dp.shutdown()
async def shutdown():
    logger.info("Goodbye!")


def start_bot():
    loop.run_until_complete(dp.start_polling(bot))
