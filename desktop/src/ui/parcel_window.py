from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, QComboBox, QDoubleSpinBox
from PyQt6.QtCore import Qt
from src.core.translator import translator
from src.services.parcel_service import ParcelService
from src.models.database import SessionLocal
from src.models.sale_parcel import Parcel

class ParcelManagement(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel(translator.translate('parcels.title'))
        self.title_label.setObjectName('header')
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            translator.translate('parcels.client_name'),
            translator.translate('parcels.phone'),
            translator.translate('parcels.status'),
            translator.translate('parcels.total'),
            translator.translate('parcels.is_collected'),
            translator.translate('parcels.collect_btn'),
            translator.translate('parcels.update_status')
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        self.load_parcels()

    def load_parcels(self):
        db = SessionLocal()
        parcels = db.query(Parcel).all()
        self.table.setRowCount(len(parcels))
        
        for i, p in enumerate(parcels):
            self.table.setItem(i, 0, QTableWidgetItem(p.client_name))
            self.table.setItem(i, 1, QTableWidgetItem(p.client_phone))
            self.table.setItem(i, 2, QTableWidgetItem(p.status))
            self.table.setItem(i, 3, QTableWidgetItem(f'{p.total_amount:.2f}'))
            self.table.setItem(i, 4, QTableWidgetItem('Yes' if p.is_money_collected else 'No'))
            
            # Collect Button
            collect_btn = QPushButton(translator.translate('parcels.collect_btn'))
            collect_btn.setEnabled(not p.is_money_collected)
            collect_btn.clicked.connect(lambda checked, pid=p.id, amt=p.total_amount: self.collect_money(pid, amt))
            self.table.setCellWidget(i, 5, collect_btn)
            
            # Status Button (Simplified for now)
            status_btn = QPushButton(translator.translate('parcels.update_status'))
            status_btn.clicked.connect(lambda checked, pid=p.id: self.update_status(pid))
            self.table.setCellWidget(i, 6, status_btn)
        db.close()

    def collect_money(self, parcel_id, amount):
        db = SessionLocal()
        ParcelService.collect_parcel_money(db, parcel_id, amount, self.user.id)
        db.close()
        self.load_parcels()
        QMessageBox.information(self, "Success", "Money collected successfully.")

    def update_status(self, parcel_id):
        # Simplified status rotation for demo
        db = SessionLocal()
        parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
        new_status = 'delivered' if parcel.status == 'created' else 'returned'
        ParcelService.update_parcel_status(db, parcel_id, new_status, self.user.id)
        db.close()
        self.load_parcels()
