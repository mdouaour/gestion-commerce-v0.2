from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import Category, CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService
from app.routes.deps import get_db, get_current_user, check_admin

router = APIRouter()

@router.get("/", response_model=List[Category])
async def read_categories(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    Retrieve categories.
    """
    return await CategoryService.get_all(db)

@router.post("/", response_model=Category, dependencies=[Depends(check_admin)])
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: CategoryCreate,
) -> Any:
    """
    Create new category.
    """
    return await CategoryService.create(db, obj_in=category_in)

@router.put("/{id}", response_model=Category, dependencies=[Depends(check_admin)])
async def update_category(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    category_in: CategoryUpdate,
) -> Any:
    """
    Update a category.
    """
    category = await CategoryService.get(db, id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await CategoryService.update(db, db_obj=category, obj_in=category_in)

@router.delete("/{id}", response_model=bool, dependencies=[Depends(check_admin)])
async def delete_category(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    """
    Delete a category.
    """
    success = await CategoryService.delete(db, id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return success
