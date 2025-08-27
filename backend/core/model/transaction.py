from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

# Database collection names
transaction_collection = "transactions"
category_collection = "categories" 
subcategory_collection = "subcategories"

class TransactionType(Enum):
    income = "income"
    expense = "expense"


class Transaction(BaseModel):
    id: str
    user_id: str
    type: TransactionType
    amount: Decimal
    transaction_date: datetime
    category_id: str
    subcategory_id: str
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: int
    updated_at: int
    is_deleted: bool = False
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v and len(v) > 200:
            raise ValueError('Description must be 200 characters or less')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v and len(v) > 500:
            raise ValueError('Notes must be 500 characters or less')
        return v

class SubCategory(BaseModel):
    id: str
    category_id: str
    name: str
    color: str
    icon: str
    is_active: bool = True
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 50:
            raise ValueError('Name must be 50 characters or less')
        return v.strip()

class Category(BaseModel):
    id: str
    name: str
    type: TransactionType
    color: str
    icon: str
    is_active: bool = True
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 50:
            raise ValueError('Name must be 50 characters or less')
        return v.strip()


