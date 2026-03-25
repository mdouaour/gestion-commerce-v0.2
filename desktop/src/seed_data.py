import sys
import os

# Ensure we use the correct PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        # Admin is already created by init_db.py, but let's ensure it's here
        admin = db.query(User).filter(User.username == 'admin').first()
        if not admin:
            admin = User(username='admin', hashed_password=ph.hash('admin123'), role=UserRole.ADMIN)
            db.add(admin)
            
        cashier = db.query(User).filter(User.username == 'cashier').first()
        if not cashier:
            cashier = User(username='cashier', hashed_password=ph.hash('cashier123'), role=UserRole.CASHIER)
            db.add(cashier)
        db.flush()

        # 2. Categories (Realistic for Algerian store)
        cats = ['Alimentation Générale', 'Boissons', 'Produits Laitiers', 'Entretien & Hygiène', 'Cosmétiques', 'Électroménager']
        cat_objs = []
        for name in cats:
            cat = db.query(Category).filter(Category.name == name).first()
            if not cat:
                cat = Category(name=name)
                db.add(cat)
            cat_objs.append(cat)
        db.flush()

        # 3. Products (30+ products with realistic DZD prices)
        product_list = [
            # Alimentation Générale
            ('Pâtes 500g', 'ALIM-001', 120.0, 100, cats[0]),
            ('Couscous 1kg', 'ALIM-002', 250.0, 50, cats[0]),
            ('Huile 5L', 'ALIM-003', 650.0, 20, cats[0]),
            ('Sucre 1kg', 'ALIM-004', 95.0, 200, cats[0]),
            ('Café 250g', 'ALIM-005', 350.0, 40, cats[0]),
            # Boissons
            ('Hamoud Boualem 1.5L', 'BOIS-001', 120.0, 60, cats[1]),
            ('Eau Minérale 1.5L', 'BOIS-002', 40.0, 300, cats[1]),
            ('Jus Ramy 1L', 'BOIS-003', 180.0, 80, cats[1]),
            ('Ifri 1.5L', 'BOIS-004', 45.0, 150, cats[1]),
            # Produits Laitiers
            ('Lait Candia 1L', 'LAIT-001', 140.0, 100, cats[2]),
            ('Fromage Portion x16', 'LAIT-002', 320.0, 50, cats[2]),
            ('Yaourt Nature', 'LAIT-003', 25.0, 200, cats[2]),
            ('Beurre 200g', 'LAIT-004', 280.0, 30, cats[2]),
            # Entretien & Hygiène
            ('Lessive Ariel 2kg', 'HYG-001', 1200.0, 15, cats[3]),
            ('Eau de Javel 2L', 'HYG-002', 150.0, 40, cats[3]),
            ('Savon Marseille', 'HYG-003', 80.0, 100, cats[3]),
            ('Liquide Vaisselle', 'HYG-004', 220.0, 30, cats[3]),
            # Cosmétiques
            ('Shampooing Elseve', 'COS-001', 650.0, 20, cats[4]),
            ('Dentifrice Signal', 'COS-002', 250.0, 40, cats[4]),
            ('Déodorant Nivea', 'COS-003', 550.0, 15, cats[4]),
            # Électroménager
            ('Mixeur Moulinex', 'ELEC-001', 4500.0, 5, cats[5]),
            ('Fer à repasser', 'ELEC-002', 3800.0, 8, cats[5]),
            ('Bouilloire électrique', 'ELEC-003', 2500.0, 10, cats[5])
        ]
        
        prod_objs = []
        for name, sku, price, stock, cat_name in product_list:
            cat = next(c for c in cat_objs if c.name == cat_name)
            prod = db.query(Product).filter(Product.sku == sku).first()
            if not prod:
                prod = Product(name=name, sku=sku, price=price, stock_quantity=stock, category_id=cat.id)
                db.add(prod)
            prod_objs.append(prod)
        db.flush()

        # 4. Cash Register
        register = db.query(CashRegister).first()
        if not register:
            register = CashRegister(current_balance=100000.0, is_open=True)
            db.add(register)
        db.flush()

        # 5. Three Months of Sales (approx 90 days)
        start_date = datetime.now() - timedelta(days=90)
        users = [admin, cashier]
        
        for i in range(90):
            date = start_date + timedelta(days=i)
            # Peak sales on weekends (Friday/Saturday in Algeria)
            num_sales = random.randint(3, 8) if date.weekday() in [4, 5] else random.randint(2, 5)
            
            for _ in range(num_sales):
                user = random.choice(users)
                total = 0
                sale = Sale(user_id=user.id, created_at=date)
                db.add(sale)
                db.flush()
                
                # Each sale has 1-5 items
                for _ in range(random.randint(1, 5)):
                    p = random.choice(prod_objs)
                    qty = random.randint(1, 3)
                    total += p.price * qty
                    item = SaleItem(sale_id=sale.id, product_id=p.id, quantity=qty, price_at_sale=p.price)
                    db.add(item)
                
                sale.total_amount = total
                tx = CashTransaction(
                    register_id=register.id, 
                    amount=total, 
                    type=TransactionType.SALE, 
                    user_id=user.id, 
                    created_at=date, 
                    reason=f'Vente #{sale.id}'
                )
                db.add(tx)
                register.current_balance += total

        # 6. Parcels
        clients = ['Ahmed Mansour', 'Sami Belkacem', 'Karima Ouali', 'Yacine Brahimi', 'Lydia Haddad']
        for i in range(15):
            user = random.choice(users)
            status = random.choice(list(ParcelStatus))
            is_collected = (status == ParcelStatus.DELIVERED and random.random() > 0.3)
            
            parcel = Parcel(
                client_name=random.choice(clients), 
                client_phone=f'0550{random.randint(100000, 999999)}', 
                client_address='Alger, Algérie', 
                user_id=user.id,
                status=status,
                total_amount=float(random.randint(2000, 15000)),
                is_money_collected=is_collected,
                collected_amount=0.0 if not is_collected else 0.0 # Will be updated in dashboard logic
            )
            db.add(parcel)

        db.commit()
        print('Realistic seed data (3 months) generated successfully!')
    finally:
        db.close()

if __name__ == '__main__':
    seed()
