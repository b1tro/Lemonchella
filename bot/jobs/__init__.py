from ..bot import scheduler
from . import special_deleter


def setup_jobs():
    scheduler.add_job(special_deleter.delete_old_special_orders, "interval", hours=1)
