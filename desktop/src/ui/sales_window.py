from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QTabWidget, QMessageBox, QCompleter, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.translator import translator
from src.services.sale_service import SaleService
from src.services.product_service import ProductService
from src.models.database import SessionLocal

class SaleTab(QWidget):
    sale_completed = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = [] # List of {'product': obj, 'quantity': int}
        self.all_products = [] # Cached for search
        self.init_ui()
        self.load_products()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Top: Search and Info
        search_layout = QHBoxLayout()
        
        # IMPROVED SEARCH UX
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Product (Name or SKU)... [Ctrl+F]")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("font-size: 16px; padding: 5px;")
        self.search_input.textChanged.connect(self.handle_search)
        
        # Keyboard Navigation for search results
        self.search_results = QTableWidget(0, 3)
        self.search_results.setHorizontalHeaderLabels(["Name", "SKU", "Price"])
        self.search_results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.search_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # READ ONLY
        self.search_results.setMinimumHeight(150)
        self.search_results.hide() # Hidden until typing
        self.search_results.itemDoubleClicked.connect(self.select_search_result)
        
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)
        self.layout.addWidget(self.search_results)

        # Cart Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            translator.translate('sales.product_search'), 
            translator.translate('sales.quantity'), 
            translator.translate('sales.price'), 
            translator.translate('sales.total')
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # CRITICAL: DATA INTEGRITY - NO MANUAL EDITS
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("font-size: 14px;")
        
        self.layout.addWidget(self.table)

        # Bottom: Total and Checkout
        bottom_layout = QHBoxLayout()
        self.total_label = QLabel(f"{translator.translate('sales.total')}: 0.00 DZD")
        self.total_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.checkout_btn = QPushButton(translator.translate('sales.checkout') + " [F5]")
        self.checkout_btn.setObjectName('primary')
        self.checkout_btn.setMinimumHeight(60)
        self.checkout_btn.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px 40px;")
        self.checkout_btn.clicked.connect(self.handle_checkout)
        
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.checkout_btn)
        self.layout.addLayout(bottom_layout)

    def load_products(self):
        db = SessionLocal()
        try:
            from src.models.product import Product
            self.all_products = db.query(Product).all()
        finally:
            db.close()

    def handle_search(self, text):
        if not text:
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
                name_item.setData(Qt.ItemDataRole.UserRole, p) # Store product object
                self.search_results.setItem(i, 0, name_item)
                self.search_results.setItem(i, 1, QTableWidgetItem(p.sku))
                self.search_results.setItem(i, 2, QTableWidgetItem(f"{p.price:.2f}"))
            self.search_results.show()
        else:
            self.search_results.hide()

    def select_search_result(self, item):
        row = item.row()
        product = self.search_results.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.add_to_cart(product)
        self.search_input.clear()
        self.search_results.hide()

    def keyPressEvent(self, event):
        # Keyboard Navigation for Search Results
        if self.search_results.isVisible():
            if event.key() == Qt.Key.Key_Down:
                self.search_results.setFocus()
                self.search_results.selectRow(0)
            elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                if self.search_results.currentRow() >= 0:
                    self.select_search_result(self.search_results.item(self.search_results.currentRow(), 0))
                return
        super().keyPressEvent(event)

    def add_to_cart(self, product):
        for item in self.cart:
            if item['product'].id == product.id:
                item['quantity'] += 1
                self.update_table()
                return
        
        self.cart.append({'product': product, 'quantity': 1})
        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.cart))
        total = 0
        for i, item in enumerate(self.cart):
            p = item['product']
            q = item['quantity']
            subtotal = p.price * q
            total += subtotal
            
            # Use QTableWidgetItem properly
            name_item = QTableWidgetItem(p.name)
            qty_item = QTableWidgetItem(str(q))
            price_item = QTableWidgetItem(f"{p.price:.2f}")
            total_item = QTableWidgetItem(f"{subtotal:.2f}")
            
            # Center text for quantity
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, qty_item)
            self.table.setItem(i, 2, price_item)
            self.table.setItem(i, 3, total_item)
            
        self.total_label.setText(f"{translator.translate('sales.total')}: {total:.2f} DZD")

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
