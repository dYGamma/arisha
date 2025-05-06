# ui/form_base.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QScrollArea, QWidget,
    QFormLayout, QLabel, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont, QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression
from ui.utils import icon_label

class EmployeeFormDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFont(QFont("Segoe UI", 10))
        self.setSizeGripEnabled(True)  # Разрешить изменение размера

        # Внешний лэйаут
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        # Область прокрутки
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        # Контейнер внутри прокрутки
        container = QWidget()
        scroll.setWidget(container)

        # Форма
        self.form = QFormLayout(container)
        self.form.setContentsMargins(24, 24, 24, 24)
        self.form.setVerticalSpacing(12)

    def add_form_row(self, label_text: str, widget, icon_name: str = 'edit'):
        """
        Добавить в форму строку с иконкой и текстовым лейблом.
        """
        container = QWidget()
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(4)
        hl.addWidget(icon_label(icon_name, 20))
        hl.addWidget(QLabel(label_text))
        self.form.addRow(container, widget)

    def set_fixed_heights(self, widgets: list, height: int = 32):
        """
        Задать фиксированную высоту группе виджетов.
        """
        for w in widgets:
            w.setFixedHeight(height)

    def apply_phone_validator(self, widgets: list):
        """
        Применить валидатор телефонного номера (+?digits 5-15).
        """
        pattern = QRegularExpression(r'^\+?\d{5,15}$')
        val = QRegularExpressionValidator(pattern, self)
        for w in widgets:
            w.setValidator(val)

    def apply_regex_validator(self, widgets: list, regex: str):
        """
        Применить QRegularExpressionValidator с заданным шаблоном.
        """
        pattern = QRegularExpression(regex)
        val = QRegularExpressionValidator(pattern, self)
        for w in widgets:
            w.setValidator(val)

    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        QMessageBox.warning(self, title, message)
