from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re

user_collection = "users"

class User(BaseModel):
    id: str
    google_id: Optional[str] = None
    email: EmailStr
    hashed_pwd: str  # if login with google, then pwd default will be hashed google id
    name: str  # if login with google, then name default will be google name
    created_at: int
    updated_at: int
    is_active: bool = True

class UserInfo(BaseModel):
    id: str
    email: EmailStr
    name: str
    created_at: int
    updated_at: int
    is_active: bool = True


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)
    pwd: str = Field(..., min_length=8, max_length=128)
    
    @validator('pwd')
    def validate_password(cls, v):
        """
        強密碼政策：
        - 至少8個字符
        - 至少包含一個大寫字母
        - 至少包含一個小寫字母
        - 至少包含一個數字
        - 至少包含一個特殊字符
        """
        if len(v) < 8:
            raise ValueError('密碼至少需要8個字符')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密碼必須包含至少一個大寫字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密碼必須包含至少一個小寫字母')
        if not re.search(r'\d', v):
            raise ValueError('密碼必須包含至少一個數字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密碼必須包含至少一個特殊字符')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """驗證用戶名格式"""
        if not v.strip():
            raise ValueError('用戶名不能為空')
        if len(v.strip()) < 2:
            raise ValueError('用戶名至少需要2個字符')
        return v.strip()