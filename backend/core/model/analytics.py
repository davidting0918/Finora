from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime as dt
from backend.core.model.transaction import TransactionType, CategoryId, Currency
from enum import Enum

class AnalyticsPeriod(Enum):
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"

class AnalyticsQuery(BaseModel):
    start_date: Optional[dt] = None
    end_date: Optional[dt] = None
    period: AnalyticsPeriod = AnalyticsPeriod.monthly
    transaction_type: Optional[TransactionType] = None
    category_id: Optional[CategoryId] = None
    
class CategoryAnalytics(BaseModel):
    category_id: str
    category_name: str
    total_amount: float
    transaction_count: int
    percentage: float
    subcategories: List[Dict[str, Any]]

class PeriodAnalytics(BaseModel):
    period: str
    income: float
    expense: float
    net: float
    transaction_count: int

class SpendingTrend(BaseModel):
    date: str
    amount: float
    transaction_count: int

class TagAnalytics(BaseModel):
    tag: str
    total_amount: float
    transaction_count: int
    avg_amount: float

class FinancialSummary(BaseModel):
    total_income: float
    total_expense: float
    net_income: float
    avg_daily_expense: float
    largest_expense: Dict[str, Any]
    most_frequent_category: Dict[str, Any]

class AnalyticsOverview(BaseModel):
    summary: FinancialSummary
    category_breakdown: List[CategoryAnalytics]
    spending_trends: List[SpendingTrend]
    top_tags: List[TagAnalytics]
    period_comparison: List[PeriodAnalytics]
