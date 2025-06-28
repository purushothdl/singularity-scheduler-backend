from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from functools import lru_cache

from app.database.mongodb import get_db
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.user_service import UserService

class ServiceProvider:
    """
    A dependency container that provides instances of all services.

    This class uses @lru_cache on its methods to ensure that for a single
    request-response cycle, each service is only instantiated once.
    This acts like a singleton pattern per request.
    """

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_db)):
        """
        Initializes the ServiceProvider with a database connection.

        Args:
            db (AsyncIOMotorDatabase): The MongoDB database connection.
        """
        self.db = db

    @lru_cache(maxsize=None)
    def get_auth_service(self) -> AuthService:
        """Returns a singleton instance of the AuthService for the current request."""
        return AuthService(self.db)

    @lru_cache(maxsize=None)
    def get_user_service(self) -> UserService:
        """Returns a singleton instance of the UserService for the current request."""
        return UserService(self.db)
    
    @lru_cache(maxsize=None)
    def get_chat_service(self) -> ChatService:
        """Returns a singleton instance of the ChatService for the current request."""
        return ChatService()