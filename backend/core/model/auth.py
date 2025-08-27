from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

load_dotenv("backend/.env")

ACCESS_TOKEN_EXPIRE_MINUTES = 120
ALGORITHM = "HS256"
ACCESS_TOKEN_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

access_token_collection = "tokens"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/access_token")


class GoogleAuthRequest(BaseModel):
    token: str

class GoogleUserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: str

class EmailAuthRequest(BaseModel):
    email: str
    pwd: str

class AccessToken(BaseModel):
    token: str
    user_id: str
    created_at: int
    expires_at: int
    is_active: bool = True