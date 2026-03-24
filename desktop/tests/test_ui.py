import pytest
from PyQt6.QtWidgets import QApplication
from src.ui.login_window import LoginWindow
from src.core.translator import translator
import sys

@pytest.fixture
def app(qtbot):
    return QApplication.instance() or QApplication(sys.argv)

def test_login_window_init(qtbot):
    window = LoginWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == translator.translate('login.title')

def test_language_switch_ui(qtbot):
    window = LoginWindow()
    qtbot.addWidget(window)
    
    # Switch to Arabic
    qtbot.keyClicks(window.lang_combo, 'ar')
    window.lang_combo.setCurrentText('ar')
    
    assert translator.current_lang == 'ar'
    assert window.windowTitle() == 'مرحباً بعودتك'
