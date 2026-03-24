import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Ensure we use the correct PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.translator import translator
from src.ui.login_window import LoginWindow
from src.ui.dashboard import DashboardWindow
from dotenv import load_dotenv

class POSApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_window = None

    def show_login(self, *args):
        if self.current_window:
             self.current_window.close()
        self.login_win = LoginWindow()
        self.login_win.login_success.connect(self.show_dashboard)
        self.login_win.show()
        self.current_window = self.login_win

    def show_dashboard(self, user):
        if self.current_window:
             self.current_window.close()
        self.dashboard_win = DashboardWindow(user)
        self.dashboard_win.logout_requested.connect(self.show_login)
        self.dashboard_win.show()
        self.current_window = self.dashboard_win

    def run(self):
        self.show_login()
        return self.app.exec()

if __name__ == '__main__':
    load_dotenv()
    translator.set_language(os.getenv('APP_LANG', 'fr'))

    pos_app = POSApplication()
    sys.exit(pos_app.run())
