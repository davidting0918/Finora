from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime as dt, timezone as tz, timedelta as td
from enum import Enum

# Database collection names
transaction_collection = "transactions"
category_collection = "categories" 
subcategory_collection = "subcategories"

class TransactionType(Enum):
    income = "income"
    expense = "expense"

class Currency(Enum):
    USD = "USD"
    JPY = "JPY"
    KRW = "KRW"
    CNY = "CNY"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    HKD = "HKD"
    TWD = "TWD"

class CategoryId(Enum):
    #expense
    shopping = "shopping"
    food_dining = "food_dining"
    transportation = "transportation"
    entertainment = "entertainment"
    living = "living"
    education = "education"
    health = "health"
    investment = "investment"
    travel = "travel" 

    # income
    income = "income"

    # other
    other = "other"

class SubCategoryId(Enum):
    # food_dining
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"
    drink = "drink"

    # shopping
    clothing = "clothing"
    electronics = "electronics"
    home_goods = "home_goods"

    # transportation
    ticket = "ticket"
    bus = "bus"
    train = "train"
    taxi = "taxi"
    parking = "parking"

    # entertainment
    movie = "movie"
    concert = "concert"
    sports = "sports"
    game = "game"

    # living
    rent = "rent"
    mortgage = "mortgage"
    telecom = "telecom"

    # education
    tuition = "tuition"
    software = "software"

    # health
    medical = "medical"
    insurance = "insurance"

    # investment
    stock = "stock"
    mutual_fund = "mutual_fund"
    crypto = "crypto"

    # travel
    hotel = "hotel"
    flight = "flight"

    # other
    other = "other"




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


# API related model

class CreateTransactionRequest(BaseModel):
    type: TransactionType
    currency: Currency = Currency.TWD
    amount: float
    transaction_date: dt
    category_id: CategoryId
    subcategory_id: SubCategoryId
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class UpdateTransactionRequest(BaseModel):
    type: Optional[TransactionType] = None
    currency: Optional[Currency] = None
    amount: Optional[float] = None
    transaction_date: Optional[dt] = None
    category_id: Optional[CategoryId] = None
    subcategory_id: Optional[SubCategoryId] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class Transaction(BaseModel):
    id: str
    user_id: str
    user_name: str
    type: TransactionType
    currency: Currency = Currency.TWD
    amount: float
    transaction_date: dt
    category_id: CategoryId
    subcategory_id: SubCategoryId
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
    
    def update(self, request: UpdateTransactionRequest):
        for key, value in request.model_dump(mode='json').items():
            if value is not None:
                setattr(self, key, value)
        self.updated_at = int(dt.now(tz.utc).timestamp())