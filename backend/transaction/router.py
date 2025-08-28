from fastapi import APIRouter, Depends, HTTPException, status
from backend.core.model import transaction
from backend.core.model.transaction import CreateTransactionRequest
from backend.transaction.service import TransactionService
from backend.core.model.user import User
from backend.auth.service import get_current_active_user
from typing import Annotated


router = APIRouter(prefix="/transaction", tags=["transaction"])
transaction_service = TransactionService()

@router.post("/create")
async def create_transaction_route(request: CreateTransactionRequest, current_user: Annotated[User, Depends(get_current_active_user)]):
    try: 
        transaction = await transaction_service.create_transaction(request, current_user)
        return {
            "status": 1,
            "data": transaction.model_dump(mode='json'),
            "message": "Transaction created successfully"
        }
    except Exception as e:
        raise e

@router.get("/category")
async def get_categories_route():
    return {
        "status": 1,
        "message": "Categories fetched successfully",
        "data": transaction_service.cat_map
    }

@router.get("/subcategory/{category_id}")
async def get_subcategories_route(category_id: str):
    return {
        "status": 1,
        "message": "Subcategories fetched successfully",
        "data": transaction_service.cat_map[category_id]['subcategories']
    }