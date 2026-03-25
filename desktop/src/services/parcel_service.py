from sqlalchemy.orm import Session
from src.models.sale_parcel import Parcel, ParcelItem, ParcelStatus
from src.models.product import Product
from src.models.user import AuditLog
import json

class ParcelService:
    @staticmethod
    def create_parcel(db: Session, client_name: str, client_phone: str, client_address: str, items_data: list, shipping_fee: float, user_id: int):
        try:
            total_items_amount = sum(item['quantity'] * item['price_at_sale'] for item in items_data)
            total_amount = total_items_amount + shipping_fee
            
            # 1. Check Stock and Create Items
            for item in items_data:
                product = db.query(Product).filter(Product.id == item['product_id']).with_for_update().first()
                if not product or product.stock_quantity < item['quantity']:
                    return None, f'INSUFFICIENT_STOCK: {product.name if product else "Unknown"}'
                product.stock_quantity -= item['quantity']
                product.version += 1
                
            # 2. Create Parcel Record
            parcel = Parcel(
                client_name=client_name,
                client_phone=client_phone,
                client_address=client_address,
                total_amount=total_amount,
                shipping_fee=shipping_fee,
                user_id=user_id,
                status=ParcelStatus.CREATED
            )
            db.add(parcel)
            db.flush() # Get parcel.id
            
            # 3. Create Parcel Items
            for item in items_data:
                parcel_item = ParcelItem(
                    parcel_id=parcel.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price_at_sale=item['price_at_sale']
                )
                db.add(parcel_item)
                
            # 4. Audit Log
            log = AuditLog(user_id=user_id, action='parcel_created', table_name='parcels', row_id=parcel.id, details=f'Client: {client_name}, Total: {total_amount}')
            db.add(log)
            
            db.commit()
            return parcel, None
        except Exception as e:
            db.rollback()
            return None, f'PARCEL_ERROR: {str(e)}'

    @staticmethod
    def update_parcel_status(db: Session, parcel_id: int, status: ParcelStatus, user_id: int):
        parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
        if not parcel:
            return None, 'PARCEL_NOT_FOUND'
            
        parcel.status = status
        log = AuditLog(user_id=user_id, action='parcel_status_updated', table_name='parcels', row_id=parcel.id, details=f'New Status: {status}')
        db.add(log)
        db.commit()
        return parcel, None

    @staticmethod
    def collect_parcel_money(db: Session, parcel_id: int, collected_amount: float, user_id: int):
        parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
        if not parcel:
            return None, 'PARCEL_NOT_FOUND'
            
        parcel.is_money_collected = True
        parcel.collected_amount = collected_amount
        log = AuditLog(user_id=user_id, action='parcel_money_collected', table_name='parcels', row_id=parcel.id, details=f'Collected: {collected_amount}')
        db.add(log)
        db.commit()
        return parcel, None
