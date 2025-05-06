# ui/form_base.py

import re
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLabel, QMessageBox, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QFont, QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression

from ui.utils import icon_label

class EmployeeFormDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFont(QFont("Segoe UI", 10))
        self.form = QFormLayout(self)
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
        """Установить фиксированную высоту группе виджетов."""
        for w in widgets:
            w.setFixedHeight(height)

    def apply_phone_validator(self, widgets: list):
        """Применить единый регэксп-валидатор для телефонов."""
        pattern = QRegularExpression(r'^\+?\d{5,15}$')
        val = QRegularExpressionValidator(pattern, self)
        for w in widgets:
            w.setValidator(val)

    def apply_regex_validator(self, widgets: list, regex: str):
        """Применить QRegularExpressionValidator с заданным шаблоном."""
        pattern = QRegularExpression(regex)
        val = QRegularExpressionValidator(pattern, self)
        for w in widgets:
            w.setValidator(val)

    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        QMessageBox.warning(self, title, message)
