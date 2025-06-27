from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserDB(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    username: str
    hashed_password: str
    timezone: Optional[str] = None

class UserInDB(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str
    timezone: Optional[str] = None