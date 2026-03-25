from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from src.core.translator import translator

class ParcelTableModel(QAbstractTableModel):
    def __init__(self, parcels=None):
        super().__init__()
        self._parcels = parcels or []
        self._headers = [
            translator.translate('parcels.client_name'),
            translator.translate('parcels.phone'),
            translator.translate('parcels.status'),
            translator.translate('parcels.total'),
            translator.translate('parcels.is_collected'),
            "Action"
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self._parcels)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        parcel = self._parcels[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0: return parcel.client_name
            if col == 1: return parcel.client_phone
            if col == 2: return parcel.status.upper()
            if col == 3: return f"{parcel.total_amount:,.2f} DA"
            if col == 4: return "✓ COLLECTED" if parcel.is_money_collected else "⏳ PENDING"
            if col == 5: return "" # Reserved for button

        if role == Qt.ItemDataRole.ForegroundRole:
            if col == 2:
                if parcel.status == 'delivered': return Qt.GlobalColor.darkGreen
                if parcel.status == 'returned': return Qt.GlobalColor.red
                if parcel.status == 'in_delivery': return Qt.GlobalColor.darkBlue
                if parcel.status == 'exchanged': return Qt.GlobalColor.magenta
            if col == 4:
                return Qt.GlobalColor.darkGreen if parcel.is_money_collected else Qt.GlobalColor.darkYellow

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col >= 3: return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

    def update_data(self, parcels):
        self.beginResetModel()
        self._parcels = parcels
        self.endResetModel()

    def get_parcel(self, row):
        if 0 <= row < len(self._parcels):
            return self._parcels[row]
        return None
