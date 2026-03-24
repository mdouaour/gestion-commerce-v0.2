from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QMessageBox, QCompleter
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
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Top: Barcode and Search
        search_layout = QHBoxLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText(translator.translate('sales.barcode_label'))
        self.barcode_input.returnPressed.connect(self.handle_barcode)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(translator.translate('sales.product_search'))
        
        search_layout.addWidget(QLabel(translator.translate('sales.barcode_label') + ':'))
        search_layout.addWidget(self.barcode_input)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            translator.translate('sales.product_search'), 
            translator.translate('sales.quantity'), 
            translator.translate('sales.price'), 
            translator.translate('sales.total')
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        # Bottom: Total and Checkout
        bottom_layout = QHBoxLayout()
        self.total_label = QLabel(f"{translator.translate('sales.total')}: 0.00 DZD")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        
        self.checkout_btn = QPushButton(translator.translate('sales.checkout'))
        self.checkout_btn.setObjectName('primary')
        self.checkout_btn.clicked.connect(self.handle_checkout)
        
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.checkout_btn)
        self.layout.addLayout(bottom_layout)

    def handle_barcode(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
            
        db = SessionLocal()
        product = ProductService.get_product_by_sku(db, barcode)
        db.close()

        if product:
            self.add_to_cart(product)
            self.barcode_input.clear()
        else:
            QMessageBox.warning(self, "Error", translator.translate('errors.PRODUCT_NOT_FOUND'))

    def add_to_cart(self, product):
        # Check if already in cart
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
            
            self.table.setItem(i, 0, QTableWidgetItem(p.name))
            self.table.setItem(i, 1, QTableWidgetItem(str(q)))
            self.table.setItem(i, 2, QTableWidgetItem(f"{p.price:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{subtotal:.2f}"))
            
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
