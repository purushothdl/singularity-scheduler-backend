from fastapi import APIRouter, Depends
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.service_dependencies import ServiceProvider
from app.schemas.user import UserPublic, UserUpdate, UserInDB

router = APIRouter(prefix="/users", tags=["Users"])

@router.put("/me", response_model=UserPublic)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    services: ServiceProvider = Depends(ServiceProvider)
):
    """
    Allows the authenticated user to update their profile information.
    """
    user_service = services.get_user_service() 
    updated_user = await user_service.update_user_profile(
        user_id=str(current_user.id), 
        user_update=user_update
    )
    return updated_user