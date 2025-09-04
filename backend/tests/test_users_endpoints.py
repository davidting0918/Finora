import pytest
from fastapi import status
from httpx import AsyncClient

from backend.core.model.user import user_collection


# Helper functions to reduce code duplication
async def create_user(async_client: AsyncClient, user_data: dict):
    """Helper function to create a user"""
    response = await async_client.post("/user/create", json=user_data)
    return response.json(), response.status_code


async def login_user(async_client: AsyncClient, email: str, password: str):
    """Helper function to login with email"""
    response = await async_client.post("/auth/email/login", json={"email": email, "pwd": password})
    return response.json(), response.status_code


async def get_user_profile(async_client: AsyncClient, access_token: str):
    """Helper function to get user profile"""
    response = await async_client.get("/user/me", headers={"Authorization": f"Bearer {access_token}"})
    return response.json(), response.status_code


def assert_successful_user_creation(response_data: dict, expected_user: dict):
    """Standardized assertions for user creation"""
    assert response_data["status"] == 1
    assert response_data["message"] == "User registered successfully"
    assert "data" in response_data
    assert response_data["data"]["email"] == expected_user["email"]
    assert response_data["data"]["name"] == expected_user["name"]
    assert "id" in response_data["data"]
    assert response_data["data"]["is_active"] is True


class TestUserCreation:
    """Test user creation functionality"""

    @pytest.mark.asyncio
    async def test_create_user_successfully(self, async_client: AsyncClient, test_user_data, db_client):
        """Test creating a user with valid data"""
        user_data = test_user_data["user1"]

        response_data, status_code = await create_user(async_client, user_data)

        assert status_code == status.HTTP_200_OK
        assert_successful_user_creation(response_data, user_data)

        # Verify in database
        db_user = await db_client.find_one(user_collection, {"email": user_data["email"]})
        assert db_user is not None
        assert db_user["email"] == user_data["email"]

    @pytest.mark.asyncio
    async def test_create_multiple_users(self, async_client: AsyncClient, test_user_data, db_client):
        """Test creating multiple users from test data"""
        # Create first user
        user1 = test_user_data["user1"]
        data1, status1 = await create_user(async_client, user1)
        assert status1 == status.HTTP_200_OK
        assert_successful_user_creation(data1, user1)

        # Create second user
        user2 = test_user_data["user2"]
        data2, status2 = await create_user(async_client, user2)
        assert status2 == status.HTTP_200_OK
        assert_successful_user_creation(data2, user2)

        # Verify unique IDs
        assert data1["data"]["id"] != data2["data"]["id"]

    @pytest.mark.asyncio
    async def test_duplicate_email_fails(self, async_client: AsyncClient, test_user_data):
        """Test that duplicate email creation fails"""
        user = test_user_data["user1"]

        # Create first user
        response_data, status_code = await create_user(async_client, user)
        assert status_code == status.HTTP_200_OK

        # Try to create duplicate
        response_data, status_code = await create_user(async_client, user)
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "User already exists" in response_data["detail"]

    @pytest.mark.asyncio
    async def test_password_validation(self, async_client: AsyncClient, test_user_data):
        """Test password validation rules"""
        weak_passwords = ["123456", "password", "Password", "Password123"]

        for i, weak_pwd in enumerate(weak_passwords):
            user_data = test_user_data["weak_pwd_user"]
            user_data["pwd"] = weak_pwd
            response_data, status_code = await create_user(async_client, user_data)
            assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserAuthentication:
    """Test user authentication functionality"""

    @pytest.mark.asyncio
    async def test_login_with_email(self, async_client: AsyncClient, test_user_data, db_client):
        """Test email login after user creation"""
        user = test_user_data["user1"]

        # Create user
        create_data, create_status = await create_user(async_client, user)
        assert create_status == status.HTTP_200_OK

        # Login
        login_data, login_status = await login_user(async_client, user["email"], user["pwd"])
        assert login_status == status.HTTP_200_OK
        assert "access_token" in login_data
        assert "token_type" in login_data
        assert login_data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_with_oauth2_form(self, async_client: AsyncClient, test_user_data):
        """Test OAuth2 form login after user creation"""
        user = test_user_data["user2"]

        # Create user
        await create_user(async_client, user)

        # Login with OAuth2 form
        response = await async_client.post(
            "/auth/access_token",
            data={"username": user["name"], "password": user["pwd"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_200_OK
        login_data = response.json()
        assert "access_token" in login_data and login_data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, async_client: AsyncClient, test_user_data):
        """Test login with wrong password fails"""
        user = test_user_data["user1"]
        await create_user(async_client, user)

        login_data, login_status = await login_user(async_client, user["email"], "WrongPassword123!")
        assert login_status == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in login_data["detail"]


class TestUserProfile:
    """Test user profile functionality"""

    @pytest.mark.asyncio
    async def test_protected_endpoint_requires_auth(self, async_client: AsyncClient, test_user_data):
        """Test protected endpoint authentication"""
        # Test unauthenticated access
        response = await async_client.get("/user/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Create user and login
        user = test_user_data["user1"]
        await create_user(async_client, user)
        login_data, _ = await login_user(async_client, user["email"], user["pwd"])

        # Test authenticated access
        profile_data, profile_status = await get_user_profile(async_client, login_data["access_token"])
        assert profile_status == status.HTTP_200_OK
        assert profile_data["data"]["email"] == user["email"]

    @pytest.mark.asyncio
    async def test_complete_user_flow(self, async_client: AsyncClient, test_user_data, db_client):
        """Test complete user flow: create -> login -> profile"""
        user = test_user_data["user1"]

        # Create user
        create_data, create_status = await create_user(async_client, user)
        assert create_status == status.HTTP_200_OK
        user_id = create_data["data"]["id"]

        # Login
        login_data, login_status = await login_user(async_client, user["email"], user["pwd"])
        assert login_status == status.HTTP_200_OK

        # Get profile
        profile_data, profile_status = await get_user_profile(async_client, login_data["access_token"])
        assert profile_status == status.HTTP_200_OK
        assert profile_data["data"]["id"] == user_id
        assert profile_data["data"]["email"] == user["email"]

        # Verify in database
        db_user = await db_client.find_one(user_collection, {"id": user_id})
        assert db_user is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
