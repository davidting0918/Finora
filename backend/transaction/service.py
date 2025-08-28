from backend.core.model.transaction import Transaction, Category, SubCategory, CreateTransactionRequest
from backend.core.database import MongoAsyncClient
from datetime import datetime as dt, timezone as tz, timedelta as td
from backend.core.model.user import User
import secrets
from fastapi import HTTPException

class TransactionService:
    def __init__(self):
        self.db = MongoAsyncClient()

    @staticmethod
    def _new_transaction_id():
        return str(secrets.token_hex(16))
    
    async def create_transaction(self, request: CreateTransactionRequest, current_user: User):
        # check if category and subcategory exist
        category = await self.db.find_one("categories", {"id": request.category_id})
        if not category:
            raise HTTPException(status_code=404, detail=f"Category {request.category_id} not found")
        subcategory = await self.db.find_one("subcategories", {"id": request.subcategory_id})
        if not subcategory:
            raise HTTPException(status_code=404, detail=f"Subcategory {request.subcategory_id} not found")
        
        transaction = Transaction(
            id=self._new_transaction_id(),
            user_id=current_user.id,
            user_name=current_user.name,
            type=request.type,
            amount=request.amount,
            transaction_date=request.transaction_date,
            category_id=request.category_id,
            subcategory_id=request.subcategory_id,
            description=request.description,
            notes=request.notes,
            tags=request.tags,
            created_at=int(dt.now(tz.utc).timestamp()),
            updated_at=int(dt.now(tz.utc).timestamp()),
            is_deleted=False
        )
        await self.db.insert_one("transactions", transaction.model_dump(mode='json'))
        return transaction
        
    async def get_transaction(self, transaction_id: str):
        pass
    
    async def update_transaction(self, transaction_id: str, transaction: Transaction):
        pass