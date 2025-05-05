# ui/edit_widget.py

import re
import logging
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDateEdit,
    QPushButton, QMessageBox, QLabel
)
from PyQt5.QtGui import QFont, QRegExpValidator
from PyQt5.QtCore import QDate, QRegExp, Qt
from database import SessionLocal
from controllers import get_employee, update_employee
from ui.utils import icon_label

logger = logging.getLogger(__name__)

class EditWidget(QDialog):
    def __init__(self, emp_id, parent=None):
        super().__init__(parent)
        self.emp_id = emp_id
        self.setWindowTitle("Редактировать сотрудника")
        self.setFixedSize(550, 650)
        self.setFont(QFont("Segoe UI", 10))

        # Верстка формы
        form = QFormLayout(self)
        form.setContentsMargins(24, 24, 24, 24)
        form.setVerticalSpacing(12)

        # Получаем данные сотрудника
        with SessionLocal() as db:
            emp = get_employee(db, emp_id)
            if not emp:
                QMessageBox.critical(self, "Ошибка", "Сотрудник не найден")
                self.reject()
                return

        # Поля с предзаполнением
        self.first_name = QLineEdit(emp.first_name)
        self.last_name  = QLineEdit(emp.last_name)
        self.position   = QLineEdit(emp.position)
        self.passport   = QLineEdit(emp.passport)

        self.birth_year = QSpinBox()
        self.birth_year.setRange(1900, QDate.currentDate().year())
        self.birth_year.setValue(emp.birth_year or QDate.currentDate().year())

        self.experience = QSpinBox()
        self.experience.setRange(0, 100)
        self.experience.setValue(emp.experience_years or 0)

        self.hire_date = QDateEdit(calendarPopup=True)
        self.hire_date.setDate(emp.hire_date or QDate.currentDate())

        self.mobile = QLineEdit(emp.phone_mobile)
        self.work   = QLineEdit(emp.phone_work)

        # Валидатор телефона
        rx = QRegExp(r'^\+?\d{5,15}$')
        val = QRegExpValidator(rx, self)
        self.mobile.setValidator(val)
        self.work.setValidator(val)

        self.vacation = QSpinBox()
        self.vacation.setRange(0, 365)
        self.vacation.setValue(emp.vacation_days_left or 0)

        # Установка высот
        for w in (
            self.first_name, self.last_name, self.position,
            self.passport, self.mobile, self.work
        ):
            w.setFixedHeight(32)
        for w in (self.birth_year, self.experience, self.vacation):
            w.setFixedHeight(32)
        self.hire_date.setFixedHeight(32)

        # Добавляем в форму
        fields = [
            ("Имя",            self.first_name),
            ("Фамилия",        self.last_name),
            ("Должность",      self.position),
            ("Паспорт",        self.passport),
            ("Год рождения",   self.birth_year),
            ("Стаж (лет)",     self.experience),
            ("Дата приёма",    self.hire_date),
            ("Моб. телефон",   self.mobile),
            ("Раб. телефон",   self.work),
            ("Отпуск (дн.)",   self.vacation),
        ]
        for label, widget in fields:
            form.addRow(icon_label('edit', 20), widget)

        # Кнопка сохранения
        btn = QPushButton("Сохранить")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)
        btn.clicked.connect(self._save)
        form.addRow(QLabel(), btn)

    def _save(self):
        # Базовая валидация
        if not all([
            self.first_name.text().strip(),
            self.last_name.text().strip(),
            self.position.text().strip()
        ]):
            QMessageBox.warning(self, "Ошибка", "Имя, фамилия и должность обязательны")
            return

        data = {
            "first_name":         self.first_name.text().strip(),
            "last_name":          self.last_name.text().strip(),
            "position":           self.position.text().strip(),
            "passport":           self.passport.text().strip(),
            "birth_year":         self.birth_year.value(),
            "experience_years":   self.experience.value(),
            "hire_date":          self.hire_date.date().toPyDate(),
            "phone_mobile":       self.mobile.text().strip(),
            "phone_work":         self.work.text().strip(),
            "vacation_days_left": self.vacation.value(),
        }

        try:
            with SessionLocal() as db:
                update_employee(db, self.emp_id, **data)
        except Exception as e:
            logger.error(f"Ошибка при обновлении: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")
            return

        QMessageBox.information(self, "Успех", "Данные обновлены")
        self.accept()
