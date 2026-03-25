from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QTableView, QHeaderView, QDialog, QFormLayout, 
                             QComboBox, QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from src.core.translator import translator
from src.services.product_service import ProductService
from src.models.database import SessionLocal
from src.models.product import Category
from src.ui.components.product_model import ProductTableModel

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(translator.translate('products.add_new'))
        self.setFixedWidth(450)
        layout = QFormLayout(self)
        layout.setSpacing(15)

        self.name_input = QLineEdit()
        self.sku_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(10000000)
        self.price_input.setSuffix(" DA")
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(100000)
        
        self.cat_combo = QComboBox()
        db = SessionLocal()
        categories = db.query(Category).all()
        for cat in categories:
            self.cat_combo.addItem(cat.name, cat.id)
        db.close()

        layout.addRow(translator.translate('products.name') + ':', self.name_input)
        layout.addRow(translator.translate('products.sku') + ':', self.sku_input)
        layout.addRow(translator.translate('products.category') + ':', self.cat_combo)
        layout.addRow(translator.translate('products.price') + ':', self.price_input)
        layout.addRow(translator.translate('products.stock') + ':', self.stock_input)

        btns = QHBoxLayout()
        self.save_btn = QPushButton(translator.translate('products.save'))
        self.save_btn.setObjectName('primary')
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
        self.load_products()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Header Area
        header_layout = QHBoxLayout()
        self.title_label = QLabel(translator.translate('products.title'))
        self.title_label.setObjectName('header')
        
        self.add_btn = QPushButton("+ " + translator.translate('products.add_new'))
        self.add_btn.setObjectName('primary')
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        self.layout.addLayout(header_layout)

        # Search Area
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 " + translator.translate('sales.product_search') + " (Name or SKU)")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

        # Advanced Data View (ERP Pattern)
        self.source_model = ProductTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1) # Filter all columns

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        
        self.layout.addWidget(self.table_view)

    def load_products(self):
        db = SessionLocal()
        products = ProductService.get_all_products(db)
        self.source_model.update_data(products)
        db.close()

    def filter_products(self, text):
        self.proxy_model.setFilterFixedString(text)

    def open_add_dialog(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            db = SessionLocal()
            ProductService.create_product(db, **data, user_id=self.user.id)
            db.close()
            self.load_products()
