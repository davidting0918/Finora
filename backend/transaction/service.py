import secrets
from datetime import datetime as dt
from datetime import timezone as tz

from fastapi import HTTPException

from backend.core.database import MongoAsyncClient
from backend.core.model.transaction import (
    CreateTransactionRequest,
    Transaction,
    TransactionListQuery,
    TransactionListResponse,
    UpdateTransactionRequest,
    category_collection,
    subcategory_collection,
    transaction_collection,
)
from backend.core.model.user import User


class TransactionService:
    def __init__(self):
        self.db = MongoAsyncClient()
        self.cat_map = {}

    async def init_cat_map(self):
        categories = await self.db.find_many(category_collection, {})
        for cat in categories:
            self.cat_map[cat["id"]] = cat
            self.cat_map[cat["id"]]["subcategories"] = {}

        subcategories = await self.db.find_many(subcategory_collection, {})
        for subcat in subcategories:
            self.cat_map[subcat["category_id"]]["subcategories"][subcat["id"]] = subcat

        return

    @staticmethod
    def _new_transaction_id():
        return str(secrets.token_hex(16))

    async def create_transaction(self, request: CreateTransactionRequest, current_user: User):
        if not self.cat_map:
            await self.init_cat_map()

        # check if category and subcategory exist
        if request.category_id.value not in self.cat_map:
            raise HTTPException(status_code=404, detail=f"Category {request.category_id} not found")

        if request.subcategory_id.value not in self.cat_map[request.category_id.value]["subcategories"]:
            raise HTTPException(status_code=404, detail=f"Subcategory {request.subcategory_id} not found")

        transaction = Transaction(
            id=self._new_transaction_id(),
            user_id=current_user.id,
            user_name=current_user.name,
            type=request.type,
            currency=request.currency,
            amount=request.amount,
            transaction_date=request.transaction_date,
            category_id=request.category_id,
            subcategory_id=request.subcategory_id,
            description=request.description,
            notes=request.notes,
            tags=request.tags,
            created_at=int(dt.now(tz.utc).timestamp()),
            updated_at=int(dt.now(tz.utc).timestamp()),
            is_deleted=False,
        )
        await self.db.insert_one(transaction_collection, transaction.model_dump(mode="json"))
        return transaction

    async def get_transaction(self, transaction_id: str, current_user: User) -> Transaction:
        transaction = await self.db.find_one(transaction_collection, {"id": transaction_id, "user_id": current_user.id})
        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        transaction = Transaction(**transaction)
        return transaction

    async def update_transaction(self, transaction_id: str, request: UpdateTransactionRequest, current_user: User):
        transaction = await self.db.find_one(transaction_collection, {"id": transaction_id, "user_id": current_user.id})
        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

        transaction = Transaction(
            **transaction,
        )
        transaction.update(request)

        await self.db.update_one(
            transaction_collection,
            {"id": transaction_id, "user_id": current_user.id},
            transaction.model_dump(mode="json"),
        )
        return transaction

    async def delete_transaction(self, transaction_id: str, current_user: User):
        # check if transaction exists
        transaction = await self.db.find_one(transaction_collection, {"id": transaction_id, "user_id": current_user.id})
        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

        # soft delete
        await self.db.update_one(
            transaction_collection, {"id": transaction_id, "user_id": current_user.id}, {"is_deleted": True}
        )

    async def get_transaction_list(self, query: TransactionListQuery, current_user: User) -> TransactionListResponse:
        """
        Get paginated list of transactions with filtering and sorting
        """
        # Build MongoDB query filter
        filter_conditions = {"user_id": current_user.id, "is_deleted": False}

        # Add date range filter
        if query.start_date or query.end_date:
            date_filter = {}
            if query.start_date:
                # Convert to timestamp for comparison
                start_timestamp = int(query.start_date.timestamp())
                date_filter["$gte"] = start_timestamp
            if query.end_date:
                # Add 24 hours to include the entire end date
                end_date = query.end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                end_timestamp = int(end_date.timestamp())
                date_filter["$lte"] = end_timestamp

            # Use created_at for timestamp comparison since transaction_date is datetime
            filter_conditions["created_at"] = date_filter

        # Add transaction type filter
        if query.transaction_type:
            filter_conditions["type"] = query.transaction_type.value

        # Add category filter
        if query.category_id:
            filter_conditions["category_id"] = query.category_id.value

        # Add subcategory filter
        if query.subcategory_id:
            filter_conditions["subcategory_id"] = query.subcategory_id.value

        # Get total count for pagination using the new database method
        total = await self.db.count_documents(transaction_collection, filter_conditions)

        # Calculate pagination
        skip = (query.page - 1) * query.limit
        total_pages = (total + query.limit - 1) // query.limit

        # Build sort criteria
        sort_direction = 1 if query.sort_order == "asc" else -1
        sort_criteria = [(query.sort_by, sort_direction)]

        # Execute query with pagination and sorting using the new database method
        documents = await self.db.find_with_pagination(
            collection=transaction_collection,
            filter=filter_conditions,
            sort_criteria=sort_criteria,
            skip=skip,
            limit=query.limit,
        )

        # Convert documents to Transaction objects
        transactions = []
        for doc in documents:
            try:
                transaction = Transaction(**doc)
                transactions.append(transaction)
            except Exception as e:
                # Log error but continue processing other transactions
                print(f"Error parsing transaction {doc.get('id', 'unknown')}: {e}")
                continue

        # Build response
        response = TransactionListResponse(
            transactions=transactions,
            total=total,
            page=query.page,
            limit=query.limit,
            total_pages=total_pages,
            has_next=query.page < total_pages,
            has_prev=query.page > 1,
        )

        return response
