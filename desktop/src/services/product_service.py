from sqlalchemy.orm import Session
from src.models.product import Product, Category, SyncQueue
from src.models.user import AuditLog
import json

class ProductService:
    @staticmethod
    def get_all_products(db: Session):
        return db.query(Product).all()

    @staticmethod
    def get_product_by_sku(db: Session, sku: str):
        return db.query(Product).filter(Product.sku == sku).first()

    @staticmethod
    def create_product(db: Session, name: str, sku: str, price: float, stock: int, category_id: int, user_id: int):
        product = Product(
            name=name,
            sku=sku,
            price=price,
            stock_quantity=stock,
            category_id=category_id
        )
        db.add(product)
        db.flush() # Get ID
        
        # Audit Log
        log = AuditLog(user_id=user_id, action='product_created', table_name='products', row_id=product.id, details=f'Name: {name}, SKU: {sku}')
        db.add(log)
        
        # Sync Queue
        sync = SyncQueue(table_name='products', row_id=product.id, operation='INSERT', data=json.dumps({'name': name, 'sku': sku, 'price': price, 'stock': stock, 'category_id': category_id}))
        db.add(sync)
        
        db.commit()
        return product

    @staticmethod
    def update_stock(db: Session, product_id: int, quantity_change: int, expected_version: int, user_id: int):
        product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
        if not product:
            return None, 'PRODUCT_NOT_FOUND'
        
        if product.version != expected_version:
            return None, 'OPTIMISTIC_LOCK_CONFLICT'
        
        if product.stock_quantity + quantity_change < 0:
            return None, 'INSUFFICIENT_STOCK'
            
        product.stock_quantity += quantity_change
        product.version += 1
        
        log = AuditLog(user_id=user_id, action='stock_updated', table_name='products', row_id=product.id, details=f'Change: {quantity_change}, New Total: {product.stock_quantity}')
        db.add(log)
        
        db.commit()
        return product, None
