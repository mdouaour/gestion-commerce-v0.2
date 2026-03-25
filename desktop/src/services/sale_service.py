from sqlalchemy.orm import Session
from src.models.sale_parcel import Sale, SaleItem
from src.models.product import Product
from src.models.finance import CashRegister, CashTransaction, TransactionType
from src.models.user import AuditLog
import json

class SaleService:
    @staticmethod
    def create_sale(db: Session, user_id: int, items_data: list):
        try:
            register = db.query(CashRegister).first()
            if not register or not register.is_open:
                return None, 'CASH_REGISTER_CLOSED'

            total_amount = sum(item['quantity'] * item['price_at_sale'] for item in items_data)

            # 1. Update stock and check versions
            for item in items_data:
                product = db.query(Product).filter(Product.id == item['product_id']).with_for_update().first()
                if not product:
                    return None, 'PRODUCT_NOT_FOUND'
                
                if product.version != item['version']:
                    return None, 'OPTIMISTIC_LOCK_CONFLICT'
                
                if product.stock_quantity < item['quantity']:
                    return None, f'INSUFFICIENT_STOCK: {product.name}'
                    
                product.stock_quantity -= item['quantity']
                product.version += 1

            # 2. Create Sale Record
            sale = Sale(total_amount=total_amount, user_id=user_id)
            db.add(sale)
            db.flush() # Get sale.id

            # 3. Create Sale Items
            for item in items_data:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price_at_sale=item['price_at_sale']
                )
                db.add(sale_item)

            # 4. Create Cash Transaction and Update Balance
            cash_tx = CashTransaction(
                register_id=register.id,
                amount=total_amount,
                type=TransactionType.SALE,
                reason=f'Sale #{sale.id}',
                user_id=user_id
            )
            db.add(cash_tx)
            db.flush() # Get cash_tx.id
            
            sale.cash_transaction_id = cash_tx.id
            register.current_balance += total_amount
            
            # 5. Audit Log
            log = AuditLog(user_id=user_id, action='sale_created', table_name='sales', row_id=sale.id, details=f'Total: {total_amount}')
            db.add(log)
            
            db.commit()
            return sale, None
        except Exception as e:
            db.rollback()
            return None, f'SALE_ERROR: {str(e)}'
