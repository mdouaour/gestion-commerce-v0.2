from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QTableView, QHeaderView, QMessageBox, QDialog, 
                             QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from src.core.translator import translator
from src.services.purchase_order_service import POService
from src.services.product_service import ProductService
from src.models.database import SessionLocal
from src.models.purchase_order import POStatus

class PODialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Purchase Order")
        self.setMinimumWidth(600)
        self.items = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.supplier_input = QLineEdit()
        form.addRow("Supplier Name:", self.supplier_input)
        layout.addLayout(form)
        
        # Product Selection
        prod_layout = QHBoxLayout()
        self.prod_combo = QComboBox()
        db = SessionLocal()
        products = ProductService.get_all_products(db)
        for p in products:
            self.prod_combo.addItem(f"{p.name} ({p.sku})", p)
        db.close()
        
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 10000)
        self.buy_price = QDoubleSpinBox()
        self.buy_price.setRange(0, 1000000)
        self.sell_price = QDoubleSpinBox()
        self.sell_price.setRange(0, 1000000)
        
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)
        
        prod_layout.addWidget(QLabel("Product:"))
        prod_layout.addWidget(self.prod_combo, 2)
        prod_layout.addWidget(QLabel("Qty:"))
        prod_layout.addWidget(self.qty_input)
        prod_layout.addWidget(QLabel("Buy Price:"))
        prod_layout.addWidget(self.buy_price)
        prod_layout.addWidget(QLabel("Sell Price:"))
        prod_layout.addWidget(self.sell_price)
        prod_layout.addWidget(add_btn)
        layout.addLayout(prod_layout)
        
        # Items Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Product", "Qty", "Buy Price", "Sell Price", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        btns = QHBoxLayout()
        save = QPushButton("Save PO")
        save.setObjectName("primary")
        save.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def add_item(self):
        product = self.prod_combo.currentData()
        qty = self.qty_input.value()
        buy = self.buy_price.value()
        sell = self.sell_price.value()
        
        self.items.append({
            'product_id': product.id,
            'name': product.name,
            'quantity': qty,
            'purchase_price': buy,
            'selling_price': sell
        })
        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.items))
        for i, item in enumerate(self.items):
            self.table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(i, 2, QTableWidgetItem(f"{item['purchase_price']:,.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{item['selling_price']:,.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{item['quantity'] * item['purchase_price']:,.2f}"))

    def get_data(self):
        return self.supplier_input.text(), self.items

class POManagement(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
        self.load_pos()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("Purchase Orders")
        title.setObjectName("header")
        header.addWidget(title)
        
        add_btn = QPushButton("+ New PO")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.open_add_dialog)
        header.addStretch()
        header.addWidget(add_btn)
        self.layout.addLayout(header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Supplier", "Status", "Total Amount", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

    def load_pos(self):
        db = SessionLocal()
        pos = POService.get_all_pos(db)
        self.table.setRowCount(len(pos))
        for i, po in enumerate(pos):
            self.table.setItem(i, 0, QTableWidgetItem(str(po.id)))
            self.table.setItem(i, 1, QTableWidgetItem(po.supplier_name))
            self.table.setItem(i, 2, QTableWidgetItem(po.status.upper()))
            self.table.setItem(i, 3, QTableWidgetItem(f"{po.total_amount:,.2f} DA"))
            
            # Actions Cell
            actions = QWidget()
            act_layout = QHBoxLayout(actions)
            act_layout.setContentsMargins(2, 2, 2, 2)
            
            if po.status == POStatus.DRAFT:
                recv_btn = QPushButton("Receive")
                recv_btn.clicked.connect(lambda checked, p_id=po.id: self.receive_po(p_id))
                act_layout.addWidget(recv_btn)
            elif po.status == POStatus.DELIVERED:
                pay_btn = QPushButton("Mark Paid")
                pay_btn.clicked.connect(lambda checked, p_id=po.id: self.pay_po(p_id))
                act_layout.addWidget(pay_btn)
            
            self.table.setCellWidget(i, 4, actions)
        db.close()

    def open_add_dialog(self):
        dialog = PODialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            supplier, items = dialog.get_data()
            if not items: return
            db = SessionLocal()
            POService.create_po(db, supplier, items, self.user.id)
            db.close()
            self.load_pos()

    def receive_po(self, po_id):
        confirm = QMessageBox.question(self, "Confirm Receipt", "This will increase stock levels. Continue?")
        if confirm == QMessageBox.StandardButton.Yes:
            db = SessionLocal()
            success, error = POService.receive_po(db, po_id, self.user.id)
            db.close()
            if success:
                self.load_pos()
            else:
                QMessageBox.critical(self, "Error", error)

    def pay_po(self, po_id):
        db = SessionLocal()
        POService.pay_po(db, po_id, self.user.id)
        db.close()
        self.load_pos()
