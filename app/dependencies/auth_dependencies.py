from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import InvalidTokenException, UserNotFoundException
from app.database.mongodb import get_db
from app.schemas.user import UserInDB, UserBase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorClient = Depends(get_db)
) -> UserInDB:
    """
    Dependency to get the current user from a JWT token.

    Verifies the token, decodes its payload, and retrieves the user
    from the database.

    Raises:
        InvalidTokenException: If the token is invalid or expired.
        UserNotFoundException: If the user from the token does not exist.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        exp: int = payload.get("exp")
        if exp and datetime.utcnow() > datetime.utcfromtimestamp(exp):
            raise InvalidTokenException(detail="Token has expired")
    except JWTError:
        raise InvalidTokenException()

    user_doc = await db.users.find_one({"email": email})

    if user_doc is None:
        raise UserNotFoundException(detail="User from token not found")

    return UserInDB(**user_doc)


