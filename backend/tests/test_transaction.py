import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.fixture
async def user_and_token(async_client: AsyncClient, sample_user_data, init_category_for_test):

    response = await async_client.post(
        "/user/create",
        json=sample_user_data["user1"]
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == 1
    assert data["message"] == "User registered successfully"

    response = await async_client.post(
        "/auth/email/login",
        json={
            "email": sample_user_data["user1"]["email"],
            "pwd": sample_user_data["user1"]["pwd"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data

    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }
    return headers, sample_user_data["user1"]

class TestTransaction:
    @pytest.mark.asyncio
    async def test_create_transaction(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = await user_and_token
        response = await async_client.post(
            "/transaction/create",
            json=sample_transaction_data["transaction1"],
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction created successfully"

    @pytest.mark.asyncio
    async def test_get_transaction(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = await user_and_token

        response = await async_client.post(
            "/transaction/create",
            json=sample_transaction_data["transaction1"],
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction created successfully"
