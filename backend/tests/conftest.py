import os

os.environ["PYTEST_RUNNING"] = "1"

import asyncio
import hashlib
import json
import uuid
from datetime import datetime as dt

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

from backend.core.database import MongoAsyncClient
from backend.core.initializer import init_category
from backend.core.model.auth import APIKey, access_token_collection, api_key_collection
from backend.core.model.transaction import category_collection, subcategory_collection, transaction_collection
from backend.core.model.user import user_collection
from backend.main import app

# Simplified fixtures and database management


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for test session"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    try:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
    except Exception as e:
        print(f"Warning: Event loop cleanup error: {e}")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def async_client():
    """Session-scoped async client for better performance"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_client():
    """Database client with automatic cleanup"""
    client = MongoAsyncClient()
    try:
        # Clean before test
        await cleanup_test_db(client)
        yield client
    finally:
        # Clean after test
        await cleanup_test_db(client)
        await safe_close_client(client)


async def safe_close_client(client):
    """Safely close database client"""
    try:
        if client and hasattr(client, "close"):
            await client.close()
    except Exception as e:
        print(f"Warning: Database client close error: {e}")


async def cleanup_test_db(db_client):
    """Clean test database efficiently"""
    if not db_client:
        return
    try:
        # Clean all collections concurrently
        collections = [
            user_collection,
            access_token_collection,
            transaction_collection,
            category_collection,
            subcategory_collection,
        ]
        cleanup_tasks = [db_client.delete_many(col, {}) for col in collections]
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error cleaning test database: {e}")


@pytest_asyncio.fixture(scope="session")
async def init_category_for_test():
    """Initialize categories for testing - session scoped for better performance"""
    try:
        await init_category()
        yield
    except Exception as e:
        print(f"Warning: Category initialization failed in tests: {e}")
        yield


# Session-scoped user authentication fixture
@pytest_asyncio.fixture(scope="session")
async def test_user_with_auth(test_user_data, async_client, init_category_for_test):
    """Create test users and return auth info for the entire test session"""
    # Create user1
    user1_response = await async_client.post("/user/create", json=test_user_data["user1"])
    assert user1_response.status_code == 200, f"User1 creation failed: {user1_response.text}"

    # Login user1 and get token
    login_response = await async_client.post(
        "/auth/email/login", json={"email": test_user_data["user1"]["email"], "pwd": test_user_data["user1"]["pwd"]}
    )
    assert login_response.status_code == 200, f"User1 login failed: {login_response.text}"

    login_data = login_response.json()

    return login_data


@pytest_asyncio.fixture(scope="session")
async def session_auth_headers(test_user_with_auth):
    """Get authentication headers for the entire test session"""
    return {"Authorization": f"Bearer {test_user_with_auth['access_token']}"}


@pytest_asyncio.fixture(scope="session")
async def session_api_key_headers():
    """Get API key headers for the entire test session"""
    """Initialize test API key for testing and store into env"""
    db = MongoAsyncClient()
    try:
        existing_api_key = await db.find_one(api_key_collection, {"name": "pytest"})
        if existing_api_key:
            return {"Authorization": f"Bearer {existing_api_key['api_key']}:{existing_api_key['api_secret']}"}
        else:
            api_key = APIKey(
                name=f"pytest-{dt.now().strftime('%Y%m%d%H%M%S')}",
                api_key=str(uuid.uuid4().hex),
                api_secret=hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest(),
            )
            await db.insert_one(api_key_collection, api_key.model_dump())
        return {"Authorization": f"Bearer {api_key.api_key}:{api_key.api_secret}"}
    finally:
        await db.close()


@pytest_asyncio.fixture(scope="session")
async def session_transaction_list(async_client, session_auth_headers, test_analytics_data):
    """Create transaction list for the entire test session"""
    tx_list = test_analytics_data["transactions"]
    for tx in tx_list:
        await async_client.post("/transaction/create", json=tx, headers=session_auth_headers)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def session_clean_db():
    """Clean database before and after the `entire test session"""
    client = MongoAsyncClient()
    try:
        # Clean before test session starts
        await cleanup_test_db(client)
        yield client
    finally:
        # Clean after test session ends
        await cleanup_test_db(client)
        await safe_close_client(client)


# Test data fixtures - session scope for better performance since they're read-only
@pytest.fixture(scope="session")
def test_user_data():
    """Load user test data from JSON file (session-scoped for performance)"""
    path = "backend/data/test_users_data.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def test_transactions_data():
    """Load transaction test data from JSON file (session-scoped for performance)"""
    path = "backend/data/test_transactions_data.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def test_analytics_data():
    """Load analytics test data from JSON file (session-scoped for performance)"""
    path = "backend/data/test_analytics_data.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
