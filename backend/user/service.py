from backend.core.database import MongoAsyncClient
from backend.core.model.user import user_collection, User, CreateUserRequest, UserInfo
from fastapi import HTTPException
import uuid
from backend.core.model.auth import pwd_context
from datetime import datetime as dt, timezone as tz

class UserService:
    def __init__(self):
        self.db = MongoAsyncClient()

    async def create_user(self, request: CreateUserRequest) -> UserInfo:
        # first check if user already exists
        user = await self.db.find_one(
            user_collection,
            {"email": request.email}
        )
        if user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # create user
        user = User(
            id=str(uuid.uuid4())[:8],
            email=request.email,
            name=request.name,
            hashed_pwd=pwd_context.hash(request.pwd),
            created_at=int(dt.now(tz.utc).timestamp()),
            updated_at=int(dt.now(tz.utc).timestamp()),
            is_active=True
        )
        await self.db.insert_one(user_collection, user.model_dump())
        return UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active
        )
    
    async def get_user_info(self, user_id: str) -> UserInfo:
        user_dict = await self.db.find_one(user_collection, {"id": user_id})
        if not user_dict:
            raise HTTPException(status_code=404, detail="User not found")
        user = User(**user_dict)
        return UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active
        )