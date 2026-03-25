from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QTabWidget, QMessageBox, QAbstractItemView, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from src.core.translator import translator
from src.services.sale_service import SaleService
from src.models.database import SessionLocal

class SaleTab(QWidget):
    sale_completed = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = [] # List of {'product': obj, 'quantity': int}
        self.all_products = [] # Cached for search
        self.init_ui()
        self.setup_shortcuts()
        self.load_products()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        # --- TOP SECTION: SEARCH & QUICK ACTION ---
        top_bar = QHBoxLayout()
        
        # Search Box with Icon placeholder logic
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 " + translator.translate('sales.product_search') + " [Ctrl+F]")
        self.search_input.setMinimumHeight(50)
        self.search_input.setStyleSheet("font-size: 18px; font-weight: 500;")
        self.search_input.textChanged.connect(self.handle_search)
        
        # Quantity Spinbox for quick adding
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 999)
        self.qty_input.setValue(1)
        self.qty_input.setMinimumHeight(50)
        self.qty_input.setMinimumWidth(80)
        self.qty_input.setStyleSheet("font-size: 18px;")
        
        top_bar.addWidget(self.search_input, 4)
        top_bar.addWidget(QLabel("Qty:"), 0)
        top_bar.addWidget(self.qty_input, 1)
        self.layout.addLayout(top_bar)

        # SEARCH RESULTS (Drop-down style table)
        self.search_results = QTableWidget(0, 3)
        self.search_results.setHorizontalHeaderLabels(["Name", "SKU", "Price"])
        self.search_results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search_results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.search_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.search_results.setMinimumHeight(200)
        self.search_results.setMaximumHeight(300)
        self.search_results.hide()
        self.search_results.itemDoubleClicked.connect(self.select_search_result)
        self.layout.addWidget(self.search_results)

        # --- MIDDLE SECTION: CART ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            translator.translate('products.name'), 
            translator.translate('sales.quantity'), 
            translator.translate('products.price'), 
            translator.translate('sales.total')
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("font-size: 15px;")
        self.layout.addWidget(self.table)

        # --- BOTTOM SECTION: TOTAL & CHECKOUT ---
        bottom_layout = QHBoxLayout()
        
        self.total_label = QLabel(f"0.00 DZD")
        self.total_label.setObjectName("header")
        self.total_label.setStyleSheet("font-size: 32px; color: #27ae60;")
        
        self.checkout_btn = QPushButton(translator.translate('sales.checkout') + " [F5]")
        self.checkout_btn.setObjectName('primary')
        self.checkout_btn.setMinimumHeight(70)
        self.checkout_btn.setMinimumWidth(250)
        self.checkout_btn.setStyleSheet("font-size: 20px;")
        self.checkout_btn.clicked.connect(self.handle_checkout)
        
        bottom_layout.addWidget(QLabel(f"{translator.translate('sales.total')}:"))
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.checkout_btn)
        self.layout.addLayout(bottom_layout)

    def setup_shortcuts(self):
        # Ctrl+F to focus search
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(self.search_input.setFocus)
        
        # F5 to Checkout
        self.shortcut_checkout = QShortcut(QKeySequence("F5"), self)
        self.shortcut_checkout.activated.connect(self.handle_checkout)

    def load_products(self):
        db = SessionLocal()
        try:
            from src.models.product import Product
            self.all_products = db.query(Product).all()
        finally:
            db.close()

    def handle_search(self, text):
        if not text or len(text) < 1:
            self.search_results.hide()
            return
            
        results = []
        for p in self.all_products:
            if text.lower() in p.name.lower() or text.lower() in p.sku.lower():
                results.append(p)
        
        if results:
            self.search_results.setRowCount(len(results))
            for i, p in enumerate(results):
                name_item = QTableWidgetItem(p.name)
                name_item.setData(Qt.ItemDataRole.UserRole, p)
                self.search_results.setItem(i, 0, name_item)
                self.search_results.setItem(i, 1, QTableWidgetItem(p.sku))
                self.search_results.setItem(i, 2, QTableWidgetItem(f"{p.price:,.2f}"))
            self.search_results.show()
            self.search_results.selectRow(0)
        else:
            self.search_results.hide()

    def select_search_result(self, item=None):
        if not self.search_results.isVisible(): return
        
        row = self.search_results.currentRow()
        if row < 0: return
        
        product = self.search_results.item(row, 0).data(Qt.ItemDataRole.UserRole)
        qty = self.qty_input.value()
        
        self.add_to_cart(product, qty)
        self.search_input.clear()
        self.qty_input.setValue(1)
        self.search_results.hide()
        self.search_input.setFocus()

    def keyPressEvent(self, event):
        if self.search_input.hasFocus():
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.select_search_result()
                return
            elif event.key() == Qt.Key.Key_Down:
                self.search_results.setFocus()
                return

        if self.search_results.hasFocus():
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.select_search_result()
                return
            elif event.key() == Qt.Key.Key_Up and self.search_results.currentRow() == 0:
                self.search_input.setFocus()
                return

        super().keyPressEvent(event)

    def add_to_cart(self, product, quantity):
        for item in self.cart:
            if item['product'].id == product.id:
                item['quantity'] += quantity
                self.update_table()
                return
        
        self.cart.append({'product': product, 'quantity': quantity})
        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.cart))
        total = 0
        for i, item in enumerate(self.cart):
            p = item['product']
            q = item['quantity']
            subtotal = p.price * q
            total += subtotal
            
            self.table.setItem(i, 0, QTableWidgetItem(p.name))
            
            qty_item = QTableWidgetItem(str(q))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, qty_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(f"{p.price:,.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{subtotal:,.2f}"))
            
        self.total_label.setText(f"{total:,.2f} DZD")

    def handle_checkout(self):
        if not self.cart:
            QMessageBox.information(self, "Info", translator.translate('sales.empty_cart'))
            return
            
        items_data = []
        for item in self.cart:
            items_data.append({
                'product_id': item['product'].id,
                'quantity': item['quantity'],
                'price_at_sale': item['product'].price,
                'version': item['product'].version
            })
            
        db = SessionLocal()
        sale, error = SaleService.create_sale(db, self.user.id, items_data)
        db.close()
        
        if sale:
            QMessageBox.information(self, "Success", translator.translate('sales.success_msg'))
            self.cart = []
            self.update_table()
            self.sale_completed.emit()
            self.search_input.setFocus()
        else:
            QMessageBox.critical(self, "Error", translator.translate(f'errors.{error}'))

class SalesTerminal(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        self.add_tab_btn = QPushButton(translator.translate('sales.new_sale'))
        self.add_tab_btn.clicked.connect(self.add_new_sale_tab)
        
        self.layout.addWidget(self.add_tab_btn)
        self.layout.addWidget(self.tabs)
        
        self.add_new_sale_tab()

    def add_new_sale_tab(self):
        tab_id = self.tabs.count() + 1
        new_tab = SaleTab(self.user)
        self.tabs.addTab(new_tab, translator.translate('sales.tab_name', id=tab_id))
        self.tabs.setCurrentWidget(new_tab)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
