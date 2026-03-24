import pytest
from app.services.finance_service import FinanceService
from app.schemas.finance import WithdrawalCreate
from app.models.finance import TransactionType
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.models.user import UserRole
from app.core.config import settings

@pytest.mark.asyncio
async def test_finance_service(db_session):
    # Setup user
    user_in = UserCreate(username="fin_user", email="fin@ex.com", full_name="Fin User", password="pass")
    user = await UserService.create(db_session, user_in)
    
    # 1. Test initial register
    register = await FinanceService.get_or_create_register(db_session)
    assert register.current_balance == 0.0
    
    # 2. Test deposit
    await FinanceService.add_transaction(
        db_session, amount=100.0, type=TransactionType.DEPOSIT, reason="Initial cash", user_id=user.id
    )
    assert register.current_balance == 100.0
    
    # 3. Test withdrawal
    withdrawal_in = WithdrawalCreate(amount=30.0, reason="Buying office supplies")
    withdrawal = await FinanceService.create_withdrawal(db_session, withdrawal_in, user.id)
    assert withdrawal.amount == 30.0
    assert register.current_balance == 70.0
    
    # 4. Test insufficient funds
    with pytest.raises(ValueError, match="Insufficient funds"):
        fail_withdrawal = WithdrawalCreate(amount=100.0, reason="Too much")
        await FinanceService.create_withdrawal(db_session, fail_withdrawal, user.id)

@pytest.mark.asyncio
async def test_finance_api(client, db_session):
    # 1. Create admin and login
    admin_in = UserCreate(
        username="admin_fin",
        email="admin_fin@example.com",
        full_name="Admin Fin",
        password="password123",
        role=UserRole.ADMIN
    )
    admin = await UserService.create(db_session, admin_in)
    
    login_data = {"username": "admin_fin", "password": "password123"}
    response = await client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Add some money via service first to test withdrawal API
    await FinanceService.add_transaction(
        db_session, amount=500.0, type=TransactionType.DEPOSIT, reason="Seed", user_id=admin.id
    )
    
    # 3. Test GET register
    response = await client.get(f"{settings.API_V1_STR}/finance/register", headers=headers)
    assert response.status_code == 200
    assert response.json()["current_balance"] == 500.0
    
    # 4. Test POST withdraw
    withdraw_data = {"amount": 50.0, "reason": "Test Withdrawal"}
    response = await client.post(f"{settings.API_V1_STR}/finance/withdraw", json=withdraw_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["amount"] == 50.0
    
    # 5. Verify balance
    response = await client.get(f"{settings.API_V1_STR}/finance/register", headers=headers)
    assert response.json()["current_balance"] == 450.0
