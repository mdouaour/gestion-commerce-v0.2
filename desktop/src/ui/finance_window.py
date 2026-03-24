from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, QDoubleSpinBox, QGroupBox
from PyQt6.QtCore import Qt
from src.core.translator import translator
from src.services.finance_service import FinanceService
from src.models.database import SessionLocal
from src.models.finance import CashRegister, CashTransaction

class WithdrawalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(translator.translate('finance.withdrawal'))
        layout = QFormLayout(self)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.reason_input = QLineEdit()
        layout.addRow(translator.translate('finance.amount') + ':', self.amount_input)
        layout.addRow(translator.translate('finance.reason') + ':', self.reason_input)
        btns = QHBoxLayout()
        self.save_btn = QPushButton(translator.translate('products.save'))
        self.save_btn.clicked.connect(self.accept)
        btns.addWidget(self.save_btn)
        layout.addRow(btns)

    def get_data(self):
        return self.amount_input.value(), self.reason_input.text()

class FinanceManagement(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.status_group = QGroupBox(translator.translate('finance.status'))
        status_layout = QVBoxLayout(self.status_group)
        self.balance_label = QLabel()
        self.balance_label.setStyleSheet('font-size: 24px; font-weight: bold; color: #27ae60;')
        self.state_label = QLabel()
        status_layout.addWidget(self.balance_label)
        status_layout.addWidget(self.state_label)
        btn_layout = QHBoxLayout()
        self.open_btn = QPushButton(translator.translate('finance.open_btn'))
        self.open_btn.clicked.connect(self.open_reg)
        self.close_btn = QPushButton(translator.translate('finance.close_btn'))
        self.close_btn.clicked.connect(self.close_reg)
        self.withdraw_btn = QPushButton(translator.translate('finance.withdrawal'))
        self.withdraw_btn.setObjectName('danger')
        self.withdraw_btn.clicked.connect(self.withdraw)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addWidget(self.withdraw_btn)
        status_layout.addLayout(btn_layout)
        self.layout.addWidget(self.status_group)
        self.layout.addWidget(QLabel(translator.translate('finance.history')))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['Date', 'Type', 'Amount', 'Reason'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        self.refresh_data()

    def refresh_data(self):
        db = SessionLocal()
        reg = db.query(CashRegister).first()
        if reg:
            self.balance_label.setText(f'{translator.translate("finance.balance")}: {reg.current_balance:.2f} DZD')
            status_text = translator.translate('finance.open') if reg.is_open else translator.translate('finance.closed')
            self.state_label.setText(f'{translator.translate("finance.status")}: {status_text}')
            self.open_btn.setEnabled(not reg.is_open)
            self.close_btn.setEnabled(reg.is_open)
            self.withdraw_btn.setEnabled(reg.is_open)
        txs = db.query(CashTransaction).order_by(CashTransaction.created_at.desc()).limit(50).all()
        self.table.setRowCount(len(txs))
        for i, tx in enumerate(txs):
            self.table.setItem(i, 0, QTableWidgetItem(tx.created_at.strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(i, 1, QTableWidgetItem(tx.type))
            self.table.setItem(i, 2, QTableWidgetItem(f'{tx.amount:+.2f}'))
            self.table.setItem(i, 3, QTableWidgetItem(tx.reason or ''))
        db.close()

    def open_reg(self):
        db = SessionLocal()
        FinanceService.open_register(db, self.user.id)
        db.close()
        self.refresh_data()

    def close_reg(self):
        db = SessionLocal()
        FinanceService.close_register(db, self.user.id)
        db.close()
        self.refresh_data()

    def withdraw(self):
        dialog = WithdrawalDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount, reason = dialog.get_data()
            db = SessionLocal()
            res, error = FinanceService.create_withdrawal(db, amount, reason, self.user.id)
            db.close()
            if error:
                QMessageBox.critical(self, 'Error', translator.translate(f'errors.{error}'))
            else:
                self.refresh_data()
