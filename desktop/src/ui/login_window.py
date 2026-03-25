from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from src.core.translator import translator
from src.services.auth_service import AuthService
from src.models.database import SessionLocal
from src.ui.styles import get_main_style

class LoginWindow(QWidget):
    login_success = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.users = []
        self.init_ui()
        self.load_users()
        translator.language_changed.connect(self.update_ui_text)

    def init_ui(self):
        self.setWindowTitle(translator.translate('login.title'))
        self.setFixedSize(450, 550)
        self.setStyleSheet(get_main_style(translator.current_lang == 'ar'))

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.main_layout)

        # Header
        self.logo = QLabel('G-POS SYSTEM')
        self.logo.setObjectName('header')
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        self.main_layout.addWidget(self.logo)

        self.subtitle = QLabel("Select User & Enter Password")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        self.main_layout.addWidget(self.subtitle)

        # User Selection
        self.user_combo = QComboBox()
        self.user_combo.setMinimumHeight(45)
        self.user_combo.setStyleSheet("font-size: 16px; padding: 5px;")
        self.main_layout.addWidget(self.user_combo)

        # Password (Focused by default)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText(translator.translate('login.passwordLabel'))
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet("font-size: 18px; padding: 10px;")
        # CRITICAL: Allow Enter key to trigger login
        self.password_input.returnPressed.connect(self.handle_login)
        self.main_layout.addWidget(self.password_input)

        # Login Button
        self.login_btn = QPushButton(translator.translate('login.signInButton'))
        self.login_btn.setMinimumHeight(55)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #3498db; color: white; border-radius: 5px;")
        self.login_btn.clicked.connect(self.handle_login)
        self.main_layout.addWidget(self.login_btn)

        # Error Label
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: #e74c3c; font-size: 13px; font-weight: bold;')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.error_label)

        # Language Switcher
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['fr', 'ar', 'en'])
        self.lang_combo.setCurrentText(translator.current_lang)
        self.lang_combo.currentTextChanged.connect(translator.set_language)
        lang_layout.addStretch()
        lang_layout.addWidget(QLabel("Lang:"))
        lang_layout.addWidget(self.lang_combo)
        self.main_layout.addLayout(lang_layout)

        # Auto-focus password
        self.password_input.setFocus()

    def load_users(self):
        db = SessionLocal()
        try:
            from src.models.user import User
            self.users = db.query(User).filter(User.is_active == True).all()
            for user in self.users:
                self.user_combo.addItem(user.username, user)
        finally:
            db.close()

    def handle_login(self):
        # Clear previous error
        self.error_label.setText("")
        self.error_label.setStyleSheet('color: #e74c3c; font-size: 13px; font-weight: bold;')
        
        username = self.user_combo.currentText()
        password = self.password_input.text()
        
        if not password:
            self.error_label.setText("Please enter your password")
            return

        db = SessionLocal()
        try:
            user, error_code = AuthService.authenticate_user(db, username, password)
            if user:
                self.login_success.emit(user)
            else:
                error_msg = translator.translate(f'errors.{error_code}')
                self.error_label.setText(error_msg)
                self.password_input.clear()
                self.password_input.setFocus()
        finally:
            db.close()

    def update_ui_text(self, lang):
        self.setWindowTitle(translator.translate('login.title'))
        self.password_input.setPlaceholderText(translator.translate('login.passwordLabel'))
        self.login_btn.setText(translator.translate('login.signInButton'))
        self.setStyleSheet(get_main_style(lang == 'ar'))
        if lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
