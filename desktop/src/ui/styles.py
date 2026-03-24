def get_main_style(rtl=False):
    return f"""
        QMainWindow {{ background-color: #f5f6fa; }}
        QWidget {{ font-family: 'Segoe UI', sans-serif; font-size: 14px; }}
        QLineEdit {{ padding: 10px; border: 1px solid #dcdde1; border-radius: 5px; background: white; }}
        QPushButton {{ padding: 10px 20px; border-radius: 5px; background-color: #3498db; color: white; border: none; font-weight: bold; }}
        QPushButton:hover {{ background-color: #2980b9; }}
        QPushButton#primary {{ background-color: #27ae60; }}
        QPushButton#danger {{ background-color: #e74c3c; }}
        QLabel#header {{ font-size: 24px; font-weight: bold; color: #2f3640; margin-bottom: 20px; }}
        QTableWidget {{ background: white; border: 1px solid #dcdde1; }}
        QComboBox {{ padding: 5px; border: 1px solid #dcdde1; border-radius: 5px; }}
    """
