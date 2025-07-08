from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.service_dependencies import ServiceProvider
from app.dependencies.auth_dependencies import get_current_user
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserPublic, UserInDB

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, 
    services: ServiceProvider = Depends(ServiceProvider) 
):
    """
    Handles user registration and returns a JWT access token.
    The service is accessed from the dependency container.
    """
    auth_service = services.get_auth_service()
    new_user = await auth_service.register_user(user_in)
    access_token = auth_service.create_jwt_token_for_user(new_user)
    return Token(access_token=access_token)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    services: ServiceProvider = Depends(ServiceProvider) 
):
    """
    Handles user login and returns a JWT access token.
    """
    auth_service = services.get_auth_service()
    user = await auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )
    
    access_token = auth_service.create_jwt_token_for_user(user)
    return Token(access_token=access_token)

@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Fetches the details of the currently authenticated user.
    """
    return current_user