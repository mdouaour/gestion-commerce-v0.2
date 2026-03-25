from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from src.core.translator import translator

class ProductTableModel(QAbstractTableModel):
    def __init__(self, products=None):
        super().__init__()
        self._products = products or []
        self._headers = [
            translator.translate('products.name'),
            translator.translate('products.sku'),
            translator.translate('products.category'),
            translator.translate('products.price'),
            translator.translate('products.stock')
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self._products)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        product = self._products[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0: return product.name
            if col == 1: return product.sku
            if col == 2: return product.category.name
            if col == 3: return f"{product.price:,.2f}"
            if col == 4: return str(product.stock_quantity)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col >= 3: return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        # Professional touch: Blue tint for read-only cells or specific columns
        if role == Qt.ItemDataRole.BackgroundRole:
            if col == 1: # SKU is unique/special
                return None # Or a very light blue if we want
        
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

    def update_data(self, products):
        self.beginResetModel()
        self._products = products
        self.endResetModel()

    def get_product(self, row):
        if 0 <= row < len(self._products):
            return self._products[row]
        return None
