import os
os.environ["PYTEST_RUNNING"] = "1"

import pytest
import pytest_asyncio
import asyncio
import json
from typing import Dict, Any, List
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
from backend.user.service import UserService
from backend.auth.service import AuthService
from backend.transaction.service import TransactionService

# Global variable to track session cleanup
_session_db_client = None

# ==================== SESSION SCOPE FIXTURES ====================

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

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_session():
    """Clean database at the start of test session and initialize categories"""
    global _session_db_client
    
    _session_db_client = MongoAsyncClient(test_mode=True)
    try:
        await cleanup_test_db(_session_db_client)
        await init_category()
        yield
        await cleanup_test_db(_session_db_client)
    except Exception as e:
        print(f"Error during session setup/cleanup: {e}")
    finally:
        if _session_db_client:
            await safe_close_client(_session_db_client)
            _session_db_client = None

# ==================== MODULE SCOPE FIXTURES ====================

@pytest_asyncio.fixture(scope="module")
async def module_db_client():
    """Module-scoped database client that can be used across all tests in a module"""
    client = MongoAsyncClient(test_mode=True)
    try:
        yield client
    finally:
        if client:
            await safe_close_client(client)

@pytest_asyncio.fixture(scope="module")
async def module_async_client():
    """Module-scoped async HTTP client for testing endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="module")
async def module_test_users(module_db_client):
    """
    Module-scoped test users (2 users) that persist across all tests in a module.
    Creates 2 standard test users with known credentials and access tokens.
    Uses service layer for fast and reliable user creation.
    """
    # Clean database first  
    await cleanup_test_db(module_db_client)
    await init_category()
    
    user_service = UserService()
    auth_service = AuthService()
    
    # User 1 data
    user1_data = {
        "email": "user1@example.com",
        "name": "Test User 1",
        "pwd": "TestUser1Pass!"
    }
    
    # User 2 data
    user2_data = {
        "email": "user2@example.com", 
        "name": "Test User 2",
        "pwd": "TestUser2Pass!"
    }
    
    # Create user 1 using service layer (not API)
    from backend.core.model.user import CreateUserRequest
    
    user1_request = CreateUserRequest(
        email=user1_data["email"],
        name=user1_data["name"],
        pwd=user1_data["pwd"]
    )
    created_user1 = await user_service.create_user(user1_request)
    
    # Create user 2 using service layer  
    user2_request = CreateUserRequest(
        email=user2_data["email"],
        name=user2_data["name"],
        pwd=user2_data["pwd"]
    )
    created_user2 = await user_service.create_user(user2_request)
    
    # Get access tokens for both users using service layer
    token1_result = await auth_service.get_or_create_token(created_user1.id)
    token2_result = await auth_service.get_or_create_token(created_user2.id)
    
    return {
        "user1": {
            "user": created_user1,
            "user_data": user1_data,
            "access_token": token1_result["access_token"],
            "headers": {"Authorization": f"Bearer {token1_result['access_token']}"}
        },
        "user2": {
            "user": created_user2,
            "user_data": user2_data, 
            "access_token": token2_result["access_token"],
            "headers": {"Authorization": f"Bearer {token2_result['access_token']}"}
        }
    }

@pytest.fixture(scope="module")
def module_auth_headers(module_test_users):
    """Module-scoped authorization headers for API requests (user1 by default)"""
    return module_test_users["user1"]["headers"]

@pytest_asyncio.fixture(scope="module")
async def module_test_transactions(module_test_users, module_db_client):
    """
    Module-scoped test transactions that persist across tests in a module.
    Creates comprehensive transaction data for testing analytics and other features.
    """
    transaction_service = TransactionService()
    created_user = module_test_users["user1"]["user"]
    
    # Load transaction data from file if available, else use embedded data
    try:
        with open("/workspace/backend/data/test_transactions_data.json", "r", encoding="utf-8") as f:
            transactions_data = json.load(f)
    except FileNotFoundError:
        # Fallback to embedded comprehensive test data
        transactions_data = [
            {
                "type": "income",
                "currency": "TWD",
                "amount": 50000,
                "transaction_date": "2024-12-01",
                "category_id": "income",
                "subcategory_id": "income_other",
                "description": "Monthly salary",
                "notes": "Company salary",
                "tags": ["salary", "monthly"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 15000,
                "transaction_date": "2024-12-02",
                "category_id": "living",
                "subcategory_id": "rent",
                "description": "Monthly rent",
                "notes": "Apartment rent",
                "tags": ["rent", "monthly"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 1200,
                "transaction_date": "2024-12-03",
                "category_id": "food_dining",
                "subcategory_id": "lunch",
                "description": "Business lunch",
                "notes": "Restaurant meal",
                "tags": ["business", "food"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 500,
                "transaction_date": "2024-12-04",
                "category_id": "transportation",
                "subcategory_id": "taxi",
                "description": "Taxi ride",
                "notes": "Uber",
                "tags": ["transport", "taxi"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 800,
                "transaction_date": "2024-12-05",
                "category_id": "entertainment",
                "subcategory_id": "movie",
                "description": "Movie night",
                "notes": "Cinema",
                "tags": ["entertainment", "movie"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 2500,
                "transaction_date": "2024-12-06",
                "category_id": "shopping",
                "subcategory_id": "clothing",
                "description": "Winter jacket",
                "notes": "Clothing store",
                "tags": ["winter", "clothing"]
            },
            {
                "type": "income",
                "currency": "TWD",
                "amount": 5000,
                "transaction_date": "2024-12-07",
                "category_id": "income",
                "subcategory_id": "income_other",
                "description": "Freelance project",
                "notes": "Side project",
                "tags": ["freelance", "bonus"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 3500,
                "transaction_date": "2024-12-08",
                "category_id": "health",
                "subcategory_id": "medical",
                "description": "Medical checkup",
                "notes": "Annual checkup",
                "tags": ["health", "medical"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 10000,
                "transaction_date": "2024-12-09",
                "category_id": "investment",
                "subcategory_id": "stock",
                "description": "Stock investment",
                "notes": "Portfolio investment",
                "tags": ["investment", "stock"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 250,
                "transaction_date": "2024-12-10",
                "category_id": "food_dining",
                "subcategory_id": "breakfast",
                "description": "Morning coffee",
                "notes": "Coffee shop",
                "tags": ["coffee", "morning"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 1800,
                "transaction_date": "2024-12-11",
                "category_id": "food_dining",
                "subcategory_id": "dinner",
                "description": "Family dinner",
                "notes": "Japanese restaurant",
                "tags": ["family", "dinner"]
            },
            {
                "type": "expense",
                "currency": "TWD",
                "amount": 4500,
                "transaction_date": "2024-12-12",
                "category_id": "education",
                "subcategory_id": "course",
                "description": "Programming course",
                "notes": "Online learning platform",
                "tags": ["learning", "programming"]
            }
        ]
    
    # Create all test transactions
    created_transactions = []
    for transaction_data in transactions_data:
        created_transaction = await transaction_service.create_transaction(
            transaction_data,
            created_user
        )
        created_transactions.append(created_transaction)
    
    return {
        "transactions": created_transactions,
        "raw_data": transactions_data,
        "count": len(created_transactions)
    }

@pytest_asyncio.fixture(scope="module")
async def comprehensive_test_data(module_test_users, module_test_transactions):
    """
    Module-scoped comprehensive test data combining users, auth, and transactions.
    This is the main fixture that test modules should use.
    """
    return {
        "user1": module_test_users["user1"]["user"],
        "user2": module_test_users["user2"]["user"],
        "user1_data": module_test_users["user1"]["user_data"],
        "user2_data": module_test_users["user2"]["user_data"],
        "user1_headers": module_test_users["user1"]["headers"],
        "user2_headers": module_test_users["user2"]["headers"],
        "access_token": module_test_users["user1"]["access_token"],  # Default to user1
        "transactions": module_test_transactions["transactions"],
        "transactions_data": module_test_transactions["raw_data"],
        "transactions_count": module_test_transactions["count"]
    }

@pytest.fixture(scope="module")
def comprehensive_auth_headers(comprehensive_test_data):
    """Module-scoped auth headers using comprehensive test data"""
    return {"Authorization": f"Bearer {comprehensive_test_data['access_token']}"}

# ==================== FUNCTION SCOPE FIXTURES ====================

@pytest.fixture
def client():
    """Function-scoped sync test client"""
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture(scope="function")
async def async_client():
    """Function-scoped async client for tests that need isolation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def db_client():
    """Function-scoped database client with auto-cleanup"""
    client = MongoAsyncClient(test_mode=True)
    try:
        yield client
        await cleanup_test_db(client)
    finally:
        await safe_close_client(client)

@pytest_asyncio.fixture(scope="function")
async def fresh_test_user(db_client):
    """
    Function-scoped test user for tests that need isolation.
    Creates a new user for each test and cleans up afterwards.
    """
    user_service = UserService()
    auth_service = AuthService()
    
    # Unique user data per test
    import time
    timestamp = int(time.time())
    user_data = {
        "email": f"test_{timestamp}@example.com",
        "name": f"Test User {timestamp}",
        "pwd": "TestPass123!"
    }
    
    # Create and login user
    created_user = await user_service.create_user(
        email=user_data["email"],
        name=user_data["name"],
        pwd=user_data["pwd"]
    )
    
    login_result = await auth_service.login_user(
        email=user_data["email"], 
        pwd=user_data["pwd"]
    )
    
    return {
        "user": created_user,
        "user_data": user_data,
        "auth_tokens": login_result,
        "access_token": login_result.access_token
    }

@pytest.fixture(scope="function")
def fresh_auth_headers(fresh_test_user):
    """Function-scoped auth headers for isolated tests"""
    return {"Authorization": f"Bearer {fresh_test_user['access_token']}"}

# ==================== AUTO-USE FIXTURES ====================

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

# ==================== DATA LOADING UTILITIES ====================

@pytest.fixture(scope="module")
def load_test_data():
    """Module-scoped utility to load test data from JSON files"""
    def _load_data(filename: str) -> Dict[str, Any]:
        """Load test data from backend/data directory"""
        try:
            file_path = f"/workspace/backend/data/{filename}"
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Test data file {filename} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {filename}: {e}")
            return {}
    
    return _load_data

@pytest_asyncio.fixture(scope="module") 
async def analytics_test_data(module_test_users, load_test_data):
    """
    Module-scoped analytics test data.
    Loads analytics-specific test data and creates transactions for analytics testing.
    """
    # Try to load analytics test data
    analytics_data = load_test_data("test_analytics_data.json")
    
    # If no specific analytics data, create comprehensive test transactions
    if not analytics_data.get("transactions"):
        analytics_data = {
            "user": module_test_users["user1"]["user_data"],
            "transactions": [
                # Income transactions
                {
                    "type": "income",
                    "currency": "TWD", 
                    "amount": 50000,
                    "transaction_date": "2024-12-01",
                    "category_id": "income",
                    "subcategory_id": "income_other",
                    "description": "Monthly salary",
                    "notes": "Company A",
                    "tags": ["salary", "monthly"]
                },
                {
                    "type": "income",
                    "currency": "TWD",
                    "amount": 5000,
                    "transaction_date": "2024-12-15",
                    "category_id": "income", 
                    "subcategory_id": "income_other",
                    "description": "Freelance project",
                    "notes": "Side project",
                    "tags": ["freelance", "bonus"]
                },
                # Expense transactions across categories
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 15000,
                    "transaction_date": "2024-12-02",
                    "category_id": "living",
                    "subcategory_id": "rent",
                    "description": "Monthly rent",
                    "notes": "Apartment rent",
                    "tags": ["rent", "monthly"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 1200,
                    "transaction_date": "2024-12-03",
                    "category_id": "food_dining",
                    "subcategory_id": "lunch",
                    "description": "Business lunch",
                    "notes": "Restaurant",
                    "tags": ["business", "food"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 250,
                    "transaction_date": "2024-12-04",
                    "category_id": "food_dining", 
                    "subcategory_id": "breakfast",
                    "description": "Morning coffee",
                    "notes": "Coffee shop",
                    "tags": ["coffee", "morning"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 800,
                    "transaction_date": "2024-12-05",
                    "category_id": "entertainment",
                    "subcategory_id": "movie",
                    "description": "Movie night",
                    "notes": "Cinema",
                    "tags": ["entertainment", "movie"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 2500,
                    "transaction_date": "2024-12-06",
                    "category_id": "shopping",
                    "subcategory_id": "clothing",
                    "description": "Winter jacket",
                    "notes": "Clothing store",
                    "tags": ["winter", "clothing"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 500,
                    "transaction_date": "2024-12-07",
                    "category_id": "transportation",
                    "subcategory_id": "taxi",
                    "description": "Taxi ride",
                    "notes": "Uber",
                    "tags": ["transport", "taxi"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 3500,
                    "transaction_date": "2024-12-08",
                    "category_id": "health",
                    "subcategory_id": "medical",
                    "description": "Medical checkup",
                    "notes": "Annual checkup",
                    "tags": ["health", "medical"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 10000,
                    "transaction_date": "2024-12-09",
                    "category_id": "investment",
                    "subcategory_id": "stock",
                    "description": "Stock investment",
                    "notes": "Portfolio",
                    "tags": ["investment", "stock"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 1500,
                    "transaction_date": "2024-12-10",
                    "category_id": "food_dining",
                    "subcategory_id": "dinner",
                    "description": "Family dinner",
                    "notes": "Japanese restaurant", 
                    "tags": ["family", "dinner"]
                },
                {
                    "type": "expense",
                    "currency": "TWD",
                    "amount": 4500,
                    "transaction_date": "2024-12-11",
                    "category_id": "education",
                    "subcategory_id": "course",
                    "description": "Programming course",
                    "notes": "Online learning",
                    "tags": ["learning", "programming"]
                }
            ]
    
    # Create transactions using the transaction service
    transaction_service = TransactionService()
    created_transactions = []
    
    for transaction_data in analytics_data["transactions"]:
        created_transaction = await transaction_service.create_transaction(
            transaction_data,
            module_test_users["user1"]["user"]
        )
        created_transactions.append(created_transaction)
    
    return {
        "user": module_test_users["user1"]["user"],
        "access_token": module_test_users["user1"]["access_token"],
        "auth_tokens": module_test_users["user1"],
        "transactions": created_transactions,
        "raw_data": analytics_data["transactions"],
        "count": len(created_transactions)
    }

# ==================== UTILITY FUNCTIONS ====================

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

# ==================== LEGACY FUNCTION SCOPE FIXTURES ====================
# Keep these for backward compatibility

@pytest.fixture(scope="function")
def sample_user_data():
    """Legacy function-scoped user data for backward compatibility"""
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
    """Legacy function-scoped transaction data for backward compatibility"""
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
            "tags": ["test tag"]
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
        }
    }