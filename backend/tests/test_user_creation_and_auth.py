import pytest
from httpx import AsyncClient
from fastapi import status
from backend.core.model.user import user_collection


class TestUserCreationAndAuth:
    
    @pytest.mark.asyncio
    async def test_create_two_users_successfully(self, async_client: AsyncClient, sample_user_data, db_client):
        
        response1 = await async_client.post(
            "/user/create",
            json=sample_user_data["user1"]
        )
        
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert data1["status"] == 1
        assert data1["message"] == "User registered successfully"
        assert "data" in data1
        assert data1["data"]["email"] == sample_user_data["user1"]["email"]
        assert data1["data"]["name"] == sample_user_data["user1"]["name"]
        assert "id" in data1["data"]
        assert data1["data"]["is_active"] is True
        
        # Create second user
        response2 = await async_client.post(
            "/user/create", 
            json=sample_user_data["user2"]
        )
        
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert data2["status"] == 1
        assert data2["message"] == "User registered successfully"
        assert data2["data"]["email"] == sample_user_data["user2"]["email"]
        assert data2["data"]["name"] == sample_user_data["user2"]["name"]
        
        # Verify that the two users have different IDs
        assert data1["data"]["id"] != data2["data"]["id"]
        
        # Verify that the users are stored in the database
        user1_in_db = await db_client.find_one(user_collection, {"email": sample_user_data["user1"]["email"]})
        user2_in_db = await db_client.find_one(user_collection, {"email": sample_user_data["user2"]["email"]})
        
        assert user1_in_db is not None
        assert user2_in_db is not None
        assert user1_in_db["name"] == sample_user_data["user1"]["name"]
        assert user2_in_db["name"] == sample_user_data["user2"]["name"]
        
        print(f"✅ Successfully created two users:")
        print(f"   User 1: {data1['data']['name']} ({data1['data']['email']})")
        print(f"   User 2: {data2['data']['name']} ({data2['data']['email']})")

    @pytest.mark.asyncio
    async def test_duplicate_email_creation_fails(self, async_client: AsyncClient, sample_user_data):
        
        response1 = await async_client.post(
            "/user/create",
            json=sample_user_data["user1"]
        )
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = await async_client.post(
            "/user/create",
            json=sample_user_data["user1"]
        )
        
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "User already exists" in response2.json()["detail"]
        
        print("✅ Duplicate email registration test passed, correctly returned 400 error")

    @pytest.mark.asyncio
    async def test_user_login_with_email_after_creation(self, async_client: AsyncClient, sample_user_data):
        
        create_response = await async_client.post(
            "/user/create",
            json=sample_user_data["user1"]
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        login_response = await async_client.post(
            "/auth/email/login",
            json={
                "email": sample_user_data["user1"]["email"],
                "pwd": sample_user_data["user1"]["pwd"]
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        
        assert "access_token" in login_data
        assert "token_type" in login_data
        assert login_data["token_type"] == "bearer"
        assert "user" in login_data
        assert login_data["user"]["email"] == sample_user_data["user1"]["email"]
        assert login_data["user"]["name"] == sample_user_data["user1"]["name"]
        
        print(f"✅ Email login test passed")
        print(f"   User: {login_data['user']['name']}")
        print(f"   Token type: {login_data['token_type']}")

    @pytest.mark.asyncio
    async def test_user_login_with_oauth2_form_after_creation(self, async_client: AsyncClient, sample_user_data):
        
        create_response = await async_client.post(
            "/user/create",
            json=sample_user_data["user2"]
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        login_response = await async_client.post(
            "/auth/access_token",
            data={
                "username": sample_user_data["user2"]["name"],  # OAuth2 使用 username
                "password": sample_user_data["user2"]["pwd"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        
        assert "access_token" in login_data
        assert "token_type" in login_data
        assert login_data["token_type"] == "bearer"
        
        print(f"✅ OAuth2 form 登入測試通過")

    @pytest.mark.asyncio
    async def test_login_with_wrong_credentials_fails(self, async_client: AsyncClient, sample_user_data):
        
        await async_client.post("/user/create", json=sample_user_data["user1"])
        
        wrong_login_response = await async_client.post(
            "/auth/email/login",
            json={
                "email": sample_user_data["user1"]["email"],
                "pwd": "WrongPassword123!"
            }
        )
        
        assert wrong_login_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in wrong_login_response.json()["detail"]
        
        print("✅ Wrong credentials login test passed, correctly returned 401 error")

    @pytest.mark.asyncio
    async def test_protected_endpoint_requires_authentication(self, async_client: AsyncClient, sample_user_data):
        
        response = await async_client.get("/user/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        await async_client.post("/user/create", json=sample_user_data["user1"])
        
        login_response = await async_client.post(
            "/auth/email/login",
            json={
                "email": sample_user_data["user1"]["email"],
                "pwd": sample_user_data["user1"]["pwd"]
            }
        )
        
        access_token = login_response.json()["access_token"]
        
        protected_response = await async_client.get(
            "/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert protected_response.status_code == status.HTTP_200_OK
        user_data = protected_response.json()
        
        assert user_data["status"] == 1
        assert user_data["data"]["email"] == sample_user_data["user1"]["email"]
        assert user_data["data"]["name"] == sample_user_data["user1"]["name"]
        
        print("✅ Protected endpoint authentication test passed")

    @pytest.mark.asyncio
    async def test_password_validation_enforced(self, async_client: AsyncClient):
        
        weak_passwords = [
            "123456",
            "password",
            "Password",
            "Password123",
        ]
        
        for weak_pwd in weak_passwords:
            response = await async_client.post(
                "/user/create",
                json={
                    "email": f"test_{weak_pwd}@example.com",
                    "name": "測試用戶",
                    "pwd": weak_pwd
                }
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        print("✅ Password validation rule test passed, weak passwords correctly rejected")

    @pytest.mark.asyncio
    async def test_complete_user_flow(self, async_client: AsyncClient, sample_user_data, db_client):
        
        user_data = sample_user_data["user1"]
        
        create_response = await async_client.post("/user/create", json=user_data)
        assert create_response.status_code == status.HTTP_200_OK
        
        created_user = create_response.json()["data"]
        user_id = created_user["id"]
        
        login_response = await async_client.post(
            "/auth/email/login",
            json={"email": user_data["email"], "pwd": user_data["pwd"]}
        )
        assert login_response.status_code == status.HTTP_200_OK
        
        access_token = login_response.json()["access_token"]
        
        me_response = await async_client.get(
            "/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == status.HTTP_200_OK
        
        user_info = me_response.json()["data"]
        
        assert user_info["id"] == user_id
        assert user_info["email"] == user_data["email"]
        assert user_info["name"] == user_data["name"]
        assert user_info["is_active"] is True
        
        db_user = await db_client.find_one(user_collection, {"id": user_id})
        assert db_user is not None
        assert db_user["email"] == user_data["email"]
        
        print("🎉 Complete user flow test passed")
        print(f"   User ID: {user_id}")
        print(f"   Email: {user_info['email']}")
        print(f"   Name: {user_info['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
