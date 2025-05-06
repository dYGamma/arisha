# ui/register_widget.py

import re
import logging
from PyQt5.QtWidgets import (
    QLineEdit, QSpinBox, QDateEdit, QPushButton, QMessageBox, QLabel
)
from PyQt5.QtCore import QDate, Qt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from database import SessionLocal
from controllers import create_employee
from ui.form_base import EmployeeFormDialog
from main import DATE_FORMAT

logger = logging.getLogger(__name__)

class RegisterWidget(EmployeeFormDialog):
    def __init__(self, parent=None):
        super().__init__("Регистрация сотрудника", parent)
        self.setFixedSize(600, 870)

        # Поля ввода
        self.username   = QLineEdit()
        self.username.setPlaceholderText("Логин (латиницей, без пробелов)")

        self.password   = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Пароль, ≥8 символов, буквы и цифры")

        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Имя сотрудника")

        self.last_name  = QLineEdit()
        self.last_name.setPlaceholderText("Фамилия сотрудника")

        self.position   = QLineEdit()
        self.position.setPlaceholderText("Должность сотрудника")

        self.passport   = QLineEdit()
        self.passport.setPlaceholderText("Серия и номер паспорта, напр. 1234 567890")

        self.birth_year = QSpinBox()
        self.birth_year.setRange(1900, QDate.currentDate().year())
        self.birth_year.setSuffix(" г.")

        self.experience = QSpinBox()
        self.experience.setRange(0, 60)
        self.experience.setSuffix(" лет")

        self.hire_date  = QDateEdit(calendarPopup=True)
        self.hire_date.setDate(QDate.currentDate())
        self.hire_date.setDisplayFormat(DATE_FORMAT)

        self.mobile     = QLineEdit()
        self.mobile.setPlaceholderText("Введите +7XXXXXXXXXX")

        self.work       = QLineEdit()
        self.work.setPlaceholderText("Введите +7XXXXXXXXXX")

        self.vacation   = QSpinBox()
        self.vacation.setRange(0, 365)
        self.vacation.setSuffix(" дней")

        # Применяем утилиты базового класса
        self.set_fixed_heights([
            self.username, self.password, self.first_name, self.last_name,
            self.position, self.passport, self.mobile, self.work,
            self.birth_year, self.experience, self.vacation, self.hire_date
        ])
        self.apply_phone_validator([self.mobile, self.work])
        # Валидатор паспорта: 4 цифры, опционально пробел, 6 цифр
        self.apply_regex_validator([self.passport], r'^\d{4}\s?\d{6}$')

        # Сборка формы
        self.add_form_row("Логин:",           self.username,   'user')
        self.add_form_row("Пароль:",          self.password,   'lock')
        self.add_form_row("Имя:",             self.first_name, 'id-card')
        self.add_form_row("Фамилия:",         self.last_name,  'id-card')
        self.add_form_row("Должность:",       self.position,   'briefcase')
        self.add_form_row("Паспорт:",         self.passport,   'passport')
        self.add_form_row("Год рождения:",    self.birth_year, 'birthday-cake')
        self.add_form_row("Стаж работы:",     self.experience, 'history')
        self.add_form_row("Дата приёма:",     self.hire_date,  'calendar-alt')
        self.add_form_row("Моб. телефон:",    self.mobile,     'mobile-alt')
        self.add_form_row("Раб. телефон:",    self.work,       'phone')
        self.add_form_row("Отпуск осталось:", self.vacation,   'umbrella-beach')

        # Кнопка создания
        btn = QPushButton("Создать")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.clicked.connect(self._on_submit)
        self.form.addRow(QLabel(), btn)

    def _on_submit(self):
        # Проверка обязательных полей
        for field, name in [
            (self.username, "Логин"),
            (self.password, "Пароль"),
            (self.first_name, "Имя"),
            (self.last_name, "Фамилия"),
            (self.position, "Должность"),
            (self.passport, "Паспорт")
        ]:
            if not field.text().strip():
                self.show_warning("Ошибка", f"Пожалуйста, введите {name}.")
                return

        # Проверка пароля
        pwd = self.password.text()
        if len(pwd) < 8 or not re.search(r"\d", pwd) or not re.search(r"[A-Za-z]", pwd):
            self.show_warning(
                "Ошибка",
                "Пароль должен быть не менее 8 символов и содержать буквы и цифры."
            )
            return

        # Сбор данных
        data = dict(
            first_name=self.first_name.text().strip(),
            last_name=self.last_name.text().strip(),
            position=self.position.text().strip(),
            passport=self.passport.text().strip(),
            birth_year=self.birth_year.value(),
            experience_years=self.experience.value(),
            hire_date=self.hire_date.date().toPyDate(),
            phone_mobile=self.mobile.text().strip(),
            phone_work=self.work.text().strip(),
            vacation_days_left=self.vacation.value()
        )

        # Создание в БД
        try:
            with SessionLocal() as db:
                create_employee(
                    db,
                    username=self.username.text().strip(),
                    password=self.password.text(),
                    **data
                )
        except IntegrityError:
            self.show_warning("Ошибка", "Пользователь с таким логином уже существует.")
            return
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД при создании сотрудника: {e}")
            self.show_error("Ошибка", str(e))
            return

        QMessageBox.information(self, "Успех", "Сотрудник успешно создан.")
        self.accept()
