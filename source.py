from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QGridLayout
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from datetime import datetime, date


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0,31,59,90,120,151,181,212,243,273,304,334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def jalali_to_gregorian(jy, jm, jd):
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    months = [0,31,28,31,30,31,30,31,31,30,31,30,31]
    leap = (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)
    if leap:
        months[2] = 29
    gm = 0
    while gm < 13 and gd > months[gm]:
        gd -= months[gm]
        gm += 1
    return gy, gm, gd


def is_leap_jalali(year):
    breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111,
              1181, 1210, 1635, 2060, 2097, 2192, 2262,
              2324, 2394, 2456, 3178]
    leap = False
    for i in range(1, len(breaks)):
        if year < breaks[i]:
            break
    b = year - breaks[i-1]
    leap = (((b % 33) == 1) or ((b % 33) == 5) or ((b % 33) == 9) or
            ((b % 33) == 13) or ((b % 33) == 17) or ((b % 33) == 22) or
            ((b % 33) == 26) or ((b % 33) == 30))
    return leap


class ShamsiCalendarWidget(QWidget):
    dateChanged = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(15, 15, 15, 15)
        self.layout().setSpacing(12)

        now = datetime.now()
        jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
        self.current_year = jy
        self.current_month = jm
        self.selected_day = jd

        self.font = QFont("BNazanin", 12)
        self.font_bold = QFont("BNazanin", 13, QFont.Bold)

        self.init_header()
        self.init_weekdays()
        self.init_grid()

        self.setStyleSheet("""
            QWidget {
                background-color: #6a0dad;
                border-radius: 12px;
            }
            QPushButton {
                background-color: #e8daef;
                color: #4a235a;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #af7ac5;
                color: white;
            }
            QPushButton:checked {
                background-color: #4a235a;
                color: white;
                border: 2px solid #d2b4de;
            }
        """)

        self.update_calendar()

    def init_header(self):
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignRight)

        lbl_year = QLabel("سال:")
        lbl_year.setFont(self.font_bold)
        lbl_year.setStyleSheet("color: white;")

        self.year_combo = QComboBox()
        self.year_combo.setFont(self.font)
        for y in reversed(range(1300, 1451)):
            self.year_combo.addItem(str(y))
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self.update_calendar)

        lbl_month = QLabel("ماه:")
        lbl_month.setFont(self.font_bold)
        lbl_month.setStyleSheet("color: white;")

        self.month_combo = QComboBox()
        self.month_combo.setFont(self.font)
        self.month_combo.addItems([
            "فروردین", "اردیبهشت", "خرداد", "تیر",
            "مرداد", "شهریور", "مهر", "آبان",
            "آذر", "دی", "بهمن", "اسفند"
        ])
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.currentIndexChanged.connect(self.update_calendar)

        header_layout.addWidget(lbl_year)
        header_layout.addWidget(self.year_combo)
        header_layout.addSpacing(20)
        header_layout.addWidget(lbl_month)
        header_layout.addWidget(self.month_combo)
        self.layout().addLayout(header_layout)

        combo_style = """
            QComboBox {
                background-color: #b491d2;
                color: #2c003e;
                border: 1px solid #8e44ad;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #d2b4de;
            }
        """
        self.year_combo.setStyleSheet(combo_style)
        self.month_combo.setStyleSheet(combo_style)

    def init_weekdays(self):
        weekdays_layout = QHBoxLayout()
        weekdays = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        for wd in weekdays:
            lbl = QLabel(wd)
            lbl.setFont(self.font_bold)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(40, 36)
            lbl.setStyleSheet("""
                background-color: #9b59b6;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            """)
            weekdays_layout.addWidget(lbl)
        self.layout().addLayout(weekdays_layout)

    def init_grid(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(8)
        self.layout().addLayout(self.grid)
        self.day_buttons = []

    def update_calendar(self):
        for btn in self.day_buttons:
            self.grid.removeWidget(btn)
            btn.deleteLater()
        self.day_buttons.clear()

        year = int(self.year_combo.currentText())
        month = self.month_combo.currentIndex() + 1

        g_year, g_month, g_day = jalali_to_gregorian(year, month, 1)
        first_weekday = date(g_year, g_month, g_day).weekday()
        first_weekday = (first_weekday + 2) % 7

        days_in_month = 31 if month <= 6 else 30 if month <= 11 else (30 if is_leap_jalali(year) else 29)

        day_num = 1
        for row in range(6):
            for col in range(7):
                if row == 0 and col < first_weekday:
                    self.grid.addWidget(QLabel(""), row, col)
                elif day_num <= days_in_month:
                    btn = QPushButton(str(day_num))
                    btn.setCheckable(True)
                    btn.clicked.connect(lambda _, d=day_num: self.select_day(d))
                    self.grid.addWidget(btn, row, col)
                    self.day_buttons.append(btn)
                    if day_num == self.selected_day and year == self.current_year and month == self.current_month:
                        btn.setChecked(True)
                    day_num += 1
                else:
                    self.grid.addWidget(QLabel(""), row, col)

        self.current_year = year
        self.current_month = month

    def select_day(self, day):
        self.selected_day = day
        for btn in self.day_buttons:
            btn.setChecked(btn.text() == str(day))
        self.dateChanged.emit(self.current_year, self.current_month, self.selected_day)
