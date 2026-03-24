from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductWithCategory
from app.services.product_service import ProductService
from app.routes.deps import get_db, get_current_user, check_admin

router = APIRouter()

@router.get("/", response_model=List[ProductWithCategory])
async def read_products(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    Retrieve products.
    """
    return await ProductService.get_all(db)

@router.post("/", response_model=Product, dependencies=[Depends(check_admin)])
async def create_product(
    *,
    db: AsyncSession = Depends(get_db),
    product_in: ProductCreate,
) -> Any:
    """
    Create new product.
    """
    product = await ProductService.get_by_sku(db, sku=product_in.sku)
    if product:
        raise HTTPException(status_code=400, detail="SKU already exists")
    return await ProductService.create(db, obj_in=product_in)

@router.get("/{id}", response_model=ProductWithCategory)
async def read_product(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get product by ID.
    """
    product = await ProductService.get(db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{id}", response_model=Product, dependencies=[Depends(check_admin)])
async def update_product(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    product_in: ProductUpdate,
) -> Any:
    """
    Update a product.
    """
    product = await ProductService.get(db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check for SKU conflict
    if product_in.sku and product_in.sku != product.sku:
        existing = await ProductService.get_by_sku(db, sku=product_in.sku)
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")
            
    return await ProductService.update(db, db_obj=product, obj_in=product_in)

@router.delete("/{id}", response_model=bool, dependencies=[Depends(check_admin)])
async def delete_product(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    """
    Delete a product.
    """
    success = await ProductService.delete(db, id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return success
