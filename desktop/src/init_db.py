import sys
import os

# Ensure we use the correct PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import Base, engine, SessionLocal
from src.models.user import User, UserRole
from src.models.product import Category, Product, SyncQueue
from src.models.finance import CashRegister, CashTransaction, Withdrawal
from src.models.sale_parcel import Sale, SaleItem, Parcel, ParcelItem
from src.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from src.models.user import AuditLog
import os
from argon2 import PasswordHasher

ph = PasswordHasher()

def init_db():
    # Re-create database if exists for clean start during development
    db_name = os.getenv('DB_NAME', 'pos_local.db')
    # if os.path.exists(db_name):
    #     os.remove(db_name)
        
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create default admin if not exists
        admin = db.query(User).filter(User.username == 'admin').first()
        if not admin:
            admin = User(
                username='admin',
                hashed_password=ph.hash('admin123'),
                role=UserRole.ADMIN
            )
            db.add(admin)
            
        # Create initial cash register if not exists
        register = db.query(CashRegister).first()
        if not register:
            register = CashRegister(current_balance=0.0, is_open=True)
            db.add(register)
            
        db.commit()
        print('Database initialized successfully with default admin and cash register.')
    finally:
        db.close()

if __name__ == '__main__':
    init_db()
