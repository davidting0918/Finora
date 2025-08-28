from backend.core.model.transaction import Transaction, Category, SubCategory, CreateTransactionRequest
from backend.core.database import MongoAsyncClient
from datetime import datetime as dt, timezone as tz, timedelta as td
from backend.core.model.user import User
import secrets
from fastapi import HTTPException
import json

class TransactionService:
    def __init__(self):
        self.db = MongoAsyncClient()
        self.cat_map = self._init_category_map()

    @staticmethod
    def _init_category_map():
        with open("backend/data/default_categories.json", "r") as f:
            data = json.load(f)
        cat_map = {}

        for cat in data["categories"]:
            cat_map[cat["id"]] = cat
            cat_map[cat['id']]['subcategories'] = {}
        for subcat in data["subcategories"]:
            cat_map[subcat['category_id']]['subcategories'][subcat['id']] = subcat
        return cat_map

    @staticmethod
    def _new_transaction_id():
        return str(secrets.token_hex(16))
    
    async def create_transaction(self, request: CreateTransactionRequest, current_user: User):
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
        await self.db.insert_one("transactions", transaction.model_dump(mode='json'))
        return transaction
        
    async def get_transaction(self, transaction_id: str):
        pass
    
    async def update_transaction(self, transaction_id: str, transaction: Transaction):
        pass