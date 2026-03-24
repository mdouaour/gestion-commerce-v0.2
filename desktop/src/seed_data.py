from src.models.database import SessionLocal, Base, engine
from src.models.user import User, UserRole
from src.models.product import Category, Product
from src.models.finance import CashRegister, CashTransaction, TransactionType
from src.models.sale_parcel import Sale, SaleItem, Parcel, ParcelStatus
from datetime import datetime, timedelta
import random
from argon2 import PasswordHasher

ph = PasswordHasher()

def seed():
    db = SessionLocal()
    try:
        # 1. Users
        cashier = db.query(User).filter(User.username == 'caissier').first()
        if not cashier:
            cashier = User(username='caissier', hashed_password=ph.hash('caissier123'), role=UserRole.CASHIER)
            db.add(cashier)
            db.flush()

        # 2. Categories
        cats = ['Électronique', 'Alimentation', 'Vêtements', 'Hygiène']
        cat_objs = []
        for name in cats:
            cat = db.query(Category).filter(Category.name == name).first()
            if not cat:
                cat = Category(name=name)
                db.add(cat)
            cat_objs.append(cat)
        db.flush()

        # 3. Products
        prods = [
            ('iPhone 15', 'BAR-001', 150000.0, 10, cat_objs[0]),
            ('Samsung S23', 'BAR-002', 120000.0, 15, cat_objs[0]),
            ('Pain de mie', 'BAR-003', 250.0, 50, cat_objs[1]),
            ('Lait 1L', 'BAR-004', 120.0, 100, cat_objs[1]),
            ('T-shirt Coton', 'BAR-005', 1500.0, 30, cat_objs[2]),
            ('Savon Liquide', 'BAR-006', 450.0, 20, cat_objs[3])
        ]
        prod_objs = []
        for name, sku, price, stock, cat in prods:
            prod = db.query(Product).filter(Product.sku == sku).first()
            if not prod:
                prod = Product(name=name, sku=sku, price=price, stock_quantity=stock, category_id=cat.id)
                db.add(prod)
            prod_objs.append(prod)
        db.flush()

        # 4. Cash Register
        register = db.query(CashRegister).first()
        if not register:
            register = CashRegister(current_balance=50000.0, is_open=True)
            db.add(register)
        db.flush()

        # 5. One Month of Sales
        start_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            date = start_date + timedelta(days=i)
            # 2 to 5 sales per day
            for _ in range(random.randint(2, 5)):
                total = 0
                sale = Sale(user_id=cashier.id, created_at=date)
                db.add(sale)
                db.flush()
                
                for _ in range(random.randint(1, 3)):
                    p = random.choice(prod_objs)
                    qty = random.randint(1, 2)
                    total += p.price * qty
                    item = SaleItem(sale_id=sale.id, product_id=p.id, quantity=qty, price_at_sale=p.price)
                    db.add(item)
                
                sale.total_amount = total
                tx = CashTransaction(register_id=register.id, amount=total, type=TransactionType.SALE, user_id=cashier.id, created_at=date, reason=f'Sale #{sale.id}')
                db.add(tx)
                register.current_balance += total

        # 6. Some Parcels
        for i in range(5):
            parcel = Parcel(
                client_name=f'Client {i}', 
                client_phone=f'055000000{i}', 
                client_address='Alger, Algérie', 
                user_id=cashier.id,
                status=random.choice([ParcelStatus.CREATED, ParcelStatus.DELIVERED]),
                total_amount=5000.0,
                is_money_collected=random.choice([True, False])
            )
            db.add(parcel)

        db.commit()
        print('Seed data generated successfully!')
    finally:
        db.close()

if __name__ == '__main__':
    seed()
