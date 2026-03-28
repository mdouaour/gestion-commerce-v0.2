from sqlalchemy import String
from sqlalchemy.orm import Session, joinedload
from src.models.sale_parcel import Parcel, ParcelItem, ParcelStatus
from src.models.product import Product
from src.models.user import AuditLog
import json

class ParcelService:
    @staticmethod
    def get_all_parcels(db: Session):
        return db.query(Parcel).options(joinedload(Parcel.user)).order_by(Parcel.created_at.desc()).all()

    @staticmethod
    def search_parcels(db: Session, query: str):
        return db.query(Parcel).options(joinedload(Parcel.user)).filter(
            (Parcel.client_name.ilike(f'%{query}%')) |
            (Parcel.client_phone.ilike(f'%{query}%')) |
            (Parcel.id.cast(String).ilike(f'%{query}%'))
        ).order_by(Parcel.created_at.desc()).all()

    @staticmethod
    def validate_parcel(db: Session, parcel_id: int, user_id: int):
        """Validate a parcel (mark as delivered and ensure money is collected if required)."""
        parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
        if not parcel:
            return None, 'PARCEL_NOT_FOUND'
        
        parcel.status = ParcelStatus.DELIVERED
        # Note: Money collection is usually a separate step, but validation implies it's ready.
        
        log = AuditLog(user_id=user_id, action='parcel_validated', table_name='parcels', row_id=parcel.id, details='Parcel validated/marked as delivered')
        db.add(log)
        db.commit()
        return parcel, None

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
        from src.models.user import User, UserRole
        from src.models.finance import CashRegister, CashTransaction, TransactionType

        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.role != UserRole.ADMIN:
            return None, 'UNAUTHORIZED_ACTION'

        parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
        if not parcel:
            return None, 'PARCEL_NOT_FOUND'
            
        if parcel.is_money_collected:
            return None, 'ALREADY_COLLECTED'

        register = db.query(CashRegister).first()
        if not register or not register.is_open:
            return None, 'CASH_REGISTER_CLOSED'

        # 1. Mark as collected
        parcel.is_money_collected = True
        parcel.collected_amount = collected_amount
        parcel.status = ParcelStatus.DELIVERED # Automatically mark as delivered if not already?
        
        # 2. Update Cash Register
        register.current_balance += collected_amount
        
        # 3. Create Cash Transaction
        cash_tx = CashTransaction(
            register_id=register.id,
            amount=collected_amount,
            type=TransactionType.SALE, # Or a specific type for parcels
            reason=f'Parcel collection #{parcel.id} - Client: {parcel.client_name}',
            user_id=user_id
        )
        db.add(cash_tx)

        # 4. Audit Log
        log = AuditLog(user_id=user_id, action='parcel_money_collected', table_name='parcels', row_id=parcel.id, details=f'Collected: {collected_amount}')
        db.add(log)
        
        db.commit()
        return parcel, None
