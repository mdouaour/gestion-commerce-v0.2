import pytest
from app.services.parcel_service import ParcelService
from app.schemas.parcel import ParcelCreate, ParcelItemCreate
from app.models.parcel import ParcelStatus
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.schemas.user import UserCreate
from app.schemas.product import CategoryCreate, ProductCreate
from app.core.config import settings

@pytest.mark.asyncio
async def test_parcel_lifecycle(db_session):
    # Setup: User, Category, Product
    user_in = UserCreate(username="parcel_user", email="p@ex.com", full_name="P User", password="pass")
    user = await UserService.create(db_session, user_in)
    
    cat_in = CategoryCreate(name="Bags")
    cat = await CategoryService.create(db_session, cat_in)
    
    prod_in = ProductCreate(name="Backpack", sku="BP-01", price=50.0, stock_quantity=10, category_id=cat.id)
    prod = await ProductService.create(db_session, prod_in)
    
    # 1. Create Parcel
    parcel_in = ParcelCreate(
        client_name="John Doe",
        client_phone="123456",
        client_address="Main St",
        shipping_fee=5.0,
        items=[ParcelItemCreate(product_id=prod.id, quantity=2, price_at_sale=50.0)]
    )
    parcel = await ParcelService.create(db_session, parcel_in, user.id)
    
    assert parcel.total_amount == 105.0 # (2 * 50) + 5
    assert parcel.status == ParcelStatus.CREATED
    
    # Verify stock reduction
    await db_session.refresh(prod)
    assert prod.stock_quantity == 8
    
    # 2. Update to Delivered
    updated = await ParcelService.update_status(db_session, parcel.id, ParcelStatus.DELIVERED, user.id)
    assert updated.is_money_collected is True
    assert updated.collected_amount == 105.0
    
    # 3. Test Return logic
    # Re-create another parcel to return it
    p2_in = ParcelCreate(
        client_name="Jane", client_phone="999", client_address="Road", shipping_fee=0,
        items=[ParcelItemCreate(product_id=prod.id, quantity=1, price_at_sale=50.0)]
    )
    p2 = await ParcelService.create(db_session, p2_in, user.id)
    await db_session.refresh(prod)
    assert prod.stock_quantity == 7
    
    # Return it
    returned = await ParcelService.update_status(db_session, p2.id, ParcelStatus.RETURNED, user.id)
    assert returned.status == ParcelStatus.RETURNED
    
    # Verify stock restored
    await db_session.refresh(prod)
    assert prod.stock_quantity == 8

@pytest.mark.asyncio
async def test_parcel_api(client, db_session):
    # Login and setup
    admin_in = UserCreate(username="admin_p", email="ap@ex.com", full_name="Admin P", password="pass", role="admin")
    admin = await UserService.create(db_session, admin_in)
    
    login_data = {"username": "admin_p", "password": "pass"}
    response = await client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    cat = await CategoryService.create(db_session, CategoryCreate(name="API Cat"))
    prod = await ProductService.create(db_session, ProductCreate(name="API Prod", sku="API-01", price=10, stock_quantity=10, category_id=cat.id))
    
    # API Create Parcel
    parcel_data = {
        "client_name": "API Client",
        "client_phone": "000",
        "client_address": "API St",
        "shipping_fee": 10,
        "items": [{"product_id": prod.id, "quantity": 1, "price_at_sale": 10}]
    }
    response = await client.post(f"{settings.API_V1_STR}/parcels/", json=parcel_data, headers=headers)
    assert response.status_code == 200
    parcel_id = response.json()["id"]
    
    # API Update Status
    response = await client.put(f"{settings.API_V1_STR}/parcels/{parcel_id}/status?status=delivered", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "delivered"
    assert response.json()["is_money_collected"] is True
