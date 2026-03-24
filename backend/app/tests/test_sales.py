import pytest
from app.services.sale_service import SaleService
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.services.finance_service import FinanceService
from app.schemas.user import UserCreate
from app.schemas.product import CategoryCreate, ProductCreate
from app.core.config import settings
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_sale_logic_and_cash(db_session):
    # Setup
    user_in = UserCreate(username="sale_user", email="s@ex.com", full_name="S User", password="pass")
    user = await UserService.create(db_session, user_in)
    
    cat = await CategoryService.create(db_session, CategoryCreate(name="Sales Cat"))
    prod = await ProductService.create(db_session, ProductCreate(
        name="Soda", sku="SODA-01", price=2.0, stock_quantity=50, category_id=cat.id
    ))
    
    # 1. Create Sale
    sale_in = SaleCreate(items=[
        SaleItemCreate(product_id=prod.id, quantity=5, price_at_sale=2.0, version=prod.version)
    ])
    sale = await SaleService.create_sale(db_session, sale_in, user.id)
    
    assert sale.total_amount == 10.0
    
    # 2. Verify Stock
    await db_session.refresh(prod)
    assert prod.stock_quantity == 45
    assert prod.version == 2 # Initial 1 + 1 from adjustment
    
    # 3. Verify Cash Register
    register = await FinanceService.get_or_create_register(db_session)
    assert register.current_balance == 10.0

@pytest.mark.asyncio
async def test_optimistic_locking(db_session):
    # Setup
    user_in = UserCreate(username="lock_user", email="l@ex.com", full_name="L User", password="pass")
    user = await UserService.create(db_session, user_in)
    cat = await CategoryService.create(db_session, CategoryCreate(name="Lock Cat"))
    prod = await ProductService.create(db_session, ProductCreate(
        name="Water", sku="WATER-01", price=1.0, stock_quantity=10, category_id=cat.id
    ))
    
    # Current version is 1
    # Simulate multi-tab: two sales started with version 1
    sale1_in = SaleCreate(items=[SaleItemCreate(product_id=prod.id, quantity=1, price_at_sale=1.0, version=1)])
    sale2_in = SaleCreate(items=[SaleItemCreate(product_id=prod.id, quantity=1, price_at_sale=1.0, version=1)])
    
    # First sale succeeds
    await SaleService.create_sale(db_session, sale1_in, user.id)
    
    # Second sale should fail because version in DB is now 2
    with pytest.raises(HTTPException) as excinfo:
        await SaleService.create_sale(db_session, sale2_in, user.id)
    assert excinfo.value.status_code == 409
    assert "modified by another transaction" in excinfo.value.detail

@pytest.mark.asyncio
async def test_sale_api(client, db_session):
    # Login
    admin_in = UserCreate(username="admin_s", email="as@ex.com", full_name="Admin S", password="pass", role="admin")
    admin = await UserService.create(db_session, admin_in)
    
    login_data = {"username": "admin_s", "password": "pass"}
    response = await client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    cat = await CategoryService.create(db_session, CategoryCreate(name="API Sale"))
    prod = await ProductService.create(db_session, ProductCreate(
        name="API Item", sku="API-S-01", price=100, stock_quantity=10, category_id=cat.id
    ))
    
    # API Create Sale
    sale_data = {
        "items": [{"product_id": prod.id, "quantity": 1, "price_at_sale": 100, "version": prod.version}]
    }
    response = await client.post(f"{settings.API_V1_STR}/sales/", json=sale_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["total_amount"] == 100.0
    
    # Verify balance via API
    response = await client.get(f"{settings.API_V1_STR}/finance/register", headers=headers)
    assert response.json()["current_balance"] == 100.0
