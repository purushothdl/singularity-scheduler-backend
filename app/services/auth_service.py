from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserInDB

class AuthService:
    """Service to handle user authentication and registration."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.get_collection("users")

    async def register_user(self, user_create: UserCreate) -> UserInDB:
        """
        Registers a new user in the database.

        Args:
            user_create (UserCreate): The user creation data.

        Returns:
            UserInDB: The newly created user.

        Raises:
            UserAlreadyExistsException: If a user with the same email already exists.
        """
        hashed_password = get_password_hash(user_create.password)
        user_doc = user_create.model_dump(exclude={"password"})
        user_doc["hashed_password"] = hashed_password
        
        try:
            await self.collection.insert_one(user_doc)
        except DuplicateKeyError:
            raise UserAlreadyExistsException(detail="User with this email already exists")
        
        created_user_doc = await self.collection.find_one({"email": user_create.email})
        return UserInDB(**created_user_doc)

    async def authenticate_user(self, email: str, password: str) -> UserInDB:
        """
        Authenticates a user by verifying their email and password.

        Args:
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            UserInDB: The authenticated user.

        Raises:
            InvalidCredentialsException: If the email or password is incorrect.
        """
        user_doc = await self.collection.find_one({"email": email})
        if not user_doc:
            raise InvalidCredentialsException()

        user = UserInDB(**user_doc)
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
            
        return user
    
    def create_jwt_token_for_user(self, user: UserInDB) -> str:
        """
        Creates a JWT access token for a given user.

        Args:
            user (UserInDB): The user for whom the token is created.

        Returns:
            str: The JWT access token.
        """
        return create_access_token(subject=user.email)