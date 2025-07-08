# app/dependencies/service_dependencies.py
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_db
from app.services.auth_service import AuthService
from app.services.calendar_service import CalendarService
from app.services.chat_service import ChatService
from app.services.user_service import UserService


def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AuthService:
    """
    Returns an AuthService instance with database dependency.
    """
    return AuthService(db)


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserService:
    """
    Returns a UserService instance with database dependency.
    """
    return UserService(db)


def get_calendar_service() -> CalendarService:
    """
    Returns a CalendarService instance.
    Note: CalendarService doesn't need database dependency based on your original code.
    """
    return CalendarService()


def get_chat_service() -> ChatService:
    """
    Returns a ChatService instance.
    Note: ChatService doesn't need database dependency based on your original code.
    """
    return ChatService()

