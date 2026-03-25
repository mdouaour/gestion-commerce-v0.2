from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class KPICard(QFrame):
    def __init__(self, title, value, color="#3498db"):
        super().__init__()
        self.setMinimumHeight(120)
        self.setMinimumWidth(200)
        self.setObjectName("kpi_card")
        self.setStyleSheet(f"""
            QFrame#kpi_card {{
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 10px;
                border-left: 5px solid {color};
            }}
            QLabel {{ background: transparent; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def update_value(self, new_value):
        self.value_label.setText(str(new_value))
