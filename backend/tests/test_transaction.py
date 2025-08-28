import pytest
from httpx import AsyncClient
from fastapi import status

class TestTransaction:
    
    @pytest.mark.asyncio
    async def test_create_transaction(self, async_client: AsyncClient, sample_user_data, sample_transaction_data, db_client):
        # create user
        response = await async_client.post(
            "/user/create",
            json=sample_user_data["user1"]
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "User registered successfully"

        # get access token
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

        # create transaction
        response = await async_client.post(
            "/transaction/create",
            json=sample_transaction_data["transaction1"],
            headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction created successfully"
