from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QTableView, QHeaderView, QMessageBox, QDialog, 
                             QFormLayout, QComboBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from src.core.translator import translator
from src.services.parcel_service import ParcelService
from src.models.database import SessionLocal
from src.models.sale_parcel import Parcel, ParcelStatus
from src.ui.components.parcel_model import ParcelTableModel

class ParcelManagement(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
        self.load_parcels()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel(translator.translate('parcels.title'))
        self.title_label.setObjectName('header')
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("↻ Refresh")
        self.refresh_btn.clicked.connect(self.load_parcels)
        header_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(header_layout)

        # Search Area
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Client or Phone...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.filter_parcels)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

        # Table View
        self.source_model = ParcelTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setAlternatingRowColors(True)
        
        # Context Menu or Selection-based actions for safety
        self.table_view.doubleClicked.connect(self.handle_action_request)
        self.layout.addWidget(self.table_view)

        # Action Bar (Bottom)
        self.action_layout = QHBoxLayout()
        self.collect_btn = QPushButton("💰 COLLECT MONEY")
        self.collect_btn.setObjectName("primary")
        self.collect_btn.clicked.connect(self.collect_selected)
        
        self.status_btn = QPushButton("🔄 UPDATE STATUS")
        self.status_btn.clicked.connect(self.update_selected_status)
        
        self.action_layout.addWidget(self.collect_btn)
        self.action_layout.addWidget(self.status_btn)
        self.action_layout.addStretch()
        self.layout.addLayout(self.action_layout)

    def load_parcels(self):
        db = SessionLocal()
        parcels = db.query(Parcel).all()
        self.source_model.update_data(parcels)
        db.close()

    def filter_parcels(self, text):
        self.proxy_model.setFilterFixedString(text)

    def get_selected_parcel(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Selection Required", "Please select a row first.")
            return None
        
        source_index = self.proxy_model.mapToSource(indexes[0])
        return self.source_model.get_parcel(source_index.row())

    def collect_selected(self):
        parcel = self.get_selected_parcel()
        if not parcel: return
        
        if parcel.is_money_collected:
            QMessageBox.information(self, "Already Collected", "This money is already in the register.")
            return

        # CRITICAL SAFETY CHECK (PHASE 7)
        confirm = QMessageBox.question(
            self, "Confirm Collection",
            f"Are you sure you want to collect {parcel.total_amount:,.2f} DA from {parcel.client_name}?\n"
            "This will update the cash register and create an audit log.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            db = SessionLocal()
            success = ParcelService.collect_parcel_money(db, parcel.id, parcel.total_amount, self.user.id)
            db.close()
            if success:
                self.load_parcels()
                QMessageBox.information(self, "Success", "Collection recorded successfully.")

    def update_selected_status(self):
        parcel = self.get_selected_parcel()
        if not parcel: return

        # Status Selection Dialog (Surgical change for safety)
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Status")
        layout = QFormLayout(dialog)
        
        status_combo = QComboBox()
        status_options = [ParcelStatus.CREATED, ParcelStatus.IN_TRANSIT, ParcelStatus.DELIVERED, ParcelStatus.RETURNED]
        status_combo.addItems([s.upper() for s in status_options])
        status_combo.setCurrentText(parcel.status.upper())
        
        layout.addRow("New Status:", status_combo)
        
        btns = QHBoxLayout()
        save = QPushButton("Update")
        save.clicked.connect(dialog.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(dialog.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_status = status_combo.currentText().lower()
            
            # CONFIRMATION (PHASE 7)
            confirm = QMessageBox.question(
                self, "Confirm Status Change",
                f"Change status to {new_status.upper()}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                db = SessionLocal()
                ParcelService.update_parcel_status(db, parcel.id, new_status, self.user.id)
                db.close()
                self.load_parcels()

    def handle_action_request(self, index):
        # Double click to open update status or collect
        self.update_selected_status()
