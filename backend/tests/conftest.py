import os
os.environ["PYTEST_RUNNING"] = "1"

import pytest
import pytest_asyncio
import asyncio
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient
from backend.main import app
from backend.core.database import MongoAsyncClient
from backend.core.initializer import init_category
from backend.core.model.user import user_collection
from backend.core.model.auth import access_token_collection
from backend.core.model.transaction import transaction_collection
from backend.core.model.transaction import category_collection
from backend.core.model.transaction import subcategory_collection

# Global variable to track session cleanup
_session_db_client = None

@pytest.fixture(scope="session")
def event_loop():
    """Create and manage event loop for the entire test session"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Ensure proper cleanup
    try:
        # Cancel all running tasks
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

@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def db_client():
    client = MongoAsyncClient(test_mode=True)
    try:
        yield client
        await cleanup_test_db(client)
    finally:
        await safe_close_client(client)

# Session-level cleanup with proper resource management
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_session():
    """Clean database at the start of test session"""
    global _session_db_client
    
    _session_db_client = MongoAsyncClient(test_mode=True)
    try:
        await cleanup_test_db(_session_db_client)
        yield
        await cleanup_test_db(_session_db_client)
    except Exception as e:
        print(f"Error during session setup/cleanup: {e}")
    finally:
        if _session_db_client:
            await safe_close_client(_session_db_client)
            _session_db_client = None

# Function-level cleanup with shared client
@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_after_test():
    """Automatically clean database after every test"""
    yield  # Let the test run first
    
    # Cleanup after test completes using session client if available
    if _session_db_client:
        try:
            await cleanup_test_db(_session_db_client)
        except Exception as e:
            print(f"Warning: Cleanup after test failed: {e}")
    else:
        # Fallback: create temporary client
        temp_client = MongoAsyncClient(test_mode=True)
        try:
            await cleanup_test_db(temp_client)
        except Exception as e:
            print(f"Warning: Fallback cleanup failed: {e}")
        finally:
            await safe_close_client(temp_client)

async def safe_close_client(client):
    """Safely close database client with error handling"""
    try:
        if client and hasattr(client, 'close'):
            await client.close()
    except Exception as e:
        print(f"Warning: Database client close error: {e}")

async def cleanup_test_db(db_client):
    """Clean test database with error handling"""
    try:
        if not db_client:
            return
        await db_client.delete_many(user_collection, {})
        await db_client.delete_many(access_token_collection, {})
        await db_client.delete_many(transaction_collection, {})
        await db_client.delete_many(category_collection, {})
        await db_client.delete_many(subcategory_collection, {})
    except Exception as e:
        print(f"Error cleaning test database: {e}")

@pytest_asyncio.fixture(scope="function")
async def init_category_for_test():
    """Initialize categories for testing"""
    try:
        await init_category()
        yield
    except Exception as e:
        print(f"Warning: Category initialization failed in tests: {e}")
        yield

@pytest.fixture(scope="function")
def test_user_data():
    path = "backend/data/test_users_data.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="function")
def test_transactions_data():
    path = "backend/data/test_transactions_data.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="function")
def test_analytics_data():
    """Load analytics test data from JSON file"""
    path = "backend/data/test_analytics_data.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

