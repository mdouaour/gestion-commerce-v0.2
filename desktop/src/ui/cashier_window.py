from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QAbstractItemView, QSpinBox, QDialog, QFormLayout, 
                             QDoubleSpinBox, QFrame, QSplitter, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence, QFont
from src.core.translator import translator
from src.core.theme import Theme
from src.services.sale_service import SaleService
from src.services.parcel_service import ParcelService
from src.services.auth_service import AuthService
from src.models.database import SessionLocal
from src.models.user import UserRole
from src.models.sale_parcel import ParcelStatus, SaleStatus
from src.ui.styles import get_main_style

class AdminAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Authorization")
        self.setFixedSize(350, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.msg = QLabel("Admin authorization required for this action.")
        self.msg.setWordWrap(True)
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg)

        form = QFormLayout()
        self.admin_username = QLineEdit()
        self.admin_password = QLineEdit()
        self.admin_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        form.addRow("Admin User:", self.admin_username)
        form.addRow("Password:", self.admin_password)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.auth_btn = QPushButton("Authorize")
        self.auth_btn.setObjectName("primary")
        self.auth_btn.clicked.connect(self.handle_auth)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(self.auth_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)
        
        self.admin_user = None

    def handle_auth(self):
        username = self.admin_username.text()
        password = self.admin_password.text()
        
        db = SessionLocal()
        user, error = AuthService.authenticate_user(db, username, password)
        db.close()
        
        if user and user.role == UserRole.ADMIN:
            self.admin_user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Failed", "Invalid admin credentials.")

class ParcelMiniPanel(QFrame):
    status_updated = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setObjectName("mini_panel")
        self.setStyleSheet(f"QFrame#mini_panel {{ background-color: #f8f9fa; border-left: 2px solid {Theme.BORDER}; }}")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("PARCEL MANAGEMENT")
        title.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 16px;")
        layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Parcel (ID/Name/Phone)...")
        self.search_input.textChanged.connect(self.handle_search)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Client", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.show_parcel_actions)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self, query=None):
        db = SessionLocal()
        if query:
            parcels = ParcelService.search_parcels(db, query)
        else:
            parcels = ParcelService.get_all_parcels(db)
        db.close()

        self.table.setRowCount(len(parcels))
        for i, p in enumerate(parcels):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(p.client_name))
            status_item = QTableWidgetItem(p.status.upper())
            # Color coding for status
            if p.status == ParcelStatus.DELIVERED: status_item.setForeground(Qt.GlobalColor.green)
            elif p.status == ParcelStatus.RETURNED: status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(i, 2, status_item)
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, p.id)

    def handle_search(self, text):
        self.load_data(text if len(text) >= 2 else None)

    def show_parcel_actions(self):
        row = self.table.currentRow()
        if row < 0: return
        parcel_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Simple action dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Parcel #{parcel_id} Actions")
        vbox = QVBoxLayout(dialog)
        
        vbox.addWidget(QLabel(f"Update status for Parcel #{parcel_id}:"))
        
        status_combo = QComboBox()
        status_options = [s for s in ParcelStatus]
        status_combo.addItems([s.value.upper() for s in status_options])
        vbox.addWidget(status_combo)
        
        btn_update = QPushButton("Update Status")
        btn_update.setObjectName("primary")
        btn_update.clicked.connect(lambda: self.perform_update(parcel_id, status_combo.currentText().lower(), dialog))
        vbox.addWidget(btn_update)
        
        btn_validate = QPushButton("Validate Parcel")
        btn_validate.setObjectName("secondary")
        btn_validate.clicked.connect(lambda: self.perform_validation(parcel_id, dialog))
        vbox.addWidget(btn_validate)
        
        dialog.exec()

    def perform_update(self, parcel_id, status, dialog):
        db = SessionLocal()
        ParcelService.update_parcel_status(db, parcel_id, status, self.user.id)
        db.close()
        dialog.accept()
        self.load_data()
        self.status_updated.emit()

    def perform_validation(self, parcel_id, dialog):
        db = SessionLocal()
        ParcelService.validate_parcel(db, parcel_id, self.user.id)
        db.close()
        dialog.accept()
        self.load_data()
        self.status_updated.emit()

class CashierWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = []
        self.all_products = []
        self.init_ui()
        self.setup_shortcuts()
        self.load_products()
        
    def init_ui(self):
        self.setWindowTitle("G-POS Cashier Terminal")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(get_main_style(translator.current_lang == 'ar'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # --- HEADER ---
        header = QHBoxLayout()
        title = QLabel("CASHIER TERMINAL")
        title.setObjectName("header")
        header.addWidget(title)
        
        user_info = QLabel(f"User: {self.user.username} | Role: {self.user.role.upper()}")
        user_info.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        header.addStretch()
        header.addWidget(user_info)
        
        self.logout_btn = QPushButton("Logout [Esc]")
        self.logout_btn.setObjectName("danger")
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        header.addWidget(self.logout_btn)
        self.main_layout.addLayout(header)

        # --- SPLITTER FOR MAIN CONTENT & PARCEL PANEL ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANEL: SALE AREA
        self.sale_container = QWidget()
        sale_layout = QHBoxLayout(self.sale_container)
        
        # 1. Left Sub-Panel: Product Search
        search_panel = QVBoxLayout()
        search_panel.setContentsMargins(0, 0, 10, 0)
        
        search_label = QLabel("PRODUCT SEARCH")
        search_label.setStyleSheet("font-weight: bold; color: #34495e;")
        search_panel.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Scan barcode or type name...")
        self.search_input.setMinimumHeight(60)
        self.search_input.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        self.search_input.textChanged.connect(self.handle_search)
        search_panel.addWidget(self.search_input)

        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 999)
        self.qty_input.setValue(1)
        self.qty_input.setMinimumHeight(50)
        self.qty_input.setStyleSheet("font-size: 18px;")
        qty_box = QHBoxLayout()
        qty_box.addWidget(QLabel("Default Qty:"))
        qty_box.addWidget(self.qty_input)
        search_panel.addLayout(qty_box)

        self.search_results = QTableWidget(0, 3)
        self.search_results.setHorizontalHeaderLabels(["Name", "SKU", "Price"])
        self.search_results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search_results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.search_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.search_results.itemDoubleClicked.connect(self.select_search_result)
        search_panel.addWidget(self.search_results)
        
        sale_layout.addLayout(search_panel, 2)

        # 2. Right Sub-Panel: Cart
        cart_panel = QVBoxLayout()
        cart_panel.setContentsMargins(10, 0, 0, 0)
        
        cart_label = QLabel("SHOPPING CART")
        cart_label.setStyleSheet("font-weight: bold; color: #34495e;")
        cart_panel.addWidget(cart_label)

        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Total", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.cart_table.setColumnWidth(4, 50)
        self.cart_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.cart_table.itemChanged.connect(self.handle_cart_edit)
        cart_panel.addWidget(self.cart_table)

        # Total Section
        self.total_label = QLabel("0.00 DZD")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.total_label.setStyleSheet("font-size: 48px; font-weight: 800; color: #2ecc71; background: #ecf0f1; padding: 20px; border-radius: 10px;")
        cart_panel.addWidget(self.total_label)

        # Main Actions
        actions_box = QHBoxLayout()
        
        self.pay_btn = QPushButton("PAY [F5]")
        self.pay_btn.setObjectName("primary")
        self.pay_btn.setMinimumHeight(80)
        self.pay_btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.pay_btn.clicked.connect(self.handle_checkout)
        
        self.parcel_checkout_btn = QPushButton("PARCEL [F6]")
        self.parcel_checkout_btn.setObjectName("secondary")
        self.parcel_checkout_btn.setMinimumHeight(80)
        self.parcel_checkout_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.parcel_checkout_btn.clicked.connect(self.handle_parcel_checkout)

        self.refund_btn = QPushButton("REFUND [F8]")
        self.refund_btn.setObjectName("danger")
        self.refund_btn.setMinimumHeight(80)
        self.refund_btn.clicked.connect(self.handle_refund)
        
        actions_box.addWidget(self.refund_btn, 1)
        actions_box.addWidget(self.parcel_checkout_btn, 1)
        actions_box.addWidget(self.pay_btn, 2)
        cart_panel.addLayout(actions_box)

        sale_layout.addLayout(cart_panel, 3)
        
        self.splitter.addWidget(self.sale_container)
        
        # PARCEL MINI PANEL
        self.parcel_panel = ParcelMiniPanel(self.user)
        self.splitter.addWidget(self.parcel_panel)
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)
        
        self.main_layout.addWidget(self.splitter)

        # Status Bar
        self.status_bar = QFrame()
        self.status_bar.setFrameShape(QFrame.Shape.HLine)
        self.main_layout.addWidget(self.status_bar)
        self.status_msg = QLabel("Ready")
        self.main_layout.addWidget(self.status_msg)

        self.search_input.setFocus()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, self.search_input.setFocus)
        QShortcut(QKeySequence("F5"), self, self.handle_checkout)
        QShortcut(QKeySequence("F6"), self, self.handle_parcel_checkout)
        QShortcut(QKeySequence("F8"), self, self.handle_refund)
        QShortcut(QKeySequence("Esc"), self, self.handle_esc)

    def load_products(self):
        db = SessionLocal()
        from src.models.product import Product
        self.all_products = db.query(Product).all()
        db.close()

    def handle_search(self, text):
        if not text:
            self.search_results.hide()
            return

        # Scanner check: exact SKU match
        matched = next((p for p in self.all_products if p.sku == text), None)
        if matched:
            self.add_to_cart(matched, self.qty_input.value())
            self.search_input.clear()
            return

        results = [p for p in self.all_products if text.lower() in p.name.lower() or text.lower() in p.sku.lower()]
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

    def select_search_result(self):
        row = self.search_results.currentRow()
        if row >= 0:
            product = self.search_results.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.add_to_cart(product, self.qty_input.value())
            self.search_input.clear()
            self.search_results.hide()
            self.search_input.setFocus()

    def add_to_cart(self, product, qty):
        # Check stock before adding
        if product.stock_quantity < qty:
             QMessageBox.warning(self, "Stock Warning", f"Not enough stock for {product.name} (Available: {product.stock_quantity})")
             # We allow adding but checkout will fail anyway in service if strictly enforced.
             # Better to prevent here too.
        
        for item in self.cart:
            if item['product'].id == product.id:
                item['quantity'] += qty
                self.update_cart_display()
                return
        
        self.cart.append({'product': product, 'quantity': qty})
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.blockSignals(True)
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        for i, item in enumerate(self.cart):
            p = item['product']
            q = item['quantity']
            subtotal = p.price * q
            total += subtotal
            
            self.cart_table.setItem(i, 0, QTableWidgetItem(p.name))
            self.cart_table.item(i, 0).setFlags(self.cart_table.item(i, 0).flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.cart_table.setItem(i, 1, QTableWidgetItem(str(q)))
            
            self.cart_table.setItem(i, 2, QTableWidgetItem(f"{p.price:,.2f}"))
            self.cart_table.item(i, 2).setFlags(self.cart_table.item(i, 2).flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.cart_table.setItem(i, 3, QTableWidgetItem(f"{subtotal:,.2f}"))
            self.cart_table.item(i, 3).setFlags(self.cart_table.item(i, 3).flags() & ~Qt.ItemFlag.ItemIsEditable)

            remove_btn = QPushButton("✕")
            remove_btn.setObjectName("danger")
            remove_btn.clicked.connect(lambda checked, row=i: self.remove_cart_item(row))
            self.cart_table.setCellWidget(i, 4, remove_btn)
            
        self.total_label.setText(f"{total:,.2f} DZD")
        self.cart_table.blockSignals(False)

    def handle_cart_edit(self, item):
        if item.column() == 1:
            row = item.row()
            try:
                new_qty = int(item.text())
                if new_qty <= 0:
                    self.remove_cart_item(row)
                else:
                    self.cart[row]['quantity'] = new_qty
                    self.update_cart_display()
            except ValueError:
                self.update_cart_display()

    def remove_cart_item(self, row):
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.update_cart_display()

    def handle_checkout(self):
        if not self.cart: return
        
        items_data = [{'product_id': i['product'].id, 'quantity': i['quantity'], 
                      'price_at_sale': i['product'].price, 'version': i['product'].version} 
                     for i in self.cart]
        
        db = SessionLocal()
        sale, error = SaleService.create_sale(db, self.user.id, items_data)
        db.close()
        
        if sale:
            self.status_msg.setText(f"Last Sale: #{sale.id} | Total: {sale.total_amount:,.2f} DZD")
            self.cart = []
            self.update_cart_display()
            self.load_products() # Refresh stock
            self.search_input.setFocus()
        else:
            QMessageBox.critical(self, "Checkout Error", f"Error: {error}")

    def handle_parcel_checkout(self):
        if not self.cart: return
        from src.ui.sales_window import ParcelDialog
        dialog = ParcelDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            items_data = [{'product_id': i['product'].id, 'quantity': i['quantity'], 'price_at_sale': i['product'].price} for i in self.cart]
            db = SessionLocal()
            parcel, error = ParcelService.create_parcel(db, data['client_name'], data['client_phone'], data['client_address'], items_data, data['shipping_fee'], self.user.id)
            db.close()
            if parcel:
                QMessageBox.information(self, "Success", f"Parcel #{parcel.id} created!")
                self.cart = []
                self.update_cart_display()
                self.parcel_panel.load_data()
            else:
                QMessageBox.critical(self, "Error", f"Error: {error}")

    def handle_refund(self):
        # 1. Ask for Sale ID
        from PyQt6.QtWidgets import QInputDialog
        sale_id, ok = QInputDialog.getInt(self, "Refund", "Enter Sale ID to refund:")
        if not ok: return
        
        # 2. Require Admin Auth
        auth = AdminAuthDialog(self)
        if auth.exec() == QDialog.DialogCode.Accepted:
            admin_user = auth.admin_user
            db = SessionLocal()
            success, error = SaleService.refund_sale(db, sale_id, admin_user.id, self.user.id)
            db.close()
            if success:
                QMessageBox.information(self, "Success", f"Sale #{sale_id} has been refunded.")
                self.load_products() # Refresh stock
            else:
                QMessageBox.critical(self, "Error", f"Refund failed: {error}")

    def handle_esc(self):
        if self.search_results.isVisible():
            self.search_results.hide()
            self.search_input.clear()
        elif self.cart:
            if QMessageBox.question(self, "Clear Cart", "Are you sure you want to clear the cart?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.cart = []
                self.update_cart_display()
        else:
            self.logout_requested.emit()

    def keyPressEvent(self, event):
        if self.search_input.hasFocus():
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.select_search_result()
                return
            elif event.key() == Qt.Key.Key_Down:
                self.search_results.setFocus()
                return
        super().keyPressEvent(event)
