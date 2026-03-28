from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class KPICard(QFrame):
    def __init__(self, title, value, color="#3498db", trend=None):
        super().__init__()
        self.setMinimumHeight(130)
        self.setMinimumWidth(220)
        self.color = color
        self.setObjectName("kpi_card")
        self.setStyleSheet(f"""
            QFrame#kpi_card {{
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 12px;
                border-left: 6px solid {color};
            }}
            QLabel {{ background: transparent; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel(title.upper())
        self.title_label.setStyleSheet("color: #7f8c8d; font-size: 13px; font-weight: 700; letter-spacing: 0.5px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 800;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.trend_label = QLabel(trend if trend else "")
        self.trend_label.setStyleSheet("color: #95a5a6; font-size: 12px; font-weight: 500;")
        self.trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not trend:
            self.trend_label.hide()
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.trend_label)

    def update_value(self, new_value, trend=None):
        self.value_label.setText(str(new_value))
        if trend:
            self.trend_label.setText(trend)
            self.trend_label.show()
        else:
            self.trend_label.hide()
