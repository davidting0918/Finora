import pytest
import pytest_asyncio  # 添加這個import
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from backend.main import app
from backend.core.database import MongoAsyncClient
from backend.core.model.user import user_collection
from backend.core.model.auth import access_token_collection
from dotenv import load_dotenv
import sys
import os

# Add project root to Python module search path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv("backend/.env")

@pytest.fixture(scope="session")
def event_loop():
    """根據文章建議的 event_loop fixture 配置"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture(scope="function")  # 使用 pytest_asyncio.fixture
async def async_client():
    """根據文章建議使用 async with 語法"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="function")  # 使用 pytest_asyncio.fixture
async def db_client():
    """數據庫客戶端 fixture，包含測試後清理"""
    client = MongoAsyncClient(test_mode=True)
    yield client
    await cleanup_test_db(client)
    await client.close()

async def cleanup_test_db(db_client):
    try:
        await db_client.delete_many(user_collection, {})
        await db_client.delete_many(access_token_collection, {})
        print(f"Successfully cleaned test database: {db_client.db_name}")
    except Exception as e:
        print(f"Error cleaning test database: {e}")

@pytest.fixture(scope="function")
def sample_user_data():
    return {
        "user1": {
            "email": "test1@example.com",
            "name": "test1",
            "pwd": "TestPass1!"  # 符合強密碼規則
        },
        "user2": {
            "email": "test2@example.com", 
            "name": "test2",
            "pwd": "TestPass2@"  # 符合強密碼規則
        }
    }
