from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from backend.core.model.user import CreateUserRequest, User
from backend.user.service import UserService
from backend.auth.service import get_current_active_user


router = APIRouter(
    prefix="/user",
    tags=["user"]
)

user_service = UserService()

# Public endpoint - no JWT token required
@router.post("/create")
async def create_user(request: CreateUserRequest) -> dict:
    """
    Create user - public endpoint, no authentication required
    Anyone can register a new account
    """
    try:
        user_info = await user_service.create_user(request)
        return {
            "status": 1,
            "data": user_info.model_dump(),
            "message": "User registered successfully"
        }
    except Exception as e:
        raise e

# Protected endpoint - JWT token required
@router.get("/me")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    Get current user info - requires JWT authentication
    Returns complete information of the authenticated user
    """
    try:
        return {
            "status": 1,
            "data": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "created_at": current_user.created_at,
                "updated_at": current_user.updated_at,
                "is_active": current_user.is_active
            },
            "message": f"Welcome, {current_user.name}!"
        }
    except Exception as e:
        raise e