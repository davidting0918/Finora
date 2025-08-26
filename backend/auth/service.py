from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime as dt, timedelta as td, timezone as tz
from backend.core.database import MongoAsyncClient
from backend.core.model.user import User, user_collection
from backend.core.model.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    ALGORITHM, 
    ACCESS_TOKEN_SECRET_KEY,
    access_token_collection,
    AccessToken,
    oauth2_scheme,
    pwd_context
)
from backend.auth.providers.google import GoogleAuthProvider
import uuid
import os

_db = MongoAsyncClient()
class AuthService:
    def __init__(self):
        self.db = _db
        self.google_provider = GoogleAuthProvider(
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
        )
        self.secret_key = ACCESS_TOKEN_SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, user_id: str) :
        to_encode = {}
        current_time = dt.now(tz.utc)
        expire = current_time + td(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "sub": user_id,
            "exp": expire,
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return AccessToken(
            token=encoded_jwt,
            user_id=user_id,
            created_at=int(current_time.timestamp()),
            expires_at=int(expire.timestamp()),
            is_active=True
        )

    async def store_token(self, token: AccessToken):
        token_info = token.model_dump()
        await self.db.insert_one(access_token_collection, token_info)

    async def find_valid_token(self, user_id: str) -> Optional[AccessToken]:
        current_time = int(dt.now(tz.utc).timestamp())
        
        token_dict = await self.db.find_one(
            access_token_collection,
            {
                "user_id": user_id,
                "expires_at": {"$gt": current_time},
                "is_active": True
            }
        )
        
        if token_dict:
            return AccessToken(**token_dict)
        return None

    async def get_or_create_token(self, user_id: str) -> dict:

        existing_token = await self.find_valid_token(user_id)
        
        if existing_token:
            return {
                "access_token": existing_token.token,
                "token_type": "bearer",
            }
        else:
            access_token = self.create_access_token(
                user_id=user_id
            )
            
            await self.store_token(access_token)
            
            return {
                "access_token": access_token.token,
                "token_type": "bearer",
            }

    async def authenticate_user(self, name: str = None, email: str = None, password: str = None) -> Optional[User]:
        if name:
            user_dict = await self.db.find_one(user_collection, {"name": name})
        elif email:
            user_dict = await self.db.find_one(user_collection, {"email": email})
        else:
            raise ValueError("Either name or email must be provided")
        
        if not user_dict:
            return None
        
        user = User(**user_dict)
        if not self.verify_password(password, user.hashed_pwd):
            return None
        return user

    async def authenticate_google_user(self, token: str) -> Optional[User]:
        google_user_info = await self.google_provider.verify_token(token)
        
        user_dict = await self.db.find_one(
            user_collection, 
            {"$or": [{"email": google_user_info.email}, {"google_id": google_user_info.id}]}
        )
        
        if user_dict:
            user = User(**user_dict)
            
            if not user.google_id:
                await self.db.update_one(
                    user_collection,
                    {"id": user.id},
                    {
                        "google_id": google_user_info.id,
                        "updated_at": int(dt.now(tz.utc).timestamp())
                    }
                )
                user.google_id = google_user_info.id
            
            return user
        else:
            new_user = User(
                id=str(uuid.uuid4())[:8],
                google_id=google_user_info.id,
                email=google_user_info.email,
                hashed_pwd=self.get_password_hash(google_user_info.id),
                name=google_user_info.name,
                created_at=int(dt.now(tz.utc).timestamp()),
                updated_at=int(dt.now(tz.utc).timestamp()),
                is_active=True
            )
            await self.db.insert_one(user_collection, new_user.model_dump())
            return new_user

# separated function for other routers authentication
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Dependency function to get current authenticated user from JWT token
    This can be used across all routers without instantiating AuthService
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user_dict = await _db.find_one(user_collection, {"id": user_id})
    if user_dict is None:
        raise credentials_exception
    
    return User(**user_dict)

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency function to get current active user
    Ensures the user account is not deactivated
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user