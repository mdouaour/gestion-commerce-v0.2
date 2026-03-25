import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class SalesTrendChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # Style the chart
        fig.patch.set_facecolor('#f5f6fa')
        self.axes.set_facecolor('#ffffff')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        
        super().__init__(fig)

    def plot(self, dates, values):
        self.axes.clear()
        self.axes.plot(dates, values, marker='o', linestyle='-', color='#3498db', linewidth=2)
        self.axes.fill_between(dates, values, color='#3498db', alpha=0.1)
        self.axes.set_title('30-Day Sales Trend (DZD)', fontsize=12, fontweight='bold', color='#2c3e50')
        self.axes.tick_params(axis='x', rotation=45, labelsize=8)
        self.axes.tick_params(axis='y', labelsize=8)
        self.draw()
