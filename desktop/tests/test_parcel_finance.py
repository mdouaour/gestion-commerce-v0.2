import pytest
from src.models.database import SessionLocal, Base, engine
from src.models.product import Category
from src.models.user import User, UserRole
from src.models.finance import CashRegister
from src.services.parcel_service import ParcelService
from src.services.product_service import ProductService

@pytest.fixture(scope='function')
def db():
    # Use a clean DB for each test in this module
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    # Setup: Create category, user, and register
    cat = Category(name='Test Category')
    db_user = User(username='test_user', hashed_password='fake', role=UserRole.ADMIN)
    db_register = CashRegister(current_balance=100.0, is_open=True)
    session.add(cat)
    session.add(db_user)
    session.add(db_register)
    session.commit()
    
    yield session
    session.close()

def test_parcel_collection_updates_cash(db):
    # 1. Setup product and parcel
    user = db.query(User).filter(User.username == 'test_user').one()
    cat = db.query(Category).one()
    
    prod = ProductService.create_product(
        db=db, 
        name='Laptop',
        sku='LP-001',
        price=1000.0,
        stock=5,
        category_id=cat.id,
        user_id=user.id
    )
    
    items_data = [{'product_id': prod.id, 'quantity': 1, 'price_at_sale': 1000.0}]
    parcel, error = ParcelService.create_parcel(
        db=db, 
        client_name='Alice',
        client_phone='123456',
        client_address='123 St',
        items_data=items_data,
        shipping_fee=50.0,
        user_id=user.id
    )
    
    assert parcel is not None
    assert parcel.total_amount == 1050.0
    
    # Check initial register balance
    register = db.query(CashRegister).first()
    assert register.current_balance == 100.0 # Parcel creation shouldn't add to cash yet
    
    # 2. Collect money
    collected_amount = parcel.total_amount
    res, error = ParcelService.collect_parcel_money(db, parcel.id, collected_amount, user.id)
    assert error is None, f"Collection failed with error: {error}"
    
    # 3. Verify cash register update
    db.refresh(register)
    assert register.current_balance == 1150.0, f"Expected 1150.0, got {register.current_balance}"
    
    # Verify transaction record
    from src.models.finance import CashTransaction
    txs = db.query(CashTransaction).all()
    print(f"Transactions in DB: {[tx.reason for tx in txs]}")
    
    tx = db.query(CashTransaction).filter(CashTransaction.reason.like(f"%Parcel collection #{parcel.id}%")).first()
    assert tx is not None
    assert tx.amount == 1050.0

def test_parcel_collection_unauthorized(db):
    # 1. Setup
    cat = db.query(Category).one()
    admin = db.query(User).filter(User.username == 'test_user').one()
    
    # Create a cashier
    cashier = User(username='cashier_joe', hashed_password='fake', role=UserRole.CASHIER)
    db.add(cashier)
    db.commit()
    
    prod = ProductService.create_product(db, 'Item', 'SKU1', 10.0, 10, cat.id, admin.id)
    parcel, _ = ParcelService.create_parcel(db, 'Bob', '123', 'Home', [{'product_id': prod.id, 'quantity': 1, 'price_at_sale': 10.0}], 0, admin.id)
    
    # 2. Try collection as cashier
    res, error = ParcelService.collect_parcel_money(db, parcel.id, 10.0, cashier.id)
    
    assert res is None
    assert error == 'UNAUTHORIZED_ACTION'
    
    # Verify no money added
    register = db.query(CashRegister).first()
    assert register.current_balance == 100.0
