from fastapi import APIRouter, Depends
from backend.core.model.transaction import CreateTransactionRequest, UpdateTransactionRequest
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
    
@router.get("/info/{transaction_id}")
async def get_transaction_route(transaction_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        transaction = await transaction_service.get_transaction(transaction_id, current_user)
        return {
            "status": 1,
            "data": transaction.model_dump(mode='json'),
            "message": "Transaction fetched successfully"
        }
    except Exception as e:
        raise e
    

@router.post("/update/{transaction_id}")
async def update_transaction_route(transaction_id: str, request: UpdateTransactionRequest, current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        transaction = await transaction_service.update_transaction(transaction_id, request, current_user)
        return {
            "status": 1,
            "data": transaction.model_dump(mode='json'),
            "message": "Transaction updated successfully"
        }
    except Exception as e:
        raise e

@router.get("/category")
async def get_categories_route():
    if not transaction_service.cat_map:
        await transaction_service.init_cat_map()

    return {
        "status": 1,
        "message": "Categories fetched successfully",
        "data": transaction_service.cat_map
    }

@router.get("/subcategory/{category_id}")
async def get_subcategories_route(category_id: str):
    if not transaction_service.cat_map:
        await transaction_service.init_cat_map()

    return {
        "status": 1,
        "message": "Subcategories fetched successfully",
        "data": transaction_service.cat_map[category_id]['subcategories']
    }