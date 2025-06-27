from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

class DBUser(BaseModel):
    id: ObjectId = Field(alias="_id")
    email: str
    username: str
    hashed_password: str

    @field_validator("id", mode="before")
    def validate_id(cls, v):
        if isinstance(v, str):
            return ObjectId(v)
        return v 