from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.user import UserUpdate, UserInDB
from app.core.exceptions import UserNotFoundException

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.get_collection("users")

    async def update_user_profile(self, user_id: str, user_update: UserUpdate) -> UserInDB:
        """
        Updates a user's profile information in the database.
        """
        update_data = user_update.model_dump(exclude_unset=True)

        if not update_data:
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        else:
            user_doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True 
            )

        if not user_doc:
            raise UserNotFoundException()
            
        return UserInDB(**user_doc)