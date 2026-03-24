from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.translator import translator
from src.ui.styles import get_main_style
from src.ui.sales_window import SalesTerminal
from src.ui.product_window import ProductManagement
from src.ui.parcel_window import ParcelManagement
from src.ui.finance_window import FinanceManagement

class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
        translator.language_changed.connect(self.update_ui_text)

    def init_ui(self):
        self.setWindowTitle(translator.translate('dashboard.title'))
        self.setMinimumSize(1100, 800)
        self.setStyleSheet(get_main_style(translator.current_lang == 'ar'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2c3e50; border-right: 1px solid #dcdde1;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.sidebar_label = QLabel("POS MENU")
        self.sidebar_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px; margin-bottom: 20px;")
        self.sidebar_layout.addWidget(self.sidebar_label)

        # Sidebar buttons
        self.btn_dashboard = QPushButton(translator.translate('dashboard.title'))
        self.btn_sales = QPushButton(translator.translate('dashboard.sales'))
        self.btn_products = QPushButton(translator.translate('products.title') if hasattr(translator, 'translate') else "Products")
        self.btn_parcels = QPushButton(translator.translate('parcels.title') if hasattr(translator, 'translate') else "Parcels")
        self.btn_finance = QPushButton(translator.translate('finance.title') if hasattr(translator, 'translate') else "Finance")
        self.btn_admin = QPushButton("Admin")

        self.nav_btns = [self.btn_dashboard, self.btn_sales, self.btn_products, self.btn_parcels, self.btn_finance, self.btn_admin]
        
        for i, btn in enumerate(self.nav_btns):
            btn.setStyleSheet("text-align: left; background: transparent; color: #ecf0f1; border: none; padding: 10px;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self.content_stack.setCurrentIndex(idx))
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()
        
        self.logout_btn = QPushButton(translator.translate('dashboard.logoutButton'))
        self.logout_btn.setObjectName('danger')
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        self.sidebar_layout.addWidget(self.logout_btn)

        self.main_layout.addWidget(self.sidebar)

        # Main Content Area
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # Page 0: Welcome
        self.welcome_page = QWidget()
        self.welcome_layout = QVBoxLayout(self.welcome_page)
        self.welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label = QLabel(translator.translate('dashboard.welcomeMessage', username=self.user.username))
        self.welcome_label.setObjectName('header')
        self.role_label = QLabel(translator.translate('dashboard.roleInfo', role=self.user.role))
        self.welcome_layout.addWidget(self.welcome_label)
        self.welcome_layout.addWidget(self.role_label)
        self.content_stack.addWidget(self.welcome_page)

        # Page 1: Sales
        self.sales_page = SalesTerminal(self.user)
        self.content_stack.addWidget(self.sales_page)

        # Page 2: Products
        self.products_page = ProductManagement(self.user)
        self.content_stack.addWidget(self.products_page)

        # Page 3: Parcels
        self.parcels_page = ParcelManagement(self.user)
        self.content_stack.addWidget(self.parcels_page)

        # Page 4: Finance
        self.finance_page = FinanceManagement(self.user)
        self.content_stack.addWidget(self.finance_page)

        # Page 5: Admin
        self.admin_page = QWidget()
        layout = QVBoxLayout(self.admin_page)
        layout.addWidget(QLabel("Admin Module - Coming Soon"))
        self.content_stack.addWidget(self.admin_page)

        self.update_layout_direction(translator.current_lang)

    def update_ui_text(self, lang):
        self.setWindowTitle(translator.translate('dashboard.title'))
        self.btn_dashboard.setText(translator.translate('dashboard.title'))
        self.btn_sales.setText(translator.translate('dashboard.sales'))
        self.btn_products.setText(translator.translate('products.title'))
        self.btn_parcels.setText(translator.translate('parcels.title'))
        self.btn_finance.setText(translator.translate('finance.title'))
        self.welcome_label.setText(translator.translate('dashboard.welcomeMessage', username=self.user.username))
        self.role_label.setText(translator.translate('dashboard.roleInfo', role=self.user.role))
        self.logout_btn.setText(translator.translate('dashboard.logoutButton'))
        self.setStyleSheet(get_main_style(lang == 'ar'))
        self.update_layout_direction(lang)

    def update_layout_direction(self, lang):
        if lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
