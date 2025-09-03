import pytest
from httpx import AsyncClient
from fastapi import status

async def get_analytics_overview(async_client: AsyncClient, headers: dict, params: dict = None):
    """Helper function to get analytics overview"""
    response = await async_client.get("/analytics/overview", headers=headers, params=params)
    return response.json(), response.status_code


class TestAnalyticsEndpoints:
    @pytest.mark.asyncio
    async def test_get_analytics_overview(self, async_client: AsyncClient, session_auth_headers, session_transaction_list):
        """Test getting analytics overview"""
        response_data, status_code = await get_analytics_overview(
            async_client, session_auth_headers
        )
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Analytics overview fetched successfully"
        assert response_data["data"] is not None

    @pytest.mark.asyncio
    async def test_get_analytics_overview_with_params(self, async_client: AsyncClient, session_auth_headers, session_transaction_list):
        """Test getting analytics overview with params"""
        response_data, status_code = await get_analytics_overview(
            async_client, session_auth_headers, params={"start_date": "2024-01-01", "end_date": "2024-01-31", "period": "monthly", "transaction_type": "expense", "category_id": "food_dining"}
        )
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Analytics overview fetched successfully"
        assert response_data["data"] is not None