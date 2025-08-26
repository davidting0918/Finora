from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from backend.core.model.auth import GoogleAuthRequest, EmailAuthRequest
from backend.core.model.user import User
from backend.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()

@router.post("/google/login")
async def validate_google_login_route(request: GoogleAuthRequest):
    user = await auth_service.authenticate_google_user(request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    token_info = await auth_service.get_or_create_token(user.id)
    
    return {
        "access_token": token_info["access_token"],
        "token_type": token_info["token_type"],
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }

@router.post("/email/login")
async def validate_email_login_route(request: EmailAuthRequest):
    user = await auth_service.authenticate_user(email=request.email, password=request.pwd)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token_info = await auth_service.get_or_create_token(user.id)
    
    return {
        "access_token": token_info["access_token"],
        "token_type": token_info["token_type"],
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }

@router.post("/access_token")
async def get_access_token_route(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await auth_service.authenticate_user(name=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    token_info = await auth_service.get_or_create_token(user.id)
    
    return {
        "access_token": token_info["access_token"], 
        "token_type": token_info["token_type"]
    }