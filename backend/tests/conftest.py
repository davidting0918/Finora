import os
os.environ["PYTEST_RUNNING"] = "1"

import pytest
import pytest_asyncio
import asyncio
import atexit
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
def sample_user_data():
    return {
        "user1": {
            "email": "test1@example.com",
            "name": "test1",
            "pwd": "TestPass1!"
        },
        "user2": {
            "email": "test2@example.com", 
            "name": "test2",
            "pwd": "TestPass2@"
        }
    }

@pytest.fixture(scope="function")
def sample_transaction_data():
    from datetime import datetime
    
    return {
        "transaction1": {
            "type": "expense",
            "currency": "TWD",
            "amount": 1000,
            "transaction_date": "2025-08-01",
            "category_id": "food_dining",
            "subcategory_id": "breakfast",
            "description": "Breakfast",
            "notes": "7-11",
            "tags": [
              "test tag"
            ]
        },
        "old_transaction": {
            "type": "expense",
            "currency": "TWD",
            "amount": 1000,
            "transaction_date": "2025-08-01",
            "category_id": "food_dining",
            "subcategory_id": "breakfast",
        },
        "new_transaction": {
            "type": "expense",
            "currency": "TWD",
            "amount": 2000,
            "transaction_date": "2025-08-02",
            "category_id": "shopping",
            "subcategory_id": "clothing",
            "description": "ZARA",
        },
        "transaction_list": [
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 250,
                "transaction_date": "2025-01-15",
                "category_id": "food_dining",
                "subcategory_id": "breakfast",
                "description": "Morning coffee",
                "notes": "Starbucks",
                "tags": ["coffee", "morning"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 1200,
                "transaction_date": "2025-01-16",
                "category_id": "food_dining",
                "subcategory_id": "lunch",
                "description": "Business lunch",
                "notes": "Din Tai Fung",
                "tags": ["business", "restaurant"]
            },
            {
                "type": "income",
                "currency": "TWD",
                "amount": 50000,
                "transaction_date": "2025-01-01",
                "category_id": "income",
                "subcategory_id": "income_other",
                "description": "Monthly salary",
                "notes": "Company A",
                "tags": ["salary", "monthly"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 3500,
                "transaction_date": "2025-01-12",
                "category_id": "shopping",
                "subcategory_id": "clothing",
                "description": "Winter jacket",
                "notes": "Uniqlo",
                "tags": ["winter", "clothing"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 120,
                "transaction_date": "2025-01-18",
                "category_id": "transportation",
                "subcategory_id": "bus",
                "description": "Daily commute",
                "notes": "MRT card top-up",
                "tags": ["commute", "transport"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 800,
                "transaction_date": "2025-01-20",
                "category_id": "entertainment",
                "subcategory_id": "movie",
                "description": "Movie night",
                "notes": "威秀影城",
                "tags": ["movie", "entertainment"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 15000,
                "transaction_date": "2025-01-05",
                "category_id": "living",
                "subcategory_id": "rent",
                "description": "Monthly rent",
                "notes": "Apartment rent",
                "tags": ["rent", "monthly"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 2500,
                "transaction_date": "2025-01-10",
                "category_id": "education",
                "subcategory_id": "software",
                "description": "Online course",
                "notes": "Udemy Python course",
                "tags": ["learning", "programming"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 500,
                "transaction_date": "2025-01-22",
                "category_id": "health",
                "subcategory_id": "medical",
                "description": "Dental checkup",
                "notes": "Annual cleaning",
                "tags": ["health", "dental"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 10000,
                "transaction_date": "2025-01-25",
                "category_id": "investment",
                "subcategory_id": "stock",
                "description": "Stock purchase",
                "notes": "TSMC shares",
                "tags": ["investment", "stock"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 450,
                "transaction_date": "2025-01-14",
                "category_id": "food_dining",
                "subcategory_id": "dinner",
                "description": "Family dinner",
                "notes": "Hot pot restaurant",
                "tags": ["family", "dinner"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 25000,
                "transaction_date": "2025-01-08",
                "category_id": "shopping",
                "subcategory_id": "electronics",
                "description": "New laptop",
                "notes": "MacBook Pro",
                "tags": ["laptop", "work"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 350,
                "transaction_date": "2025-01-19",
                "category_id": "transportation",
                "subcategory_id": "taxi",
                "description": "Taxi to airport",
                "notes": "Uber",
                "tags": ["airport", "travel"]
            },
            {
                "type": "income",
                "currency": "TWD",
                "amount": 5000,
                "transaction_date": "2025-01-15",
                "category_id": "income",
                "subcategory_id": "income_other",
                "description": "Freelance project",
                "notes": "Web development",
                "tags": ["freelance", "bonus"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 2200,
                "transaction_date": "2025-01-09",
                "category_id": "shopping",
                "subcategory_id": "home_goods",
                "description": "Kitchen appliances",
                "notes": "IKEA",
                "tags": ["home", "kitchen"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 1500,
                "transaction_date": "2025-01-13",
                "category_id": "health",
                "subcategory_id": "insurance",
                "description": "Health insurance",
                "notes": "Monthly premium",
                "tags": ["insurance", "health"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 300,
                "transaction_date": "2025-01-23",
                "category_id": "transportation",
                "subcategory_id": "parking",
                "description": "Parking fee",
                "notes": "Taipei 101",
                "tags": ["parking", "city"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 15000,
                "transaction_date": "2025-01-27",
                "category_id": "travel",
                "subcategory_id": "flight",
                "description": "Flight to Japan",
                "notes": "EVA Air",
                "tags": ["travel", "international"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 950,
                "transaction_date": "2025-01-07",
                "category_id": "entertainment",
                "subcategory_id": "game",
                "description": "Gaming subscription",
                "notes": "PlayStation Plus",
                "tags": ["gaming", "subscription"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 1000,
                "transaction_date": "2025-01-01",
                "category_id": "food_dining",
                "subcategory_id": "food_dining_other",
                "description": "Other food and dining",
                "notes": "Other food and dining",
            }
        ]
    }