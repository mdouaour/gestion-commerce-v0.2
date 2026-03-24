from sqlalchemy.orm import Session
from src.models.finance import CashRegister, CashTransaction, TransactionType, Withdrawal
from src.models.user import AuditLog
from datetime import datetime

class FinanceService:
    @staticmethod
    def open_register(db: Session, user_id: int):
        register = db.query(CashRegister).first()
        if not register:
            register = CashRegister(current_balance=0.0, is_open=True, last_opened_at=datetime.now())
            db.add(register)
        elif not register.is_open:
            register.is_open = True
            register.last_opened_at = datetime.now()
            
        log = AuditLog(user_id=user_id, action='register_opened')
        db.add(log)
        db.commit()
        return register

    @staticmethod
    def close_register(db: Session, user_id: int):
        register = db.query(CashRegister).first()
        if register and register.is_open:
            register.is_open = False
            
        log = AuditLog(user_id=user_id, action='register_closed')
        db.add(log)
        db.commit()
        return register

    @staticmethod
    def create_withdrawal(db: Session, amount: float, reason: str, admin_id: int):
        register = db.query(CashRegister).first()
        if not register:
            return None, 'CASH_REGISTER_NOT_FOUND'
            
        if register.current_balance < amount:
            return None, 'INSUFFICIENT_FUNDS'
            
        # 1. Create Withdrawal Record
        withdrawal = Withdrawal(amount=amount, reason=reason, admin_id=admin_id)
        db.add(withdrawal)
        db.flush() # Get withdrawal.id
        
        # 2. Create Cash Transaction and Update Balance
        cash_tx = CashTransaction(
            register_id=register.id,
            amount=-amount, # Negative for withdrawal
            type=TransactionType.WITHDRAWAL,
            reason=f'Withdrawal #{withdrawal.id}: {reason}',
            user_id=admin_id
        )
        db.add(cash_tx)
        
        register.current_balance -= amount
        
        # 3. Audit Log
        log = AuditLog(user_id=admin_id, action='withdrawal_created', table_name='withdrawals', row_id=withdrawal.id, details=f'Amount: {amount}, Reason: {reason}')
        db.add(log)
        
        db.commit()
        return withdrawal, None
