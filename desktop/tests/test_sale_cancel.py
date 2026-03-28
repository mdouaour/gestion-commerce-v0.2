import pytest
from src.models.database import SessionLocal, Base, engine
from src.models.product import Category, Product
from src.models.user import User, UserRole
from src.models.finance import CashRegister, CashTransaction
from src.services.sale_service import SaleService
from src.services.product_service import ProductService

@pytest.fixture(scope='function')
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    cat = Category(name='Test')
    admin = User(username='admin', hashed_password='fake', role=UserRole.ADMIN)
    reg = CashRegister(current_balance=100.0, is_open=True)
    session.add(cat)
    session.add(admin)
    session.add(reg)
    session.commit()
    yield session
    session.close()

def test_cancel_sale_flow(db):
    admin = db.query(User).filter(User.username == 'admin').one()
    cat = db.query(Category).one()
    
    # 1. Create product and sell it
    prod = ProductService.create_product(db, 'Phone', 'PH1', 500.0, 10, cat.id, admin.id)
    items_data = [{'product_id': prod.id, 'quantity': 2, 'price_at_sale': 500.0, 'version': prod.version}]
    sale, _ = SaleService.create_sale(db, admin.id, items_data)
    
    db.refresh(prod)
    reg = db.query(CashRegister).first()
    assert prod.stock_quantity == 8
    assert reg.current_balance == 1100.0
    
    # 2. Cancel the sale (Function doesn't exist yet)
    success, error = SaleService.cancel_sale(db, sale.id, admin.id)
    
    assert success is True
    assert error is None
    
    # 3. Verify stock restored and cash reversed
    db.refresh(prod)
    db.refresh(reg)
    assert prod.stock_quantity == 10
    assert reg.current_balance == 100.0
    
    # Verify transaction record
    tx = db.query(CashTransaction).filter(CashTransaction.reason.contains(f'Reversal for Sale #{sale.id}')).first()
    assert tx is not None
    assert tx.amount == -1000.0
