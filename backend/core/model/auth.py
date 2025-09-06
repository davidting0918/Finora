import os
from datetime import datetime as dt
from datetime import timezone as tz

from dotenv import load_dotenv
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

load_dotenv("backend/.env")

ACCESS_TOKEN_EXPIRE_MINUTES = 120
ALGORITHM = "HS256"
ACCESS_TOKEN_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

access_token_collection = "tokens"
api_key_collection = "keys"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/access_token")

# API Key security scheme
api_key_scheme = HTTPBearer()


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


class APIKey(BaseModel):
    name: str
    api_key: str
    api_secret: str
    is_active: bool = True
    created_at: int = int(dt.now(tz.utc).timestamp())
