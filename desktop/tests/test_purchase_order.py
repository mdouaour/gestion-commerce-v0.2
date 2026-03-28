import pytest
from src.models.database import SessionLocal, Base, engine
from src.models.product import Category, Product
from src.models.user import User, UserRole
from src.models.purchase_order import PurchaseOrder, POStatus
from src.services.purchase_order_service import POService
from src.services.product_service import ProductService

@pytest.fixture(scope='function')
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    cat = Category(name='Test')
    admin = User(username='admin', hashed_password='fake', role=UserRole.ADMIN)
    session.add(cat)
    session.add(admin)
    session.commit()
    yield session
    session.close()

def test_po_flow(db):
    admin = db.query(User).filter(User.username == 'admin').one()
    cat = db.query(Category).one()
    prod = ProductService.create_product(db, 'Stock Item', 'SI1', 100.0, 5, cat.id, admin.id)
    
    # 1. Create PO
    items_data = [{
        'product_id': prod.id,
        'quantity': 10,
        'purchase_price': 50.0,
        'selling_price': 110.0
    }]
    po, error = POService.create_po(db, 'Supplier A', items_data, admin.id)
    
    assert po is not None
    assert po.status == POStatus.DRAFT
    assert po.total_amount == 500.0
    
    # 2. Receive PO (Increases stock and updates price)
    success, error = POService.receive_po(db, po.id, admin.id)
    assert success is True
    
    db.refresh(prod)
    assert prod.stock_quantity == 15
    assert prod.price == 110.0
    assert po.status == POStatus.DELIVERED
    
    # 3. Pay PO
    success, error = POService.pay_po(db, po.id, admin.id)
    assert success is True
    assert po.status == POStatus.PAID
