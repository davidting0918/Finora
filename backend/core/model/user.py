import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

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

    @field_validator("pwd")
    @classmethod
    def validate_password(cls, v):
        """
        Strong password policy:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate username format"""
        if not v.strip():
            raise ValueError("Username cannot be empty")
        if len(v.strip()) < 2:
            raise ValueError("Username must be at least 2 characters long")
        return v.strip()
