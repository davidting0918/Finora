import pytest
from httpx import AsyncClient
from fastapi import status
import pytest_asyncio

@pytest_asyncio.fixture
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
        headers, _ = user_and_token
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
        headers, _ = user_and_token

        response = await async_client.post(
            "/transaction/create",
            json=sample_transaction_data["transaction1"],
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction created successfully"

        response = await async_client.get(
            "/transaction/info/{}".format(data["data"]["id"]),
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction fetched successfully"

    @pytest.mark.asyncio 
    async def test_get_main_and_sub_categories(
        self, async_client: AsyncClient, db_client, user_and_token
    ):
        headers, _ = user_and_token

        response = await async_client.get(
            "/transaction/category",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Categories fetched successfully"
        assert len(data["data"]) > 0

        response = await async_client.get(
            "/transaction/subcategory/{}".format(list(data["data"].keys())[0]),
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Subcategories fetched successfully"
        assert len(data["data"]) > 0


    @pytest.mark.asyncio
    async def test_update_transaction(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token

        response = await async_client.post(
            "/transaction/create",
            json=sample_transaction_data["old_transaction"],
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction created successfully"

        response = await async_client.post(
            "/transaction/update/{}".format(data["data"]["id"]),
            json=sample_transaction_data["new_transaction"],
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction updated successfully"
        
    @pytest.mark.asyncio
    async def test_delete_transaction(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token

        response = await async_client.post(
            "/transaction/create",
            json=sample_transaction_data["transaction1"],
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction created successfully"

        response = await async_client.post(
            "/transaction/delete/{}".format(data["data"]["id"]),
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transaction deleted successfully"
    @pytest.mark.asyncio
    async def test_get_transaction_list_basic(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Create multiple diverse transactions using sample data
        transaction_ids = []
        for transaction in sample_transaction_data["transaction_list"][:10]:  # Use first 10 transactions
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == 1
            transaction_ids.append(data["data"]["id"])
        
        # Test basic list functionality
        response = await async_client.get(
            "/transaction/list",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["message"] == "Transactions fetched successfully"
        assert "transactions" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["transactions"]) == 10
        assert data["data"]["pagination"]["total"] == 10

    @pytest.mark.asyncio
    async def test_get_transaction_list_pagination(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Create all 20 transactions for comprehensive pagination testing
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Test pagination - first page with limit 8
        response = await async_client.get(
            "/transaction/list?page=1&limit=8",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 8
        assert data["data"]["pagination"]["total"] == 20
        assert data["data"]["pagination"]["total_pages"] == 3  # 20 items, 8 per page = 3 pages
        assert data["data"]["pagination"]["has_next"] == True
        assert data["data"]["pagination"]["has_prev"] == False
        assert len(data["data"]["transactions"]) == 8

        # Test pagination - middle page
        response = await async_client.get(
            "/transaction/list?page=2&limit=8",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["page"] == 2
        assert data["data"]["pagination"]["has_next"] == True
        assert data["data"]["pagination"]["has_prev"] == True
        assert len(data["data"]["transactions"]) == 8

        # Test pagination - last page
        response = await async_client.get(
            "/transaction/list?page=3&limit=8",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["page"] == 3
        assert data["data"]["pagination"]["has_next"] == False
        assert data["data"]["pagination"]["has_prev"] == True
        assert len(data["data"]["transactions"]) == 4  # Remaining 4 transactions

    @pytest.mark.asyncio
    async def test_get_transaction_list_filtering_by_type(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Create all sample transactions (includes both income and expense)
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Filter by expense (should get 18 transactions)
        response = await async_client.get(
            "/transaction/list?transaction_type=expense",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] == 18
        for transaction in data["data"]["transactions"]:
            assert transaction["type"] == "expense"
        
        # Filter by income (should get 2 transactions)
        response = await async_client.get(
            "/transaction/list?transaction_type=income",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] == 2
        for transaction in data["data"]["transactions"]:
            assert transaction["type"] == "income"

    @pytest.mark.asyncio
    async def test_get_transaction_list_filtering_by_category(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Create all sample transactions
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Filter by food_dining category (should find multiple transactions)
        response = await async_client.get(
            "/transaction/list?category_id=food_dining",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] >= 4  # We have breakfast, lunch, dinner, snack, drink
        for transaction in data["data"]["transactions"]:
            assert transaction["category_id"] == "food_dining"
        
        # Filter by shopping category
        response = await async_client.get(
            "/transaction/list?category_id=shopping",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] >= 3  # We have clothing, electronics, home_goods
        for transaction in data["data"]["transactions"]:
            assert transaction["category_id"] == "shopping"

        # Filter by income category
        response = await async_client.get(
            "/transaction/list?category_id=income",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] == 2  # We have 2 income transactions
        for transaction in data["data"]["transactions"]:
            assert transaction["category_id"] == "income"

    @pytest.mark.asyncio
    async def test_get_transaction_list_sorting(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Create all sample transactions with diverse amounts
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Sort by amount ascending
        response = await async_client.get(
            "/transaction/list?sort_by=amount&sort_order=asc",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        transactions = data["data"]["transactions"]
        # Verify ascending order (amounts should increase)
        for i in range(len(transactions) - 1):
            assert transactions[i]["amount"] <= transactions[i + 1]["amount"]
        
        # Sort by amount descending
        response = await async_client.get(
            "/transaction/list?sort_by=amount&sort_order=desc",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        transactions = data["data"]["transactions"]
        # Verify descending order (amounts should decrease)
        for i in range(len(transactions) - 1):
            assert transactions[i]["amount"] >= transactions[i + 1]["amount"]

        # Sort by date descending (most recent first)
        response = await async_client.get(
            "/transaction/list?sort_by=transaction_date&sort_order=desc",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        transactions = data["data"]["transactions"]
        # Verify date descending order
        for i in range(len(transactions) - 1):
            assert transactions[i]["transaction_date"] >= transactions[i + 1]["transaction_date"]

    @pytest.mark.asyncio
    async def test_get_transaction_list_search(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Create all sample transactions for comprehensive search testing
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Search by description keyword "coffee"
        response = await async_client.get(
            "/transaction/list?search_keyword=coffee",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] >= 1
        found_coffee = any("coffee" in t["description"].lower() for t in data["data"]["transactions"])
        assert found_coffee
        
        # Search by notes keyword "Starbucks"
        response = await async_client.get(
            "/transaction/list?search_keyword=Starbucks",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] >= 1
        found_starbucks = any("starbucks" in t.get("notes", "").lower() for t in data["data"]["transactions"])
        assert found_starbucks
        
        # Search by description keyword "laptop"
        response = await async_client.get(
            "/transaction/list?search_keyword=laptop",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] >= 1
        found_laptop = any("laptop" in t["description"].lower() for t in data["data"]["transactions"])
        assert found_laptop

        # Search by amount-related keyword (should find salary)
        response = await async_client.get(
            "/transaction/list?search_keyword=salary",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["pagination"]["total"] >= 1
        found_salary = any("salary" in t["description"].lower() for t in data["data"]["transactions"])
        assert found_salary

    @pytest.mark.asyncio
    async def test_get_transaction_list_date_range_filtering(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        """Test date range filtering with realistic transaction dates"""
        headers, _ = user_and_token
        
        # Create all sample transactions
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Test filtering by date range (first half of January)
        response = await async_client.get(
            "/transaction/list?start_date=2025-01-01&end_date=2025-01-15",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for transaction in data["data"]["transactions"]:
            assert "2025-01-01" <= transaction["transaction_date"] <= "2025-01-15"
        
        # Test filtering by date range (second half of January)
        response = await async_client.get(
            "/transaction/list?start_date=2025-01-16&end_date=2025-01-31",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for transaction in data["data"]["transactions"]:
            assert "2025-01-16" <= transaction["transaction_date"] <= "2025-01-31"

    @pytest.mark.asyncio
    async def test_get_transaction_list_amount_statistics(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        """Test transaction list with focus on amount statistics using realistic data"""
        headers, _ = user_and_token
        
        # Create all sample transactions
        total_expense = 0
        total_income = 0
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
            
            # Calculate expected totals
            if transaction["type"] == "expense":
                total_expense += transaction["amount"]
            else:
                total_income += transaction["amount"]
        
        # Get all transactions and verify amounts
        response = await async_client.get(
            "/transaction/list?limit=50",  # Ensure we get all transactions
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify we have the correct mix of transaction types
        expense_count = sum(1 for t in data["data"]["transactions"] if t["type"] == "expense")
        income_count = sum(1 for t in data["data"]["transactions"] if t["type"] == "income")
        assert expense_count == 18  # We created 18 expense transactions
        assert income_count == 2   # We created 2 income transactions
        
        # Verify amount ranges exist
        amounts = [t["amount"] for t in data["data"]["transactions"]]
        assert min(amounts) >= 75    # Smallest amount is bubble tea
        assert max(amounts) >= 50000 # Largest amount is monthly salary


    @pytest.mark.asyncio
    async def test_get_transaction_list_subcategory_filtering(
        self, async_client: AsyncClient, sample_transaction_data, db_client, user_and_token
    ):
        """Test filtering by subcategories using diverse sample data"""
        headers, _ = user_and_token
        
        # Create all sample transactions
        for transaction in sample_transaction_data["transaction_list"]:
            response = await async_client.post(
                "/transaction/create",
                json=transaction,
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Test filtering by specific subcategories
        subcategory_tests = [
            ("breakfast", "food_dining"),
            ("lunch", "food_dining"), 
            ("clothing", "shopping"),
            ("electronics", "shopping"),
            ("stock", "investment"),
            ("hotel", "travel")
        ]
        
        for subcategory_id, category_id in subcategory_tests:
            response = await async_client.get(
                f"/transaction/list?subcategory_id={subcategory_id}",
                headers=headers
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            if data["data"]["pagination"]["total"] > 0:
                for transaction in data["data"]["transactions"]:
                    assert transaction["subcategory_id"] == subcategory_id
                    assert transaction["category_id"] == category_id

    @pytest.mark.asyncio
    async def test_get_transaction_list_empty_result(
        self, async_client: AsyncClient, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Test empty transaction list
        response = await async_client.get(
            "/transaction/list",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == 1
        assert data["data"]["pagination"]["total"] == 0
        assert len(data["data"]["transactions"]) == 0
        assert data["data"]["pagination"]["has_next"] == False
        assert data["data"]["pagination"]["has_prev"] == False

    @pytest.mark.asyncio
    async def test_get_transaction_list_invalid_params(
        self, async_client: AsyncClient, db_client, user_and_token
    ):
        headers, _ = user_and_token
        
        # Test invalid page number
        response = await async_client.get(
            "/transaction/list?page=0",
            headers=headers
        )
        assert response.status_code == 422  # Validation error
        
        # Test invalid limit
        response = await async_client.get(
            "/transaction/list?limit=0",
            headers=headers
        )
        assert response.status_code == 422  # Validation error
        
        # Test limit exceeding maximum
        response = await async_client.get(
            "/transaction/list?limit=101",
            headers=headers
        )
        assert response.status_code == 422  # Validation error