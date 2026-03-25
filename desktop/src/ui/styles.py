def get_main_style(rtl=False):
    # Professional Color Palette
    PRIMARY = "#3498db"      # Blue (Action)
    PRIMARY_HOVER = "#2980b9"
    SUCCESS = "#27ae60"      # Green (Safe/Complete)
    SUCCESS_HOVER = "#2ecc71"
    DANGER = "#e74c3c"       # Red (Delete/Cancel)
    DANGER_HOVER = "#c0392b"
    DARK_BLUE = "#2c3e50"    # Headers/Sidebar
    LIGHT_GRAY = "#f5f6fa"   # Background
    BORDER = "#dcdde1"       # Borders
    TEXT_MAIN = "#2f3640"    # Text Color

    alignment = "right" if rtl else "left"

    return f"""
        /* Main Window & Core Widgets */
        QMainWindow {{ 
            background-color: {LIGHT_GRAY}; 
        }}
        
        QWidget {{ 
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif; 
            font-size: 14px; 
            color: {TEXT_MAIN};
        }}

        /* Typography */
        QLabel#header {{ 
            font-size: 26px; 
            font-weight: 700; 
            color: {DARK_BLUE}; 
            margin-bottom: 10px; 
        }}
        
        QLabel#subtitle {{ 
            font-size: 14px; 
            color: #7f8c8d; 
            margin-bottom: 20px; 
        }}

        /* Input Fields */
        QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {{ 
            padding: 10px; 
            border: 2px solid {BORDER}; 
            border-radius: 6px; 
            background: white; 
            selection-background-color: {PRIMARY};
        }}
        
        QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{ 
            border: 2px solid {PRIMARY}; 
        }}

        /* Buttons */
        QPushButton {{ 
            padding: 12px 24px; 
            border-radius: 6px; 
            background-color: {PRIMARY}; 
            color: white; 
            border: none; 
            font-weight: 600; 
            font-size: 14px;
        }}
        
        QPushButton:hover {{ 
            background-color: {PRIMARY_HOVER}; 
        }}
        
        QPushButton:pressed {{
            background-color: {DARK_BLUE};
        }}

        QPushButton#primary {{ 
            background-color: {SUCCESS}; 
        }}
        
        QPushButton#primary:hover {{ 
            background-color: {SUCCESS_HOVER}; 
        }}

        QPushButton#danger {{ 
            background-color: {DANGER}; 
        }}
        
        QPushButton#danger:hover {{ 
            background-color: {DANGER_HOVER}; 
        }}

        /* Sidebar Styling */
        QFrame#sidebar {{
            background-color: {DARK_BLUE};
            border-right: 1px solid {BORDER};
        }}
        
        QPushButton#nav_btn {{
            text-align: {alignment};
            background: transparent;
            color: #ecf0f1;
            border: none;
            padding: 12px 20px;
            border-radius: 0px;
            font-size: 15px;
        }}
        
        QPushButton#nav_btn:hover {{
            background-color: #34495e;
            color: white;
        }}
        
        QPushButton#nav_btn_active {{
            background-color: {PRIMARY};
            color: white;
            font-weight: bold;
        }}

        /* Tables & Data */
        QTableWidget, QTableView {{ 
            background: white; 
            border: 1px solid {BORDER}; 
            gridline-color: {BORDER};
            alternate-background-color: #fafbfc;
        }}
        
        QHeaderView::section {{
            background-color: #f8f9fa;
            padding: 8px;
            border: none;
            border-bottom: 2px solid {BORDER};
            font-weight: bold;
            color: {DARK_BLUE};
        }}

        /* Tabs */
        QTabWidget::pane {{ border: 1px solid {BORDER}; }}
        QTabBar::tab {{
            background: #ecf0f1;
            padding: 10px 20px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background: white;
            border: 1px solid {BORDER};
            border-bottom: none;
        }}
    """
