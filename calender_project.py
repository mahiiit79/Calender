from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import sys

# فرض کنیم فایل بالا ShamsiCalendar.py ذخیره شده است
from source import ShamsiCalendarWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تقویم شمسی PyQt5")
        self.resize(300, 350)

        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.calendar = ShamsiCalendarWidget()
        layout.addWidget(self.calendar)

        self.calendar.dateChanged.connect(self.on_date_changed)

    def on_date_changed(self, year, month, day):
        print(f"تاریخ انتخاب شده: {year}/{month}/{day}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
