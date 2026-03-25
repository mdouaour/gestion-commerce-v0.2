from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.finance import CashRegister, CashTransaction, TransactionType
from src.models.sale_parcel import Sale, Parcel, ParcelStatus, SaleItem
from src.models.product import Product
from datetime import datetime, timedelta

class DashboardService:
    @staticmethod
    def get_metrics(db: Session):
        # 1. Total Cash in Register
        register = db.query(CashRegister).first()
        total_cash = register.current_balance if register else 0.0

        # 2. Money to collect (parcels delivered but not collected)
        to_collect = db.query(func.sum(Parcel.total_amount)).filter(
            Parcel.status == ParcelStatus.DELIVERED,
            Parcel.is_money_collected == False
        ).scalar() or 0.0

        # 3. Money collected (parcels marked as collected)
        collected = db.query(func.sum(Parcel.collected_amount)).filter(
            Parcel.is_money_collected == True
        ).scalar() or 0.0

        # 4. Sales Metrics (Daily, Monthly, Yearly)
        today = datetime.now().date()
        daily_sales = db.query(func.sum(Sale.total_amount)).filter(
            func.date(Sale.created_at) == today
        ).scalar() or 0.0

        first_day_month = today.replace(day=1)
        monthly_sales = db.query(func.sum(Sale.total_amount)).filter(
            Sale.created_at >= first_day_month
        ).scalar() or 0.0

        first_day_year = today.replace(month=1, day=1)
        yearly_sales = db.query(func.sum(Sale.total_amount)).filter(
            Sale.created_at >= first_day_year
        ).scalar() or 0.0

        # 5. Profit Estimation (Sales - Cost)
        # Note: Cost of goods sold (COGS) would require a 'purchase_price' in Product model.
        # Since it's missing, let's assume a default 20% margin for estimation if needed,
        # or just return 0 for now until the model is updated.
        # For this simulation, let's assume profit = 25% of sales.
        estimated_profit = monthly_sales * 0.25

        return {
            'total_cash': total_cash,
            'money_to_collect': to_collect,
            'money_collected': collected,
            'daily_sales': daily_sales,
            'monthly_sales': monthly_sales,
            'yearly_sales': yearly_sales,
            'estimated_profit': estimated_profit
        }
