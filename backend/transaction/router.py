from datetime import datetime as dt
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from backend.auth.service import get_current_active_user
from backend.core.model.transaction import (
    CategoryId,
    CreateTransactionRequest,
    SubCategoryId,
    TransactionListQuery,
    TransactionType,
    UpdateTransactionRequest,
)
from backend.core.model.user import User
from backend.transaction.service import TransactionService

router = APIRouter(prefix="/transaction", tags=["transaction"])
transaction_service = TransactionService()


@router.post("/create")
async def create_transaction_route(
    request: CreateTransactionRequest, current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        transaction = await transaction_service.create_transaction(request, current_user)
        return {"status": 1, "data": transaction.model_dump(mode="json"), "message": "Transaction created successfully"}
    except Exception as e:
        raise e


# get single transaction
@router.get("/info/{transaction_id}")
async def get_transaction_route(transaction_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        transaction = await transaction_service.get_transaction(transaction_id, current_user)
        return {"status": 1, "data": transaction.model_dump(mode="json"), "message": "Transaction fetched successfully"}
    except Exception as e:
        raise e


@router.get("/list")
async def get_transaction_list_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page (1-100)"),
    start_date: Optional[dt] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[dt] = Query(None, description="End date filter (ISO format)"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    category_id: Optional[CategoryId] = Query(None, description="Filter by category ID"),
    subcategory_id: Optional[SubCategoryId] = Query(None, description="Filter by subcategory ID"),
    sort_by: str = Query(
        "transaction_date", description="Sort by field (transaction_date, amount, created_at, updated_at)"
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"),
):
    try:
        # Create query object with validation
        query = TransactionListQuery(
            page=page,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            category_id=category_id,
            subcategory_id=subcategory_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        result = await transaction_service.get_transaction_list(query, current_user)

        return {
            "status": 1,
            "data": {
                "transactions": [t.model_dump(mode="json") for t in result.transactions],
                "pagination": {
                    "total": result.total,
                    "page": result.page,
                    "limit": result.limit,
                    "total_pages": result.total_pages,
                    "has_next": result.has_next,
                    "has_prev": result.has_prev,
                },
            },
            "message": "Transactions fetched successfully",
        }
    except Exception as e:
        raise e


@router.post("/update/{transaction_id}")
async def update_transaction_route(
    transaction_id: str,
    request: UpdateTransactionRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        transaction = await transaction_service.update_transaction(transaction_id, request, current_user)
        return {"status": 1, "data": transaction.model_dump(mode="json"), "message": "Transaction updated successfully"}
    except Exception as e:
        raise e


@router.post("/delete/{transaction_id}")
async def delete_transaction_route(
    transaction_id: str, current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        await transaction_service.delete_transaction(transaction_id, current_user)
        return {"status": 1, "message": "Transaction deleted successfully"}
    except Exception as e:
        raise e


@router.get("/category")
async def get_categories_route():
    if not transaction_service.cat_map:
        await transaction_service.init_cat_map()

    return {"status": 1, "message": "Categories fetched successfully", "data": transaction_service.cat_map}


@router.get("/subcategory/{category_id}")
async def get_subcategories_route(category_id: str):
    if not transaction_service.cat_map:
        await transaction_service.init_cat_map()

    return {
        "status": 1,
        "message": "Subcategories fetched successfully",
        "data": transaction_service.cat_map[category_id]["subcategories"],
    }
