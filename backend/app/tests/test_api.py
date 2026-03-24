import pytest
from app.core.config import settings
from app.models.user import UserRole

@pytest.mark.asyncio
async def test_api_flow(client, db_session):
    # 1. Create an admin user directly for testing
    from app.services.user_service import UserService
    from app.schemas.user import UserCreate
    
    admin_in = UserCreate(
        username="admin_api",
        email="admin_api@example.com",
        full_name="Admin API",
        password="password123",
        role=UserRole.ADMIN
    )
    await UserService.create(db_session, admin_in)
    
    # 2. Login
    login_data = {
        "username": "admin_api",
        "password": "password123"
    }
    # Form data for OAuth2
    response = await client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Get /me
    response = await client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin_api"
    
    # 4. Create Category
    cat_data = {"name": "Test Cat", "description": "Test Desc"}
    response = await client.post(f"{settings.API_V1_STR}/categories/", json=cat_data, headers=headers)
    assert response.status_code == 200
    cat_id = response.json()["id"]
    
    # 5. Create Product
    prod_data = {
        "name": "Test Prod",
        "sku": "TP-001",
        "price": 10.5,
        "stock_quantity": 5,
        "category_id": cat_id
    }
    response = await client.post(f"{settings.API_V1_STR}/products/", json=prod_data, headers=headers)
    assert response.status_code == 200
    prod_id = response.json()["id"]
    
    # 6. Adjust Stock
    adj_data = {"product_id": prod_id, "change_amount": 10, "reason": "Restock Test"}
    response = await client.post(f"{settings.API_V1_STR}/stock/adjust", json=adj_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 15
    
    # 7. Check History
    response = await client.get(f"{settings.API_V1_STR}/stock/history/{prod_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["change_amount"] == 10
