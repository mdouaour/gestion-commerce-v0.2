import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.cashier_window import CashierWindow
from src.models.user import User, UserRole
from src.models.product import Product
from unittest.mock import MagicMock, patch
import sys

@pytest.fixture
def app(qtbot):
    return QApplication.instance() or QApplication(sys.argv)

@pytest.fixture
def mock_user():
    return User(id=1, username='cashier1', role=UserRole.CASHIER)

@pytest.fixture
def mock_products():
    return [
        Product(id=1, name='Milk', sku='123', price=1.5, stock_quantity=10, version=1),
        Product(id=2, name='Bread', sku='456', price=2.0, stock_quantity=5, version=1)
    ]

def test_cashier_window_init(qtbot, mock_user):
    with patch('src.models.database.SessionLocal'), \
         patch('src.ui.cashier_window.CashierWindow.load_products'):
        window = CashierWindow(mock_user)
        qtbot.addWidget(window)
        window.show()
        # In some CI environments, focus might not be reliable, 
        # but let's try to wait a bit.
        qtbot.waitUntil(lambda: window.search_input.hasFocus(), timeout=1000)
        assert "Cashier Terminal" in window.windowTitle()
        assert window.search_input.hasFocus()

def test_add_to_cart_scanner(qtbot, mock_user, mock_products):
    with patch('src.models.database.SessionLocal'), \
         patch('src.ui.cashier_window.CashierWindow.load_products'):
        window = CashierWindow(mock_user)
        window.all_products = mock_products
        qtbot.addWidget(window)
        
        # Simulate barcode scan
        qtbot.keyClicks(window.search_input, '123')
        # Exact SKU match should add to cart and clear search
        assert len(window.cart) == 1
        assert window.cart[0]['product'].name == 'Milk'
        assert window.search_input.text() == ''

def test_cart_total_calculation(qtbot, mock_user, mock_products):
    with patch('src.models.database.SessionLocal'), \
         patch('src.ui.cashier_window.CashierWindow.load_products'):
        window = CashierWindow(mock_user)
        window.all_products = mock_products
        qtbot.addWidget(window)
        
        window.add_to_cart(mock_products[0], 2) # 2 * 1.5 = 3.0
        window.add_to_cart(mock_products[1], 1) # 1 * 2.0 = 2.0
        
        assert window.total_label.text() == "5.00 DZD"

def test_remove_item_from_cart(qtbot, mock_user, mock_products):
    with patch('src.models.database.SessionLocal'), \
         patch('src.ui.cashier_window.CashierWindow.load_products'):
        window = CashierWindow(mock_user)
        window.all_products = mock_products
        qtbot.addWidget(window)
        
        window.add_to_cart(mock_products[0], 1)
        assert len(window.cart) == 1
        
        window.remove_cart_item(0)
        assert len(window.cart) == 0
        assert window.total_label.text() == "0.00 DZD"

def test_rbac_routing_logic():
    from src.main import POSApplication
    pos_app = POSApplication()
    
    admin = User(username='admin', role=UserRole.ADMIN)
    cashier = User(username='cashier', role=UserRole.CASHIER)
    
    with patch('src.main.DashboardWindow') as mock_dash, \
         patch('src.main.CashierWindow') as mock_cash, \
         patch('src.main.LoginWindow'):
        
        pos_app.show_main_ui(admin)
        assert mock_dash.called
        
        pos_app.show_main_ui(cashier)
        assert mock_cash.called
