from fastapi import APIRouter, Depends, Query
from backend.core.model.analytics import AnalyticsQuery, AnalyticsPeriod
from backend.core.model.transaction import TransactionType, CategoryId
from backend.analytics.service import AnalyticsService
from backend.core.model.user import User
from backend.auth.service import get_current_active_user
from typing import Annotated, Optional
from datetime import datetime as dt

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()

@router.get("/overview")
async def get_analytics_overview_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: Optional[dt] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[dt] = Query(None, description="End date filter (ISO format)"),
    period: AnalyticsPeriod = Query(AnalyticsPeriod.monthly, description="Analysis period granularity"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    category_id: Optional[CategoryId] = Query(None, description="Filter by category ID")
):
    """
    Get comprehensive analytics overview including summary, trends, and breakdowns
    """
    try:
        query = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date,
            period=period,
            transaction_type=transaction_type,
            category_id=category_id
        )
        
        overview = await analytics_service.get_analytics_overview(query, current_user)
        
        return {
            "status": 1,
            "data": overview.model_dump(mode='json'),
            "message": "Analytics overview fetched successfully"
        }
    except Exception as e:
        raise e

@router.get("/category-breakdown")
async def get_category_breakdown_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: Optional[dt] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[dt] = Query(None, description="End date filter (ISO format)"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type")
):
    """
    Get detailed breakdown of spending by categories and subcategories
    """
    try:
        query = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        
        breakdown = await analytics_service.get_category_breakdown(query, current_user)
        
        return {
            "status": 1,
            "data": [category.model_dump(mode='json') for category in breakdown],
            "message": "Category breakdown fetched successfully"
        }
    except Exception as e:
        raise e

@router.get("/spending-trends")
async def get_spending_trends_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: Optional[dt] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[dt] = Query(None, description="End date filter (ISO format)"),
    period: AnalyticsPeriod = Query(AnalyticsPeriod.weekly, description="Analysis period granularity"),
    category_id: Optional[CategoryId] = Query(None, description="Filter by category ID")
):
    """
    Get spending trends over time with specified granularity
    """
    try:
        query = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date,
            period=period,
            category_id=category_id
        )
        
        trends = await analytics_service.get_spending_trends(query, current_user)
        
        return {
            "status": 1,
            "data": [trend.model_dump(mode='json') for trend in trends],
            "message": "Spending trends fetched successfully"
        }
    except Exception as e:
        raise e

@router.get("/financial-summary")
async def get_financial_summary_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: Optional[dt] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[dt] = Query(None, description="End date filter (ISO format)")
):
    """
    Get high-level financial summary including income, expense, and key metrics
    """
    try:
        query = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date
        )
        
        summary = await analytics_service.get_financial_summary(query, current_user)
        
        return {
            "status": 1,
            "data": summary.model_dump(mode='json'),
            "message": "Financial summary fetched successfully"
        }
    except Exception as e:
        raise e

@router.get("/tag-analytics")
async def get_tag_analytics_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: Optional[dt] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[dt] = Query(None, description="End date filter (ISO format)")
):
    """
    Get analytics based on transaction tags showing spending patterns
    """
    try:
        query = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date
        )
        
        tag_analytics = await analytics_service.get_tag_analytics(query, current_user)
        
        return {
            "status": 1,
            "data": [tag.model_dump(mode='json') for tag in tag_analytics],
            "message": "Tag analytics fetched successfully"
        }
    except Exception as e:
        raise e


