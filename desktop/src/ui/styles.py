from src.core.theme import Theme

def get_main_style(rtl=False):
    alignment = "right" if rtl else "left"
    opp_alignment = "left" if rtl else "right"

    return f"""
        /* Main Window & Core Widgets */
        QMainWindow {{ 
            background-color: {Theme.BACKGROUND}; 
        }}
        
        QWidget {{ 
            font-family: {Theme.FONT_FAMILY}; 
            font-size: {Theme.FONT_SIZE_DEFAULT}px; 
            color: {Theme.TEXT_MAIN};
        }}

        /* Typography */
        QLabel#header {{ 
            font-size: {Theme.FONT_SIZE_TITLE}px; 
            font-weight: {Theme.FONT_WEIGHT_HEAVY}; 
            color: {Theme.DARK_BLUE}; 
            margin-bottom: 10px; 
        }}
        
        QLabel#subtitle {{ 
            font-size: {Theme.FONT_SIZE_SUBTITLE}px; 
            color: {Theme.NEUTRAL}; 
            margin-bottom: 20px; 
        }}

        /* Input Fields */
        QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {{ 
            padding: 10px; 
            border: {Theme.BORDER_WIDTH}px solid {Theme.BORDER}; 
            border-radius: {Theme.RADIUS_DEFAULT}px; 
            background: {Theme.WHITE}; 
            selection-background-color: {Theme.PRIMARY};
        }}
        
        QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{ 
            border: {Theme.BORDER_WIDTH}px solid {Theme.PRIMARY}; 
        }}

        /* Buttons */
        QPushButton {{ 
            padding: 10px 20px; 
            border-radius: {Theme.RADIUS_DEFAULT}px; 
            background-color: {Theme.PRIMARY}; 
            color: {Theme.WHITE}; 
            border: none; 
            font-weight: {Theme.FONT_WEIGHT_BOLD}; 
        }}
        
        QPushButton:hover {{ 
            background-color: {Theme.PRIMARY_HOVER}; 
        }}
        
        QPushButton#primary {{ background-color: {Theme.SUCCESS}; }}
        QPushButton#primary:hover {{ background-color: {Theme.SUCCESS_HOVER}; }}

        QPushButton#danger {{ background-color: {Theme.DANGER}; }}
        QPushButton#danger:hover {{ background-color: {Theme.DANGER_HOVER}; }}

        /* Sidebar Styling */
        QFrame#sidebar {{
            background-color: {Theme.DARK_BLUE};
            border-{opp_alignment}: 1px solid {Theme.BORDER};
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
            color: {Theme.WHITE};
        }}
        
        QPushButton#nav_btn[active="true"] {{
            background-color: #3d566e;
            color: {Theme.WHITE};
            font-weight: bold;
            border-{alignment}: 4px solid {Theme.PRIMARY};
        }}

        /* Sidebar Toggle */
        QPushButton#sidebar_toggle {{
            background: transparent;
            font-size: 18px;
            padding: 5px;
            margin-bottom: 10px;
        }}

        /* Divider Line */
        QFrame#divider {{
            background-color: #34495e;
            max-height: 1px;
            margin: 10px 5px;
        }}

        /* Tables & Tabs (Omitted for brevity, assumed unchanged but using Theme) */
    """
