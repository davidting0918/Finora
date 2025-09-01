"""
Analytics endpoints tests using shared module-scoped fixtures from conftest.py.
This demonstrates the simplified approach using centralized test fixtures.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime as dt

class TestAnalyticsOverview:
    """Test the /analytics/overview endpoint with various scenarios"""
    
    @pytest.mark.asyncio
    async def test_get_analytics_overview_success(
        self, 
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict,
        analytics_test_data: dict
    ):
        """Test successful analytics overview retrieval"""
        response = await module_async_client.get(
            "/analytics/overview",
            headers=comprehensive_auth_headers
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test analytics overview with date range filtering"""
        params = {
            "start_date": "2024-12-01T00:00:00",
            "end_date": "2024-12-15T23:59:59",
            "period": "daily"
        }
        
        response = await module_async_client.get(
            "/analytics/overview",
            headers=comprehensive_auth_headers,
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test analytics overview filtered by transaction type"""
        # Test expense only
        response = await module_async_client.get(
            "/analytics/overview",
            headers=comprehensive_auth_headers,
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
        module_async_client: AsyncClient
    ):
        """Test analytics overview without authorization"""
        response = await module_async_client.get("/analytics/overview")
        assert response.status_code == 401

class TestCategoryBreakdown:
    """Test the /analytics/category-breakdown endpoint"""
    
    @pytest.mark.asyncio
    async def test_category_breakdown_success(
        self, 
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test successful category breakdown retrieval"""
        response = await module_async_client.get(
            "/analytics/category-breakdown",
            headers=comprehensive_auth_headers
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test category breakdown filtered by expense type"""
        response = await module_async_client.get(
            "/analytics/category-breakdown",
            headers=comprehensive_auth_headers,
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test daily spending trends"""
        response = await module_async_client.get(
            "/analytics/spending-trends",
            headers=comprehensive_auth_headers,
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test monthly spending trends"""
        response = await module_async_client.get(
            "/analytics/spending-trends",
            headers=comprehensive_auth_headers,
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test spending trends filtered by category"""
        response = await module_async_client.get(
            "/analytics/spending-trends",
            headers=comprehensive_auth_headers,
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test successful financial summary retrieval"""
        response = await module_async_client.get(
            "/analytics/financial-summary",
            headers=comprehensive_auth_headers
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test financial summary with date filtering"""
        response = await module_async_client.get(
            "/analytics/financial-summary",
            headers=comprehensive_auth_headers,
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test successful tag analytics retrieval"""
        response = await module_async_client.get(
            "/analytics/tag-analytics",
            headers=comprehensive_auth_headers
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
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test tag analytics with date filtering"""
        response = await module_async_client.get(
            "/analytics/tag-analytics",
            headers=comprehensive_auth_headers,
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
        expected_tags = ["monthly", "salary", "rent", "coffee", "business"]
        
        # At least some expected tags should be present
        found_tags = [tag for tag in expected_tags if tag in tag_names]
        assert len(found_tags) > 0

class TestAnalyticsValidation:
    """Test analytics endpoints validation and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(
        self, 
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test analytics with invalid date format"""
        response = await module_async_client.get(
            "/analytics/overview",
            headers=comprehensive_auth_headers,
            params={"start_date": "invalid-date"}
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_period_value(
        self, 
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test analytics with invalid period value"""
        response = await module_async_client.get(
            "/analytics/spending-trends",
            headers=comprehensive_auth_headers,
            params={"period": "invalid_period"}
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_future_date_range(
        self, 
        module_async_client: AsyncClient, 
        comprehensive_auth_headers: dict
    ):
        """Test analytics with future date range (should return empty results)"""
        response = await module_async_client.get(
            "/analytics/overview",
            headers=comprehensive_auth_headers,
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