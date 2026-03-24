import pytest
from app.services.user_service import UserService
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.services.stock_service import StockService
from app.schemas.user import UserCreate
from app.schemas.product import CategoryCreate, ProductCreate
from app.schemas.stock import StockAdjustment
from app.models.user import UserRole

@pytest.mark.asyncio
async def test_user_service(db_session):
    # Test Create
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="password123",
        role=UserRole.CASHIER
    )
    user = await UserService.create(db_session, user_in)
    assert user.username == "testuser"
    assert user.role == UserRole.CASHIER
    
    # Test Authenticate
    auth_user = await UserService.authenticate(db_session, "testuser", "password123")
    assert auth_user is not None
    assert auth_user.id == user.id
    
    # Test Wrong Password
    wrong_user = await UserService.authenticate(db_session, "testuser", "wrong")
    assert wrong_user is None

@pytest.mark.asyncio
async def test_category_and_product_service(db_session):
    # Create Category
    cat_in = CategoryCreate(name="Food", description="Things to eat")
    cat = await CategoryService.create(db_session, cat_in)
    assert cat.name == "Food"
    
    # Create Product
    prod_in = ProductCreate(
        name="Bread",
        sku="BREAD-001",
        price=1.5,
        stock_quantity=100,
        category_id=cat.id
    )
    prod = await ProductService.create(db_session, prod_in)
    assert prod.name == "Bread"
    assert prod.category_id == cat.id

@pytest.mark.asyncio
async def test_stock_service(db_session):
    # Setup: User, Category, Product
    user_in = UserCreate(username="admin_stock", email="admin@stock.com", full_name="Admin Stock", password="pass")
    user = await UserService.create(db_session, user_in)
    
    cat_in = CategoryCreate(name="Hardware")
    cat = await CategoryService.create(db_session, cat_in)
    
    prod_in = ProductCreate(name="Hammer", sku="HAM-01", price=10.0, stock_quantity=10, category_id=cat.id)
    prod = await ProductService.create(db_session, prod_in)
    
    # Test Stock Adjustment (Increase)
    adj_in = StockAdjustment(product_id=prod.id, change_amount=5, reason="Restock")
    updated_prod = await StockService.adjust_stock(db_session, adj_in, user.id)
    
    assert updated_prod.stock_quantity == 15
    assert updated_prod.version == 2 
    
    # Test Stock Adjustment (Decrease)
    adj_out = StockAdjustment(product_id=prod.id, change_amount=-3, reason="Sale")
    updated_prod = await StockService.adjust_stock(db_session, adj_out, user.id)
    
    assert updated_prod.stock_quantity == 12
    assert updated_prod.version == 3
