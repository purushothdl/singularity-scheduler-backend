from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

log = logging.getLogger(__name__)

class MongoManager:
    """
    A singleton-like class to manage the MongoDB connection.
    This ensures that we create the client only once and reuse it
    across the application lifetime.
    """
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

db_manager = MongoManager()

async def connect_to_mongo():
    """
    Connects to the MongoDB instance at application startup.
    This function is called by the startup event handler in main.py.
    """
    log.info("Connecting to MongoDB...")
    db_manager.client = AsyncIOMotorClient(settings.MONGO_URI)
    db_manager.database = db_manager.client.get_database(settings.DATABASE_NAME)
    log.info("Successfully connected to MongoDB.")

async def close_mongo_connection():
    """

    Closes the MongoDB connection at application shutdown.
    This function is called by the shutdown event handler in main.py.
    """
    log.info("Closing MongoDB connection...")
    if db_manager.client:
        db_manager.client.close()
    log.info("MongoDB connection closed.")


def get_db() -> AsyncIOMotorDatabase:
    """
    A dependency function to get the database instance.

    This ensures that routes have access to the database session
    that was established at startup.
    
    Returns:
        The application's `AsyncIOMotorDatabase` instance.
    """
    if db_manager.database is None:
        # This is a safeguard for cases where the dependency is used
        # without the startup event having run (e.g., in a script).
        # In a running FastAPI app, this should not be triggered.
        raise Exception("Database not initialized. Call connect_to_mongo() first.")
    return db_manager.database