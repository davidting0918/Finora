import pytest
from httpx import AsyncClient
from fastapi import status

async def create_transaction(async_client: AsyncClient, headers: dict, transaction_data: dict):
    """Helper function to create a transaction"""
    response = await async_client.post("/transaction/create", json=transaction_data, headers=headers)
    return response.json(), response.status_code

async def update_transaction(transaction_id: str, async_client: AsyncClient, headers: dict, transaction_data: dict):
    """Helper function to update a transaction"""
    response = await async_client.post(f"/transaction/update/{transaction_id}", json=transaction_data, headers=headers)
    return response.json(), response.status_code

async def get_transaction(transaction_id: str, async_client: AsyncClient, headers: dict):
    """Helper function to get a single transaction"""
    response = await async_client.get(f"/transaction/info/{transaction_id}", headers=headers)
    return response.json(), response.status_code

async def get_transaction_list(async_client: AsyncClient, headers: dict, params: dict = None):
    """Helper function to get transaction list"""
    response = await async_client.get("/transaction/list", headers=headers, params=params)
    return response.json(), response.status_code

async def delete_transaction(transaction_id: str, async_client: AsyncClient, headers: dict):
    """Helper function to delete a transaction"""
    response = await async_client.post(f"/transaction/delete/{transaction_id}", headers=headers)
    return response.json(), response.status_code


class TestTransactionCRUD:

    @pytest.mark.asyncio
    async def test_create_single_transaction(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test creating a single transaction"""
        transaction_data = test_transactions_data["transaction1"]

        response_data, status_code = await create_transaction(
            async_client, session_auth_headers, transaction_data
        )
        
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Transaction created successfully"
        
    @pytest.mark.asyncio
    async def test_create_multiple_transactions(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test creating multiple transactions"""
        tx_list = test_transactions_data["transaction_list"]
        for tx in tx_list:
            response_data, status_code = await create_transaction(
                async_client, session_auth_headers, tx
            )
        
            assert status_code == status.HTTP_200_OK
            assert response_data["status"] == 1
            assert response_data["message"] == "Transaction created successfully"

    @pytest.mark.asyncio
    async def test_udpate_transaction(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test updating a transaction"""

        # create a transaction for later updating
        old_transaction_data = test_transactions_data["old_transaction"]
        response_data, status_code = await create_transaction(
            async_client, session_auth_headers, old_transaction_data
        )
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Transaction created successfully"

        # update the transaction
        new_transaction_data = test_transactions_data["new_transaction"]
        response_data, status_code = await update_transaction(
            response_data["data"]["id"], async_client, session_auth_headers, new_transaction_data
        )   
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Transaction updated successfully"

    # ================== READ OPERATIONS TESTS ==================
    
    @pytest.mark.asyncio
    async def test_get_single_transaction(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test getting a single transaction by ID"""
        # First create a transaction
        transaction_data = test_transactions_data["transaction1"]
        create_response_data, create_status_code = await create_transaction(
            async_client, session_auth_headers, transaction_data
        )
        
        assert create_status_code == status.HTTP_200_OK
        created_transaction_id = create_response_data["data"]["id"]
        
        # Then get the transaction
        response_data, status_code = await get_transaction(
            created_transaction_id, async_client, session_auth_headers
        )
        
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Transaction fetched successfully"
        assert response_data["data"]["id"] == created_transaction_id
        assert response_data["data"]["type"] == transaction_data["type"]
        assert response_data["data"]["amount"] == transaction_data["amount"]

    @pytest.mark.asyncio
    async def test_get_single_transaction_not_found(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test getting a non-existent transaction returns 404"""
        non_existent_id = test_transactions_data["test_constants"]["non_existent_transaction_id"]
        
        response_data, status_code = await get_transaction(
            non_existent_id, async_client, session_auth_headers
        )
        
        assert status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_transaction_list_default(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test getting transaction list with default pagination"""
        # First create a few transactions
        tx_list = test_transactions_data["transaction_list"][:3]  # Use first 3 transactions
        for tx in tx_list:
            await create_transaction(async_client, session_auth_headers, tx)
        
        # Get transaction list
        response_data, status_code = await get_transaction_list(
            async_client, session_auth_headers
        )
        
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Transactions fetched successfully"
        assert "data" in response_data
        assert "transactions" in response_data["data"]
        assert "pagination" in response_data["data"]
        
        # Check pagination info
        pagination = response_data["data"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 20
        assert pagination["total"] >= len(tx_list)
        assert isinstance(pagination["has_next"], bool)
        assert isinstance(pagination["has_prev"], bool)

    # ================== DELETE OPERATIONS TESTS ==================
    
    @pytest.mark.asyncio
    async def test_delete_single_transaction(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test deleting a single transaction"""
        # First create a transaction
        transaction_data = test_transactions_data["transaction1"]
        create_response_data, create_status_code = await create_transaction(
            async_client, session_auth_headers, transaction_data
        )
        
        assert create_status_code == status.HTTP_200_OK
        created_transaction_id = create_response_data["data"]["id"]
        
        # Delete the transaction
        response_data, status_code = await delete_transaction(
            created_transaction_id, async_client, session_auth_headers
        )
        
        assert status_code == status.HTTP_200_OK
        assert response_data["status"] == 1
        assert response_data["message"] == "Transaction deleted successfully"
        
        # Verify transaction is deleted by trying to get it
        get_response_data, get_status_code = await get_transaction(
            created_transaction_id, async_client, session_auth_headers
        )
        assert get_response_data['data']['is_deleted'] == True

    @pytest.mark.asyncio
    async def test_delete_transaction_not_found(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test deleting a non-existent transaction returns 404"""
        non_existent_id = test_transactions_data["test_constants"]["non_existent_transaction_id"]
        
        response_data, status_code = await delete_transaction(
            non_existent_id, async_client, session_auth_headers
        )
        
        assert status_code == status.HTTP_404_NOT_FOUND

    # ================== VALIDATION TESTS ==================
    @pytest.mark.asyncio
    async def test_create_transaction_invalid_category(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test creating transaction with invalid category"""
        invalid_category_data = test_transactions_data["invalid_transactions"]["invalid_category"]
        
        response_data, status_code = await create_transaction(
            async_client, session_auth_headers, invalid_category_data
        )
        
        assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_transaction_invalid_subcategory(self, async_client: AsyncClient, session_auth_headers, test_transactions_data):
        """Test creating transaction with invalid subcategory"""
        invalid_subcategory_data = test_transactions_data["invalid_transactions"]["invalid_subcategory"]
        
        response_data, status_code = await create_transaction(
            async_client, session_auth_headers, invalid_subcategory_data
        )
        
        assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


    