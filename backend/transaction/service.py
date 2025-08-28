from backend.core.model.transaction import Transaction, Category, SubCategory, CreateTransactionRequest, transaction_collection, UpdateTransactionRequest, category_collection, subcategory_collection
from backend.core.database import MongoAsyncClient
from datetime import datetime as dt, timezone as tz, timedelta as td
from backend.core.model.user import User
import secrets
from fastapi import HTTPException
import json


class TransactionService:
    def __init__(self):
        self.db = MongoAsyncClient()
        self.cat_map = {}

    async def init_cat_map(self):
        categories = await self.db.find_many(category_collection, {})
        for cat in categories:
            self.cat_map[cat['id']] = cat
            self.cat_map[cat['id']]['subcategories'] = {}

        subcategories = await self.db.find_many(subcategory_collection, {})
        for subcat in subcategories:
            self.cat_map[subcat['category_id']]['subcategories'][subcat['id']] = subcat

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

        if request.subcategory_id.value not in self.cat_map[request.category_id.value]['subcategories']:
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
            is_deleted=False
        )
        await self.db.insert_one(transaction_collection, transaction.model_dump(mode='json'))
        return transaction
        
    async def get_transaction(self, transaction_id: str, current_user: User) -> Transaction:
        transaction = await self.db.find_one(
            transaction_collection,
            {"id": transaction_id, "user_id": current_user.id}
        )
        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

        return transaction
    
    async def update_transaction(self, transaction_id: str, request: UpdateTransactionRequest, current_user: User):
        transaction = await self.db.find_one(
            transaction_collection,
            {"id": transaction_id, "user_id": current_user.id}
        )
        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        
        transaction = Transaction(
            **transaction,
        )
        transaction.update(request)

        await self.db.update_one(
            transaction_collection,
            {"id": transaction_id, "user_id": current_user.id},
            transaction.model_dump(mode='json')
        )
        return transaction