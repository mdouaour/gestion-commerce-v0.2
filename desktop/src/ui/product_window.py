from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox
from PyQt6.QtCore import Qt
from src.core.translator import translator
from src.services.product_service import ProductService
from src.models.database import SessionLocal
from src.models.product import Category

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(translator.translate('products.add_new'))
        self.setFixedWidth(400)
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.sku_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(1000000)
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(10000)
        
        self.cat_combo = QComboBox()
        db = SessionLocal()
        categories = db.query(Category).all()
        for cat in categories:
            self.cat_combo.addItem(cat.name, cat.id)
        db.close()

        layout.addRow(translator.translate('products.name') + ':', self.name_input)
        layout.addRow(translator.translate('products.sku') + ':', self.sku_input)
        layout.addRow(translator.translate('products.price') + ':', self.price_input)
        layout.addRow(translator.translate('products.stock') + ':', self.stock_input)
        layout.addRow(translator.translate('products.category') + ':', self.cat_combo)

        btns = QHBoxLayout()
        self.save_btn = QPushButton(translator.translate('products.save'))
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton(translator.translate('products.cancel'))
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        layout.addRow(btns)

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'sku': self.sku_input.text(),
            'price': self.price_input.value(),
            'stock': self.stock_input.value(),
            'category_id': self.cat_combo.currentData()
        }

class ProductManagement(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel(translator.translate('products.title'))
        self.title_label.setObjectName('header')
        self.add_btn = QPushButton(translator.translate('products.add_new'))
        self.add_btn.setObjectName('primary')
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        self.layout.addLayout(header_layout)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(translator.translate('sales.product_search'))
        self.search_input.textChanged.connect(self.load_products)
        self.layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            translator.translate('products.name'), 
            translator.translate('products.sku'), 
            translator.translate('products.category'), 
            translator.translate('products.price'), 
            translator.translate('products.stock')
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        self.load_products()

    def load_products(self):
        db = SessionLocal()
        search_text = self.search_input.text().lower()
        products = ProductService.get_all_products(db)
        
        filtered = [p for p in products if search_text in p.name.lower() or search_text in p.sku.lower()]
        
        self.table.setRowCount(len(filtered))
        for i, p in enumerate(filtered):
            self.table.setItem(i, 0, QTableWidgetItem(p.name))
            self.table.setItem(i, 1, QTableWidgetItem(p.sku))
            self.table.setItem(i, 2, QTableWidgetItem(p.category.name))
            self.table.setItem(i, 3, QTableWidgetItem(f'{p.price:.2f}'))
            self.table.setItem(i, 4, QTableWidgetItem(str(p.stock_quantity)))
        db.close()

    def open_add_dialog(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            db = SessionLocal()
            ProductService.create_product(db, **data, user_id=self.user.id)
            db.close()
            self.load_products()
