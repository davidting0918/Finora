"""
Analytics endpoints tests using shared test data across all test functions.
This module uses a module-scoped fixture to set up test data once and reuse it 
across all test functions, improving test performance and avoiding data recreation.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime as dt
from backend.main import app
from backend.user.service import UserService
from backend.auth.service import AuthService
from backend.transaction.service import TransactionService
from backend.core.initializer import init_category
from backend.core.database import MongoAsyncClient
import json

# Module-scoped fixtures that set up shared test data
@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_analytics_test_module():
    """Module-level setup and cleanup for analytics tests"""
    db_client = MongoAsyncClient(test_mode=True)
    try:
        # Clean and initialize test environment
        from backend.tests.conftest import cleanup_test_db
        await cleanup_test_db(db_client)
        await init_category()
        yield
        # Module cleanup
        await cleanup_test_db(db_client)
    finally:
        if db_client:
            await db_client.close()

@pytest_asyncio.fixture(scope="module")
async def shared_analytics_data():
    """
    Module-scoped fixture that sets up analytics test data once and preserves it 
    across all test functions in this module.
    """
    # Load test data
    path = "backend/data/test_analytics_data.json"
    with open(path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    # Create user
    user_service = UserService()
    auth_service = AuthService()
    
    user_data = test_data["user"]
    created_user = await user_service.create_user(
        email=user_data["email"],
        name=user_data["name"],
        pwd=user_data["pwd"]
    )
    
    # Login user to get tokens
    login_result = await auth_service.login_user(
        email=user_data["email"], 
        pwd=user_data["pwd"]
    )
    
    # Create transactions
    transaction_service = TransactionService()
    created_transactions = []
    
    for transaction_data in test_data["transactions"]:
        # Convert string date to datetime
        if isinstance(transaction_data["transaction_date"], str):
            transaction_data["transaction_date"] = dt.fromisoformat(transaction_data["transaction_date"])
        
        created_transaction = await transaction_service.create_transaction(
            transaction_data, created_user
        )
        created_transactions.append(created_transaction)
    
    # Return test context
    return {
        "user": created_user,
        "auth_tokens": login_result,
        "transactions": created_transactions,
        "access_token": login_result.access_token,
        "raw_data": test_data
    }

@pytest.fixture(scope="module") 
def auth_headers(shared_analytics_data):
    """Get authorization headers for analytics tests"""
    return {"Authorization": f"Bearer {shared_analytics_data['access_token']}"}

@pytest_asyncio.fixture(scope="module")
async def async_client_for_analytics():
    """Module-scoped async client for analytics tests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class TestAnalyticsOverview:
    """Test the /analytics/overview endpoint with various scenarios"""
    
    @pytest.mark.asyncio
    async def test_get_analytics_overview_success(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict,
        shared_analytics_data: dict
    ):
        """Test successful analytics overview retrieval"""
        response = await async_client_for_analytics.get(
            "/analytics/overview",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1
        assert "data" in data
        assert "message" in data
        
        overview_data = data["data"]
        assert "summary" in overview_data
        assert "category_breakdown" in overview_data
        assert "spending_trends" in overview_data
        assert "top_tags" in overview_data
        assert "period_comparison" in overview_data
        
        # Verify financial summary contains expected fields
        summary = overview_data["summary"]
        assert "total_income" in summary
        assert "total_expense" in summary
        assert "net_income" in summary
        assert "avg_daily_expense" in summary
        
        # Verify we have meaningful data (not empty)
        assert summary["total_income"] > 0
        assert summary["total_expense"] > 0
        assert len(overview_data["category_breakdown"]) > 0

    @pytest.mark.asyncio
    async def test_analytics_overview_with_date_range(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test analytics overview with date range filtering"""
        params = {
            "start_date": "2024-12-01T00:00:00",
            "end_date": "2024-12-15T23:59:59",
            "period": "daily"
        }
        
        response = await async_client_for_analytics.get(
            "/analytics/overview",
            headers=auth_headers,
            params=params
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1
        
        # Should have data but potentially less than full range
        overview_data = data["data"]
        assert overview_data["summary"]["total_income"] >= 0
        assert overview_data["summary"]["total_expense"] >= 0

    @pytest.mark.asyncio  
    async def test_analytics_overview_by_transaction_type(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test analytics overview filtered by transaction type"""
        # Test expense only
        response = await async_client_for_analytics.get(
            "/analytics/overview",
            headers=auth_headers,
            params={"transaction_type": "expense"}
        )
        
        assert response.status_code == 200
        data = response.json()
        summary = data["data"]["summary"]
        
        # When filtered by expense, income should be 0
        assert summary["total_income"] == 0
        assert summary["total_expense"] > 0

    @pytest.mark.asyncio
    async def test_analytics_overview_unauthorized(
        self, 
        async_client_for_analytics: AsyncClient
    ):
        """Test analytics overview without authorization"""
        response = await async_client_for_analytics.get("/analytics/overview")
        assert response.status_code == 401

class TestCategoryBreakdown:
    """Test the /analytics/category-breakdown endpoint"""
    
    @pytest.mark.asyncio
    async def test_category_breakdown_success(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful category breakdown retrieval"""
        response = await async_client_for_analytics.get(
            "/analytics/category-breakdown",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1
        assert isinstance(data["data"], list)
        
        # Should have multiple categories
        categories = data["data"]
        assert len(categories) > 0
        
        # Check structure of first category
        if categories:
            first_category = categories[0]
            assert "category_id" in first_category
            assert "category_name" in first_category  
            assert "total_amount" in first_category
            assert "transaction_count" in first_category
            assert "percentage" in first_category
            assert "subcategories" in first_category
            
            # Verify subcategories structure
            if first_category["subcategories"]:
                first_subcat = first_category["subcategories"][0]
                assert "subcategory_id" in first_subcat
                assert "total_amount" in first_subcat
                assert "transaction_count" in first_subcat
                assert "percentage" in first_subcat

    @pytest.mark.asyncio
    async def test_category_breakdown_by_expense_type(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test category breakdown filtered by expense type"""
        response = await async_client_for_analytics.get(
            "/analytics/category-breakdown",
            headers=auth_headers,
            params={"transaction_type": "expense"}
        )
        
        assert response.status_code == 200
        data = response.json()
        categories = data["data"]
        
        # Should have expense categories but no income category
        category_ids = [cat["category_id"] for cat in categories]
        assert "income" not in category_ids
        
        # Should have typical expense categories from test data
        assert len(categories) > 0

class TestSpendingTrends:
    """Test the /analytics/spending-trends endpoint"""
    
    @pytest.mark.asyncio
    async def test_spending_trends_daily(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test daily spending trends"""
        response = await async_client_for_analytics.get(
            "/analytics/spending-trends",
            headers=auth_headers,
            params={"period": "daily"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1
        assert isinstance(data["data"], list)
        
        trends = data["data"]
        assert len(trends) > 0
        
        # Check structure
        first_trend = trends[0]
        assert "date" in first_trend
        assert "amount" in first_trend
        assert "transaction_count" in first_trend
        
        # Dates should be in YYYY-MM-DD format for daily
        assert len(first_trend["date"]) == 10  # YYYY-MM-DD

    @pytest.mark.asyncio
    async def test_spending_trends_monthly(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test monthly spending trends"""
        response = await async_client_for_analytics.get(
            "/analytics/spending-trends",
            headers=auth_headers,
            params={"period": "monthly"}
        )
        
        assert response.status_code == 200
        data = response.json()
        trends = data["data"]
        
        # Should have December 2024 data
        assert len(trends) > 0
        
        # Monthly dates should be in YYYY-MM format
        first_trend = trends[0]
        assert len(first_trend["date"]) == 7  # YYYY-MM

    @pytest.mark.asyncio
    async def test_spending_trends_with_category_filter(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test spending trends filtered by category"""
        response = await async_client_for_analytics.get(
            "/analytics/spending-trends",
            headers=auth_headers,
            params={"category_id": "food_dining", "period": "daily"}
        )
        
        assert response.status_code == 200
        data = response.json()
        trends = data["data"]
        
        # Should have food dining trends
        assert len(trends) > 0
        
        # Verify amounts are positive (food expenses exist)
        total_amount = sum(trend["amount"] for trend in trends)
        assert total_amount > 0

class TestFinancialSummary:
    """Test the /analytics/financial-summary endpoint"""
    
    @pytest.mark.asyncio
    async def test_financial_summary_success(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful financial summary retrieval"""
        response = await async_client_for_analytics.get(
            "/analytics/financial-summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1
        
        summary = data["data"]
        assert "total_income" in summary
        assert "total_expense" in summary
        assert "net_income" in summary
        assert "avg_daily_expense" in summary
        assert "largest_expense" in summary
        assert "most_frequent_category" in summary
        
        # Verify we have meaningful financial data
        assert summary["total_income"] > 0
        assert summary["total_expense"] > 0
        assert summary["net_income"] == summary["total_income"] - summary["total_expense"]
        
        # Largest expense should have transaction details
        if summary["largest_expense"]:
            largest = summary["largest_expense"]
            assert "id" in largest
            assert "amount" in largest
            assert "description" in largest

    @pytest.mark.asyncio
    async def test_financial_summary_with_date_range(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test financial summary with date filtering"""
        response = await async_client_for_analytics.get(
            "/analytics/financial-summary",
            headers=auth_headers,
            params={
                "start_date": "2024-12-01T00:00:00",
                "end_date": "2024-12-10T23:59:59"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        summary = data["data"]
        
        # Should have partial data from the date range
        assert summary["total_income"] >= 0
        assert summary["total_expense"] >= 0

class TestTagAnalytics:
    """Test the /analytics/tag-analytics endpoint"""
    
    @pytest.mark.asyncio
    async def test_tag_analytics_success(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful tag analytics retrieval"""
        response = await async_client_for_analytics.get(
            "/analytics/tag-analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1
        assert isinstance(data["data"], list)
        
        tags = data["data"]
        assert len(tags) > 0
        
        # Check structure of tag analytics
        first_tag = tags[0]
        assert "tag" in first_tag
        assert "total_amount" in first_tag
        assert "transaction_count" in first_tag
        assert "avg_amount" in first_tag
        
        # Should be sorted by total amount (highest first)
        if len(tags) > 1:
            assert tags[0]["total_amount"] >= tags[1]["total_amount"]

    @pytest.mark.asyncio
    async def test_tag_analytics_with_date_range(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test tag analytics with date filtering"""
        response = await async_client_for_analytics.get(
            "/analytics/tag-analytics",
            headers=auth_headers,
            params={
                "start_date": "2024-12-01T00:00:00",
                "end_date": "2024-12-31T23:59:59"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        tags = data["data"]
        
        # Should have tag data from December
        assert len(tags) > 0
        
        # Verify we have expected tags from test data
        tag_names = [tag["tag"] for tag in tags]
        expected_tags = ["monthly", "salary", "rent", "coffee", "investment"]
        
        # At least some expected tags should be present
        found_tags = [tag for tag in expected_tags if tag in tag_names]
        assert len(found_tags) > 0

class TestAnalyticsValidation:
    """Test analytics endpoints validation and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test analytics with invalid date format"""
        response = await async_client_for_analytics.get(
            "/analytics/overview",
            headers=auth_headers,
            params={"start_date": "invalid-date"}
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_period_value(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test analytics with invalid period value"""
        response = await async_client_for_analytics.get(
            "/analytics/spending-trends",
            headers=auth_headers,
            params={"period": "invalid_period"}
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_future_date_range(
        self, 
        async_client_for_analytics: AsyncClient, 
        auth_headers: dict
    ):
        """Test analytics with future date range (should return empty results)"""
        response = await async_client_for_analytics.get(
            "/analytics/overview",
            headers=auth_headers,
            params={
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-12-31T23:59:59"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        summary = data["data"]["summary"]
        
        # Should have zero amounts for future dates
        assert summary["total_income"] == 0
        assert summary["total_expense"] == 0
        assert summary["net_income"] == 0
