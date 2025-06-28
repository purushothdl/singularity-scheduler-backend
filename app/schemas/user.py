from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

import pytz
from .base import PyObjectId 

class UserBase(BaseModel):
    """
    Base model for user properties.
    """
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """
    Model for creating a new user.
    """
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    """
    Model for updating user information. All fields are optional.
    This is what the API endpoint for updating a user will expect.
    """
    username: Optional[str] = None
    timezone: Optional[str] = None

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None:
            try:
                pytz.timezone(v)
            except pytz.UnknownTimeZoneError:
                raise ValueError(f"'{v}' is not a valid timezone.")
        return v

class UserPublic(UserBase):
    """
    Model for user information that is safe to return to clients.
    """
    id: PyObjectId = Field(alias="_id", default=None)
    timezone: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {PyObjectId: str} 

class UserInDB(UserPublic):
    """
    Model for user information as stored in the database, including the hashed password.
    """
    hashed_password: str