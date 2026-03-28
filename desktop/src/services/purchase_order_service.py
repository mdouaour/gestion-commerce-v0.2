from sqlalchemy.orm import Session, joinedload
from src.models.purchase_order import PurchaseOrder, PurchaseOrderItem, POStatus
from src.models.product import Product
from src.models.user import AuditLog, User, UserRole
import json

class POService:
    @staticmethod
    def get_all_pos(db: Session):
        return db.query(PurchaseOrder).options(joinedload(PurchaseOrder.user)).all()

    @staticmethod
    def create_po(db: Session, supplier_name: str, items_data: list, user_id: int):
        try:
            total_amount = sum(item['quantity'] * item['purchase_price'] for item in items_data)
            
            po = PurchaseOrder(
                supplier_name=supplier_name,
                total_amount=total_amount,
                user_id=user_id,
                status=POStatus.DRAFT
            )
            db.add(po)
            db.flush()
            
            for item in items_data:
                po_item = PurchaseOrderItem(
                    po_id=po.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    purchase_price=item['purchase_price'],
                    selling_price=item['selling_price']
                )
                db.add(po_item)
                
            log = AuditLog(user_id=user_id, action='po_created', table_name='purchase_orders', row_id=po.id)
            db.add(log)
            db.commit()
            return po, None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def receive_po(db: Session, po_id: int, user_id: int):
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or user.role != UserRole.ADMIN:
                return False, 'UNAUTHORIZED_ACTION'

            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).with_for_update().first()
            if not po:
                return False, 'PO_NOT_FOUND'
            
            if po.status != POStatus.DRAFT:
                return False, 'PO_ALREADY_PROCESSED'

            # Update stock and selling prices
            for item in po.items:
                product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
                if product:
                    product.stock_quantity += item.quantity
                    product.price = item.selling_price # Update selling price to the one in PO
                    product.version += 1

            po.status = POStatus.DELIVERED
            log = AuditLog(user_id=user_id, action='po_received', table_name='purchase_orders', row_id=po.id)
            db.add(log)
            db.commit()
            return True, None
        except Exception as e:
            db.rollback()
            return False, str(e)

    @staticmethod
    def pay_po(db: Session, po_id: int, user_id: int):
        # As per requirement: "Payment external (no system cash impact)"
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            return False, 'PO_NOT_FOUND'
        
        po.status = POStatus.PAID
        db.commit()
        return True, None
