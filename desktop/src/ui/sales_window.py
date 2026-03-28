from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QTabWidget, QMessageBox, QAbstractItemView, QSpinBox,
                             QDialog, QFormLayout, QDoubleSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from src.core.translator import translator
from src.services.sale_service import SaleService
from src.services.parcel_service import ParcelService
from src.models.database import SessionLocal

class ParcelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parcel Details")
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        self.shipping_input = QDoubleSpinBox()
        self.shipping_input.setRange(0, 10000)
        self.shipping_input.setValue(0)
        
        layout.addRow("Client Name:", self.name_input)
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("Address:", self.address_input)
        layout.addRow("Shipping Fee:", self.shipping_input)
        
        btns = QHBoxLayout()
        save = QPushButton("Create Parcel")
        save.setObjectName("primary")
        save.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

    def get_data(self):
        return {
            'client_name': self.name_input.text(),
            'client_phone': self.phone_input.text(),
            'client_address': self.address_input.text(),
            'shipping_fee': self.shipping_input.value()
        }

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
        self.table = QTableWidget(0, 5) # Added 1 column for Action
        self.table.setHorizontalHeaderLabels([
            translator.translate('products.name'), 
            translator.translate('sales.quantity'), 
            translator.translate('products.price'), 
            translator.translate('sales.total'),
            "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.itemChanged.connect(self.handle_item_changed)
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
        
        self.parcel_btn = QPushButton("🚚 " + translator.translate('parcels.title'))
        self.parcel_btn.setObjectName('secondary')
        self.parcel_btn.setMinimumHeight(70)
        self.parcel_btn.setMinimumWidth(200)
        self.parcel_btn.setStyleSheet("font-size: 18px;")
        self.parcel_btn.clicked.connect(self.handle_parcel_checkout)
        
        bottom_layout.addWidget(QLabel(f"{translator.translate('sales.total')}:"))
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.parcel_btn)
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

        # Optimization for Barcode Scanner: If exact SKU match, add immediately
        matched_product = next((p for p in self.all_products if p.sku == text), None)
        if matched_product:
            self.add_to_cart(matched_product, self.qty_input.value())
            self.search_input.clear()
            self.qty_input.setValue(1)
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
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.cart))
        total = 0
        for i, item in enumerate(self.cart):
            p = item['product']
            q = item['quantity']
            subtotal = p.price * q
            total += subtotal
            
            # Name (Read-only)
            name_item = QTableWidgetItem(p.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, name_item)
            
            # Qty (Editable)
            qty_item = QTableWidgetItem(str(q))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, qty_item)
            
            # Price (Read-only)
            price_item = QTableWidgetItem(f"{p.price:,.2f}")
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, price_item)
            
            # Total (Read-only)
            total_item = QTableWidgetItem(f"{subtotal:,.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, total_item)

            # Action (Remove Button)
            remove_btn = QPushButton("✕")
            remove_btn.setObjectName("danger")
            remove_btn.setFixedWidth(40)
            remove_btn.clicked.connect(lambda checked, row=i: self.remove_item(row))
            self.table.setCellWidget(i, 4, remove_btn)
            
        self.total_label.setText(f"{total:,.2f} DZD")
        self.table.blockSignals(False)

    def handle_item_changed(self, item):
        if item.column() == 1: # Quantity column
            row = item.row()
            try:
                new_qty = int(item.text())
                if new_qty <= 0:
                    self.remove_item(row)
                else:
                    self.cart[row]['quantity'] = new_qty
                    self.update_table()
            except ValueError:
                # Revert if invalid input
                self.update_table()

    def remove_item(self, row):
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.update_table()

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

    def handle_parcel_checkout(self):
        if not self.cart:
            QMessageBox.information(self, "Info", translator.translate('sales.empty_cart'))
            return
            
        dialog = ParcelDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['client_name'] or not data['client_phone']:
                QMessageBox.warning(self, "Error", "Client name and phone are required for parcels.")
                return

            items_data = []
            for item in self.cart:
                items_data.append({
                    'product_id': item['product'].id,
                    'quantity': item['quantity'],
                    'price_at_sale': item['product'].price
                })
                
            db = SessionLocal()
            parcel, error = ParcelService.create_parcel(
                db, 
                data['client_name'],
                data['client_phone'],
                data['client_address'],
                items_data,
                data['shipping_fee'],
                self.user.id
            )
            db.close()
            
            if parcel:
                QMessageBox.information(self, "Success", "Parcel created successfully!")
                self.cart = []
                self.update_table()
                self.sale_completed.emit()
                self.search_input.setFocus()
            else:
                QMessageBox.critical(self, "Error", f"Parcel Error: {error}")

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
