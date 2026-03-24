import pytest
from src.models.database import SessionLocal, Base, engine
from src.models.product import Product, Category
from src.models.user import User, UserRole
import os

@pytest.fixture(scope='module')
def db():
    # Use a separate test database or ensure it's clean
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_optimistic_locking(db):
    # Setup: Create category and product
    import time
    unique_name = f'Test Category {time.time()}'
    cat = Category(name=unique_name)
    db.add(cat)
    db.commit()
    
    prod = Product(
        name='Test Product',
        sku='TEST-SKU-1',
        price=100.0,
        stock_quantity=10,
        category_id=cat.id
    )
    db.add(prod)
    db.commit()
    
    # Simulate two users reading the same product
    user1_prod = db.query(Product).filter(Product.id == prod.id).one()
    
    # Use a separate session to simulate a second user
    db2 = SessionLocal()
    user2_prod = db2.query(Product).filter(Product.id == prod.id).one()
    
    # User 1 updates stock
    user1_prod.stock_quantity -= 1
    user1_prod.version += 1
    db.commit()
    
    # User 2 tries to update stock using old version
    current_prod = db.query(Product).filter(Product.id == prod.id).one()
    assert current_prod.version > user2_prod.version
    
    db2.close()
    
    assert current_prod.stock_quantity == 9
