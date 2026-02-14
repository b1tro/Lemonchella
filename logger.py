from loguru import logger
from config import LOG_FILES_DIR

logger.add(
    LOG_FILES_DIR / 'logs.log', 
    rotation='1 day',
    retention='7 days',
    compression='zip'
)