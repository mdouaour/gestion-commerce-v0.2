from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame, QComboBox, QScrollArea, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QEvent
from src.core.translator import translator
from src.ui.styles import get_main_style
from src.ui.sales_window import SalesTerminal
from src.ui.product_window import ProductManagement
from src.ui.parcel_window import ParcelManagement
from src.ui.finance_window import FinanceManagement
from src.ui.components.kpi_card import KPICard
from src.ui.components.charts import SalesTrendChart

from src.services.dashboard_service import DashboardService
from src.models.database import SessionLocal

class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
        self.setup_security()
        self.refresh_metrics()
        translator.language_changed.connect(self.update_ui_text)

    def init_ui(self):
        self.setWindowTitle(translator.translate('dashboard.title'))
        self.setMinimumSize(1250, 850)
        self.setStyleSheet(get_main_style(translator.current_lang == 'ar'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 25, 15, 25)
        self.sidebar_layout.setSpacing(8)

        self.sidebar_label = QLabel("G-POS SYSTEM")
        self.sidebar_label.setStyleSheet("color: white; font-weight: 800; font-size: 22px; margin-bottom: 40px; padding-left: 10px;")
        self.sidebar_layout.addWidget(self.sidebar_label)

        # Nav Buttons
        self.btn_dashboard = self._create_nav_btn("🏠 " + translator.translate('dashboard.title'), 0)
        self.btn_sales = self._create_nav_btn("🛒 " + translator.translate('dashboard.sales'), 1)
        self.btn_products = self._create_nav_btn("📦 " + translator.translate('products.title'), 2)
        self.btn_parcels = self._create_nav_btn("🚚 " + translator.translate('parcels.title'), 3)
        self.btn_finance = self._create_nav_btn("💰 " + translator.translate('finance.title'), 4)
        self.btn_admin = self._create_nav_btn("⚙️ System Admin", 5)

        self.nav_btns = [self.btn_dashboard, self.btn_sales, self.btn_products, self.btn_parcels, self.btn_finance, self.btn_admin]
        
        # RBAC
        if self.user.role != 'admin':
            self.btn_finance.hide()
            self.btn_admin.hide()

        self.sidebar_layout.addStretch()
        
        # Language Switcher
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['fr', 'ar', 'en'])
        self.lang_combo.setCurrentText(translator.current_lang)
        self.lang_combo.currentTextChanged.connect(translator.set_language)
        self.sidebar_layout.addWidget(QLabel("Lang:", styleSheet="color: #bdc3c7; font-size: 11px;"))
        self.sidebar_layout.addWidget(self.lang_combo)

        # Logout
        self.logout_btn = QPushButton(translator.translate('dashboard.logoutButton'))
        self.logout_btn.setObjectName('danger')
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        self.sidebar_layout.addWidget(self.logout_btn)

        self.main_layout.addWidget(self.sidebar)

        # --- MAIN CONTENT ---
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # PAGE 0: DASHBOARD OVERVIEW
        self.overview_page = QWidget()
        self.overview_layout = QVBoxLayout(self.overview_page)
        self.overview_layout.setContentsMargins(40, 40, 40, 40)
        self.overview_layout.setSpacing(25)
        
        header_box = QHBoxLayout()
        welcome_vbox = QVBoxLayout()
        self.welcome_label = QLabel(translator.translate('dashboard.welcomeMessage', username=self.user.username))
        self.welcome_label.setObjectName('header')
        self.role_label = QLabel(translator.translate('dashboard.roleInfo', role=self.user.role))
        self.role_label.setObjectName("subtitle")
        welcome_vbox.addWidget(self.welcome_label)
        welcome_vbox.addWidget(self.role_label)
        header_box.addLayout(welcome_vbox)
        header_box.addStretch()
        
        self.refresh_btn = QPushButton("↻ Refresh Data")
        self.refresh_btn.setFixedWidth(150)
        self.refresh_btn.clicked.connect(self.refresh_metrics)
        header_box.addWidget(self.refresh_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.overview_layout.addLayout(header_box)

        # KPI Cards Strip
        kpi_layout = QHBoxLayout()
        self.kpi_revenue = KPICard("REVENUE TODAY", "0.00", "#27ae60")
        self.kpi_cash = KPICard("CASH IN HAND", "0.00", "#2980b9")
        self.kpi_profit = KPICard("EST. PROFIT (MTD)", "0.00", "#8e44ad")
        self.kpi_low_stock = KPICard("LOW STOCK", "0", "#e67e22")
        
        kpi_layout.addWidget(self.kpi_revenue)
        kpi_layout.addWidget(self.kpi_cash)
        kpi_layout.addWidget(self.kpi_profit)
        kpi_layout.addWidget(self.kpi_low_stock)
        self.overview_layout.addLayout(kpi_layout)

        # Chart
        self.sales_chart = SalesTrendChart()
        self.overview_layout.addWidget(self.sales_chart)
        self.overview_layout.addStretch()

        self.content_stack.addWidget(self.overview_page)
        self.content_stack.addWidget(SalesTerminal(self.user))
        self.content_stack.addWidget(ProductManagement(self.user))
        self.content_stack.addWidget(ParcelManagement(self.user))
        self.content_stack.addWidget(FinanceManagement(self.user))
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self._set_active_nav(0)

    def setup_security(self):
        # 15 Minute Session Timeout
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.handle_timeout)
        self.session_timer.start(15 * 60 * 1000)
        self.central_widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.KeyPress):
            self.session_timer.start()
        return super().eventFilter(obj, event)

    def handle_timeout(self):
        self.status_bar.showMessage("Session expired. Logging out...")
        QTimer.singleShot(2000, self.logout_requested.emit)

    def _create_nav_btn(self, text, index):
        btn = QPushButton(text)
        btn.setObjectName("nav_btn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self._set_active_nav(index))
        self.sidebar_layout.addWidget(btn)
        return btn

    def _set_active_nav(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            if i == index:
                btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
            else:
                btn.setStyleSheet("")
        
    def refresh_metrics(self):
        self.status_bar.showMessage("Refreshing dashboard data...")
        db = SessionLocal()
        try:
            m = DashboardService.get_metrics(db)
            self.kpi_revenue.update_value(f"{m['daily_sales']:,.2f} DA")
            self.kpi_cash.update_value(f"{m['total_cash']:,.2f} DA")
            self.kpi_profit.update_value(f"{m['estimated_profit']:,.2f} DA")
            
            dates, values = DashboardService.get_sales_trend(db)
            self.sales_chart.plot(dates, values)
            self.status_bar.showMessage(f"Last sync: {QDateTime.currentDateTime().toString('hh:mm:ss')}", 5000)
        finally:
            db.close()

    def update_ui_text(self, lang):
        self.setWindowTitle(translator.translate('dashboard.title'))
        self.btn_dashboard.setText("🏠 " + translator.translate('dashboard.title'))
        self.btn_sales.setText("🛒 " + translator.translate('dashboard.sales'))
        self.btn_products.setText("📦 " + translator.translate('products.title'))
        self.btn_parcels.setText("🚚 " + translator.translate('parcels.title'))
        self.btn_finance.setText("💰 " + translator.translate('finance.title'))
        self.welcome_label.setText(translator.translate('dashboard.welcomeMessage', username=self.user.username))
        self.role_label.setText(translator.translate('dashboard.roleInfo', role=self.user.role))
        self.logout_btn.setText(translator.translate('dashboard.logoutButton'))
        self.setStyleSheet(get_main_style(lang == 'ar'))
        if lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
