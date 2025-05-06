# ui/edit_widget.py

import logging
from PyQt5.QtWidgets import (
    QLineEdit, QSpinBox, QDateEdit, QPushButton, QMessageBox, QLabel
)
from PyQt5.QtCore import QDate, Qt
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from controllers import get_employee, update_employee
from ui.form_base import EmployeeFormDialog
from main import DATE_FORMAT

logger = logging.getLogger(__name__)

class EditWidget(EmployeeFormDialog):
    def __init__(self, emp_id, parent=None):
        super().__init__("Редактировать сотрудника", parent)
        self.emp_id = emp_id

        # Разрешаем изменять размер, задаём стартовый
        self.setSizeGripEnabled(True)
        self.resize(500, 700)

        # Загрузка данных из БД
        try:
            with SessionLocal() as db:
                emp = get_employee(db, emp_id)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД при загрузке сотрудника: {e}")
            self.show_error("Ошибка", "Не удалось загрузить данные сотрудника")
            self.reject()
            return

        if not emp:
            self.show_error("Ошибка", "Сотрудник не найден")
            self.reject()
            return

        # Поля ввода
        self.first_name = QLineEdit(emp.first_name)
        self.last_name  = QLineEdit(emp.last_name)
        self.position   = QLineEdit(emp.position)
        self.passport   = QLineEdit(emp.passport or "")

        self.birth_year = QSpinBox()
        self.birth_year.setRange(1900, QDate.currentDate().year())
        if emp.birth_year is not None:
            self.birth_year.setValue(emp.birth_year)
        else:
            self.birth_year.setValue(QDate.currentDate().year())

        self.experience = QSpinBox()
        self.experience.setRange(0, 100)
        if emp.experience_years is not None:
            self.experience.setValue(emp.experience_years)
        else:
            self.experience.setValue(0)

        self.hire_date = QDateEdit(calendarPopup=True)
        if emp.hire_date:
            self.hire_date.setDate(emp.hire_date)
        else:
            self.hire_date.setDate(QDate.currentDate())
        self.hire_date.setDisplayFormat(DATE_FORMAT)

        self.mobile = QLineEdit(emp.phone_mobile or "")
        self.work   = QLineEdit(emp.phone_work or "")

        self.vacation = QSpinBox()
        self.vacation.setRange(0, 365)
        if emp.vacation_days_left is not None:
            self.vacation.setValue(emp.vacation_days_left)
        else:
            self.vacation.setValue(0)

        # Утилиты базового класса
        self.set_fixed_heights([
            self.first_name, self.last_name, self.position,
            self.passport, self.mobile, self.work,
            self.birth_year, self.experience, self.vacation,
            self.hire_date
        ])
        self.apply_phone_validator([self.mobile, self.work])
        # Валидатор паспорта: 4 цифры, опционально пробел, 6 цифр
        self.apply_regex_validator([self.passport], r'^\d{4}\s?\d{6}$')

        # Сборка формы
        fields = [
            ("Имя:",          self.first_name, 'id-card'),
            ("Фамилия:",      self.last_name,  'id-card'),
            ("Должность:",    self.position,   'briefcase'),
            ("Паспорт:",      self.passport,   'passport'),
            ("Год рождения:", self.birth_year, 'birthday-cake'),
            ("Стаж (лет):",   self.experience, 'history'),
            ("Дата приёма:",  self.hire_date,  'calendar-alt'),
            ("Моб. телефон:", self.mobile,     'mobile-alt'),
            ("Раб. телефон:", self.work,       'phone'),
            ("Отпуск (дн.):", self.vacation,   'umbrella-beach'),
        ]
        for label, widget, icon in fields:
            self.add_form_row(label, widget, icon)

        # Кнопка «Сохранить»
        btn = QPushButton("Сохранить")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.clicked.connect(self._save)
        self.form.addRow(QLabel(), btn)

    def _save(self):
        # Валидация обязательных полей
        if not all([
            self.first_name.text().strip(),
            self.last_name.text().strip(),
            self.position.text().strip()
        ]):
            self.show_warning("Ошибка", "Имя, фамилия и должность обязательны")
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
            self.show_error("Ошибка", f"Не удалось сохранить:\n{e}")
            return

        QMessageBox.information(self, "Успех", "Данные обновлены")
        self.accept()
