from config import MONGODB_URI
from models import User, Category, HotConfig, Product, Order, Addon, AddonCustomer, Customer
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import certifi


async def init():
    kwargs = {}
    if MONGODB_URI.startswith('mongodb+srv://') or 'tls=true' in MONGODB_URI.lower():
        kwargs['tlscafile'] = certifi.where()
    client = AsyncIOMotorClient(MONGODB_URI, **kwargs)
    database = client.get_database()
    # Initialize beanie with the Sample document class and a database
    await init_beanie(
        database=database,
        document_models=[User, Product, Category, HotConfig, Order, Addon, AddonCustomer, Customer],
    )
