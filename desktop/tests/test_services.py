import pytest
from src.models.database import SessionLocal, Base, engine
from src.models.product import Product, Category
from src.models.user import User, UserRole
from src.models.finance import CashRegister
from src.models.sale_parcel import SaleStatus
from src.services.sale_service import SaleService
from src.services.product_service import ProductService
import os

@pytest.fixture(scope='module')
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    # Setup: Create category and default admin
    cat = Category(name='Test Category')
    db_user = User(username='test_user', hashed_password='fake', role=UserRole.ADMIN)
    db_register = CashRegister(current_balance=100.0, is_open=True)
    session.add(cat)
    session.add(db_user)
    session.add(db_register)
    session.commit()
    
    yield session
    session.close()

def test_sale_flow_integration(db):
    # 1. Create a product
    user = db.query(User).filter(User.username == 'test_user').one()
    cat = db.query(Category).one()
    
    prod = ProductService.create_product(
        db=db, 
        name='Smartphone',
        sku='SM-001',
        price=500.0,
        stock=10,
        category_id=cat.id,
        user_id=user.id
    )
    
    assert prod.stock_quantity == 10
    
    # 2. Perform a sale
    items_data = [
        {'product_id': prod.id, 'quantity': 2, 'price_at_sale': 500.0, 'version': prod.version}
    ]
    
    sale, error = SaleService.create_sale(db, user_id=user.id, items_data=items_data)
    
    assert error is None
    assert sale.total_amount == 1000.0
    
    # 3. Verify stock and cash register
    db.refresh(prod)
    assert prod.stock_quantity == 8
    assert prod.version == 2
    
    register = db.query(CashRegister).first()
    assert register.current_balance == 1100.0
    
    # 4. Verify optimistic locking failure
    # User 2 tries to sell using old version (1)
    items_data_fail = [
        {'product_id': prod.id, 'quantity': 1, 'price_at_sale': 500.0, 'version': 1}
    ]
    sale_fail, error_fail = SaleService.create_sale(db, user_id=user.id, items_data=items_data_fail)
    
    assert sale_fail is None
    assert error_fail == 'OPTIMISTIC_LOCK_CONFLICT'

def test_refund_sale_flow(db):
    # Setup: Create a sale to refund
    user = db.query(User).filter(User.username == 'test_user').one()
    cat = db.query(Category).first()
    prod = db.query(Product).first()
    
    # 1. Capture initial state
    db.refresh(prod)
    initial_stock = prod.stock_quantity
    register = db.query(CashRegister).first()
    initial_balance = register.current_balance
    
    # 2. Perform a sale
    items_data = [{'product_id': prod.id, 'quantity': 1, 'price_at_sale': prod.price, 'version': prod.version}]
    sale, error = SaleService.create_sale(db, user_id=user.id, items_data=items_data)
    assert error is None
    
    # Verify stock decreased
    db.refresh(prod)
    assert prod.stock_quantity == initial_stock - 1
    
    # 3. Perform a refund (using same user as admin for simplicity)
    success, error = SaleService.refund_sale(db, sale.id, admin_id=user.id, cashier_id=user.id)
    assert success is True
    assert error is None
    
    # 4. Verify stock restored
    db.refresh(prod)
    assert prod.stock_quantity == initial_stock
    
    # 5. Verify balance restored
    db.refresh(register)
    assert register.current_balance == initial_balance
    
    # 6. Verify status
    db.refresh(sale)
    assert sale.status == SaleStatus.REFUNDED
