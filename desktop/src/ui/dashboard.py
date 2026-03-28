from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame, QComboBox, QScrollArea, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QEvent, QPropertyAnimation, QEasingCurve
from src.core.translator import translator
from src.core.theme import Theme
from src.ui.styles import get_main_style
from src.ui.sales_window import SalesTerminal
from src.ui.product_window import ProductManagement
from src.ui.parcel_window import ParcelManagement
from src.ui.finance_window import FinanceManagement
from src.ui.po_window import POManagement
from src.ui.components.kpi_card import KPICard
from src.ui.components.charts import SalesTrendChart

from src.services.dashboard_service import DashboardService
from src.models.database import SessionLocal

class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.sidebar_expanded = True
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
        self.sidebar.setFixedWidth(Theme.SIDEBAR_WIDTH)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 20)
        self.sidebar_layout.setSpacing(5)

        # Sidebar Header & Toggle
        sidebar_header = QHBoxLayout()
        self.sidebar_label = QLabel("G-POS")
        self.sidebar_label.setStyleSheet(f"color: white; font-weight: {Theme.FONT_WEIGHT_HEAVY}; font-size: 18px; padding-left: 5px;")
        
        self.btn_toggle = QPushButton("≡")
        self.btn_toggle.setObjectName("sidebar_toggle")
        self.btn_toggle.setFixedWidth(40)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        
        sidebar_header.addWidget(self.sidebar_label)
        sidebar_header.addStretch()
        sidebar_header.addWidget(self.btn_toggle)
        self.sidebar_layout.addLayout(sidebar_header)

        # Nav Buttons (using double spaces to facilitate easy icon splitting for collapse)
        self.btn_dashboard = self._create_nav_btn("🏠  " + translator.translate('dashboard.title'), 0)
        self.btn_sales = self._create_nav_btn("🛒  " + translator.translate('dashboard.sales'), 1)
        self.btn_products = self._create_nav_btn("📦  " + translator.translate('products.title'), 2)
        self.btn_parcels = self._create_nav_btn("🚚  " + translator.translate('parcels.title'), 3)
        self.btn_po = self._create_nav_btn("📝  Purchase Orders", 4)
        self.btn_finance = self._create_nav_btn("💰  " + translator.translate('finance.title'), 5)
        self.btn_admin = self._create_nav_btn("⚙️  System Admin", 6)

        self.nav_btns = [self.btn_dashboard, self.btn_sales, self.btn_products, self.btn_parcels, self.btn_po, self.btn_finance, self.btn_admin]
        
        # RBAC
        if self.user.role != 'admin':
            self.btn_po.hide()
            self.btn_finance.hide()
            self.btn_admin.hide()

        self.sidebar_layout.addStretch()
        
        # --- SIDEBAR FOOTER ---
        self.sidebar_divider = QFrame()
        self.sidebar_divider.setObjectName("divider")
        self.sidebar_layout.addWidget(self.sidebar_divider)

        # Language Switcher
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['fr', 'ar', 'en'])
        self.lang_combo.setCurrentText(translator.current_lang)
        self.lang_combo.currentTextChanged.connect(translator.set_language)
        self.sidebar_layout.addWidget(self.lang_combo)

        # Logout
        self.logout_btn = QPushButton("🚪  " + translator.translate('dashboard.logoutButton'))
        self.logout_btn.setObjectName('danger')
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        self.sidebar_layout.addWidget(self.logout_btn)

        self.main_layout.addWidget(self.sidebar)

        # --- MAIN CONTENT ---
        self.content_stack = QStackedWidget()
        
        # PAGE 0: DASHBOARD OVERVIEW (With Scroll Area)
        self.overview_scroll = QScrollArea()
        self.overview_scroll.setWidgetResizable(True)
        self.overview_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.overview_scroll.setStyleSheet(f"background-color: {Theme.BACKGROUND};")

        self.overview_page = QWidget()
        self.overview_page.setStyleSheet(f"background-color: {Theme.BACKGROUND};")
        self.overview_layout = QVBoxLayout(self.overview_page)
        self.overview_layout.setContentsMargins(Theme.MARGIN_PAGE, Theme.MARGIN_PAGE, Theme.MARGIN_PAGE, Theme.MARGIN_PAGE)
        self.overview_layout.setSpacing(25)
        
        # Header Section
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

        # KPI Section (Refactored Container)
        self.kpi_container = QFrame()
        self.kpi_container.setObjectName("kpi_container")
        self.kpi_container.setStyleSheet(f"""
            QFrame#kpi_container {{
                background-color: {Theme.LIGHT_GRAY};
                border-radius: {Theme.RADIUS_CARD}px;
                border: 1px solid {Theme.BORDER};
            }}
        """)
        
        kpi_layout = QHBoxLayout(self.kpi_container)
        kpi_layout.setContentsMargins(20, 20, 20, 20)
        kpi_layout.setSpacing(15)
        kpi_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.kpi_revenue = KPICard("REVENUE TODAY", "0.00", Theme.SUCCESS, "+0% vs yesterday")
        self.kpi_cash = KPICard("CASH IN HAND", "0.00", Theme.PRIMARY)
        self.kpi_profit = KPICard("EST. PROFIT (MTD)", "0.00", "#8e44ad", "+0% vs last month")
        self.kpi_low_stock = KPICard("LOW STOCK", "0", Theme.DANGER)
        
        kpi_layout.addWidget(self.kpi_revenue)
        kpi_layout.addWidget(self.kpi_cash)
        kpi_layout.addWidget(self.kpi_profit)
        kpi_layout.addWidget(self.kpi_low_stock)
        self.overview_layout.addWidget(self.kpi_container)

        # Charts Section
        self.sales_chart = SalesTrendChart()
        self.overview_layout.addWidget(self.sales_chart)
        self.overview_layout.addStretch()

        self.overview_scroll.setWidget(self.overview_page)
        self.content_stack.addWidget(self.overview_scroll)
        
        # Add Other Pages
        self.content_stack.addWidget(SalesTerminal(self.user))
        self.content_stack.addWidget(ProductManagement(self.user))
        self.content_stack.addWidget(ParcelManagement(self.user))
        self.content_stack.addWidget(POManagement(self.user))
        self.content_stack.addWidget(FinanceManagement(self.user))
        
        self.main_layout.addWidget(self.content_stack)

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

    def toggle_sidebar(self):
        """Animates the sidebar between collapsed and expanded states."""
        start_width = self.sidebar.width()
        end_width = 70 if self.sidebar_expanded else Theme.SIDEBAR_WIDTH
        
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        # Ensure maximum width also follows the animation
        self.sidebar.setMaximumWidth(end_width)
        self.animation.start()
        
        self.sidebar_expanded = not self.sidebar_expanded
        self.sidebar_label.setVisible(self.sidebar_expanded)
        
        # When collapsed, show only icons. When expanded, show icons + text.
        for btn in self.nav_btns:
            if not self.sidebar_expanded:
                btn.setText(btn.text().split('  ')[0])
            else:
                # Re-trigger update_ui_text to restore full labels
                self.update_ui_text(translator.current_lang)

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
            is_active = (i == index)
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
    def refresh_metrics(self):
        self.status_bar.showMessage("Refreshing dashboard data...")
        db = SessionLocal()
        try:
            m = DashboardService.get_metrics(db)
            self.kpi_revenue.update_value(f"{m['daily_sales']:,.2f} DA", m.get('revenue_trend', "+0%"))
            self.kpi_cash.update_value(f"{m['total_cash']:,.2f} DA")
            self.kpi_profit.update_value(f"{m['estimated_profit']:,.2f} DA", m.get('profit_trend', "+0%"))
            self.kpi_low_stock.update_value(str(m.get('low_stock_count', 0)))
            
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
        self.btn_po.setText("📝 Purchase Orders")
        self.btn_finance.setText("💰 " + translator.translate('finance.title'))
        self.welcome_label.setText(translator.translate('dashboard.welcomeMessage', username=self.user.username))
        self.role_label.setText(translator.translate('dashboard.roleInfo', role=self.user.role))
        self.logout_btn.setText(translator.translate('dashboard.logoutButton'))
        self.setStyleSheet(get_main_style(lang == 'ar'))
        if lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
