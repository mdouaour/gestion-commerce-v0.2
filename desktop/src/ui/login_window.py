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
        self.init_ui()
        translator.language_changed.connect(self.update_ui_text)

    def init_ui(self):
        self.setWindowTitle(translator.translate('login.title'))
        self.setFixedSize(400, 500)
        self.setStyleSheet(get_main_style(translator.current_lang == 'ar'))

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.main_layout)

        # Logo/Icon Placeholder
        self.logo = QLabel('POS DESKTOP')
        self.logo.setObjectName('header')
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.logo)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(translator.translate('login.usernameLabel'))
        self.main_layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText(translator.translate('login.passwordLabel'))
        self.main_layout.addWidget(self.password_input)

        # Login Button
        self.login_btn = QPushButton(translator.translate('login.signInButton'))
        self.login_btn.clicked.connect(self.handle_login)
        self.main_layout.addWidget(self.login_btn)

        # Error Label
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: red; font-size: 12px;')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.error_label)

        # Language Switcher
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['fr', 'ar', 'en'])
        self.lang_combo.setCurrentText(translator.current_lang)
        self.lang_combo.currentTextChanged.connect(translator.set_language)
        lang_layout.addStretch()
        lang_layout.addWidget(self.lang_combo)
        self.main_layout.addLayout(lang_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        db = SessionLocal()
        try:
            user, error_code = AuthService.authenticate_user(db, username, password)
            if user:
                self.login_success.emit(user)
            else:
                # Map error code to translated message
                error_msg = translator.translate(f'errors.{error_code}')
                self.error_label.setText(error_msg)
        finally:
            db.close()

    def update_ui_text(self, lang):
        self.setWindowTitle(translator.translate('login.title'))
        self.username_input.setPlaceholderText(translator.translate('login.usernameLabel'))
        self.password_input.setPlaceholderText(translator.translate('login.passwordLabel'))
        self.login_btn.setText(translator.translate('login.signInButton'))
        self.setStyleSheet(get_main_style(lang == 'ar'))
        if lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
