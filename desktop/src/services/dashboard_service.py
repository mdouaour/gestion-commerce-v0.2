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

        estimated_profit = monthly_sales * 0.25

        # 5. Low Stock Count
        low_stock_count = db.query(func.count(Product.id)).filter(
            Product.stock_quantity < 5
        ).scalar() or 0

        # 6. Separate Revenue Today
        in_store_today = db.query(func.sum(Sale.total_amount)).filter(
            func.date(Sale.created_at) == today,
            Sale.is_cancelled == False
        ).scalar() or 0.0

        parcel_today = db.query(func.sum(Parcel.collected_amount)).filter(
            func.date(Parcel.updated_at) == today, # Use updated_at for collection date
            Parcel.is_money_collected == True
        ).scalar() or 0.0

        return {
            'total_cash': total_cash,
            'money_to_collect': to_collect,
            'money_collected': collected,
            'daily_sales': in_store_today + parcel_today,
            'in_store_today': in_store_today,
            'parcel_today': parcel_today,
            'monthly_sales': monthly_sales,
            'yearly_sales': yearly_sales,
            'estimated_profit': estimated_profit,
            'low_stock_count': low_stock_count
        }

    @staticmethod
    def get_sales_trend(db: Session, days=30):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 1. In-store Sales
        sales_results = db.query(
            func.date(Sale.created_at).label('date'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            Sale.created_at >= start_date,
            Sale.is_cancelled == False
        ).group_by(
            func.date(Sale.created_at)
        ).all()

        # 2. Collected Parcels
        parcel_results = db.query(
            func.date(Parcel.updated_at).label('date'),
            func.sum(Parcel.collected_amount).label('total')
        ).filter(
            Parcel.updated_at >= start_date,
            Parcel.is_money_collected == True
        ).group_by(
            func.date(Parcel.updated_at)
        ).all()
        
        date_map = {}
        for r in sales_results:
            d_key = r.date.isoformat() if hasattr(r.date, 'isoformat') else str(r.date)
            date_map[d_key] = date_map.get(d_key, 0.0) + r.total

        for r in parcel_results:
            d_key = r.date.isoformat() if hasattr(r.date, 'isoformat') else str(r.date)
            date_map[d_key] = date_map.get(d_key, 0.0) + r.total
        
        dates = []
        values = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            ds = d.isoformat()
            dates.append(d.strftime('%m-%d'))
            values.append(date_map.get(ds, 0.0))
            
        return dates, values
