# ui/register_widget.py

import re
import logging
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDateEdit,
    QPushButton, QMessageBox, QLabel
)
from PyQt5.QtCore import QDate, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QFont
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from database import SessionLocal
from controllers import create_employee
from ui.utils import icon_label, icon

logger = logging.getLogger(__name__)

class RegisterWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация сотрудника")
        self.setFixedSize(600, 870)
        self.setFont(QFont("Segoe UI", 10))

        layout = QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setVerticalSpacing(12)

        # Поля ввода
        self.username   = QLineEdit();  self.username.setPlaceholderText("Логин (латиницей, без пробелов)")
        self.password   = QLineEdit();  self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Пароль, ≥8 символов, буквы и цифры")
        self.first_name = QLineEdit();  self.first_name.setPlaceholderText("Имя сотрудника")
        self.last_name  = QLineEdit();  self.last_name.setPlaceholderText("Фамилия сотрудника")
        self.position   = QLineEdit();  self.position.setPlaceholderText("Должность сотрудника")
        self.passport   = QLineEdit();  self.passport.setPlaceholderText("Серия и номер паспорта, напр. 1234 567890")

        self.birth_year = QSpinBox()
        self.birth_year.setRange(1900, QDate.currentDate().year())
        self.birth_year.setSuffix(" г.")

        self.experience = QSpinBox()
        self.experience.setRange(0, 60)
        self.experience.setSuffix(" лет")

        self.hire_date = QDateEdit(calendarPopup=True)
        self.hire_date.setDate(QDate.currentDate())
        self.hire_date.setDisplayFormat("dd.MM.yyyy")

        self.mobile = QLineEdit(); self.mobile.setPlaceholderText("Введите +7XXXXXXXXXX")
        self.work   = QLineEdit(); self.work.setPlaceholderText("Введите +7XXXXXXXXXX")

        self.vacation = QSpinBox()
        self.vacation.setRange(0, 365)
        self.vacation.setSuffix(" дней")

        # Фиксированная высота
        for w in (
            self.username, self.password, self.first_name,
            self.last_name, self.position, self.passport,
            self.mobile, self.work
        ):
            w.setFixedHeight(32)
        for w in (self.birth_year, self.experience, self.vacation):
            w.setFixedHeight(32)
        self.hire_date.setFixedHeight(32)

        # Телефонный валидатор
        rx = QRegExp(r"^\+?\d{5,15}$")
        ph_validator = QRegExpValidator(rx, self)
        self.mobile.setValidator(ph_validator)
        self.work.setValidator(ph_validator)

        # Сборка формы
        layout.addRow(icon_label('user', 20),      QLabel("Логин:"))
        layout.addRow(self.username)
        layout.addRow(icon_label('lock', 20),      QLabel("Пароль:"))
        layout.addRow(self.password)
        layout.addRow(icon_label('id-card', 20),   QLabel("Имя:"))
        layout.addRow(self.first_name)
        layout.addRow(icon_label('id-card', 20),   QLabel("Фамилия:"))
        layout.addRow(self.last_name)
        layout.addRow(icon_label('briefcase', 20), QLabel("Должность:"))
        layout.addRow(self.position)
        layout.addRow(icon_label('passport', 20),  QLabel("Паспорт:"))
        layout.addRow(self.passport)
        layout.addRow(icon_label('birthday-cake', 20), QLabel("Год рождения:"))
        layout.addRow(self.birth_year)
        layout.addRow(icon_label('history', 20),   QLabel("Стаж работы:"))
        layout.addRow(self.experience)
        layout.addRow(icon_label('calendar-alt', 20), QLabel("Дата приёма:"))
        layout.addRow(self.hire_date)
        layout.addRow(icon_label('mobile-alt', 20),  QLabel("Моб. телефон:"))
        layout.addRow(self.mobile)
        layout.addRow(icon_label('phone', 20),       QLabel("Раб. телефон:"))
        layout.addRow(self.work)
        layout.addRow(icon_label('umbrella-beach', 20), QLabel("Отпуск осталось:"))
        layout.addRow(self.vacation)

        btn = QPushButton(icon('check'), "Создать")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.clicked.connect(self._on_submit)
        layout.addRow(QLabel(), btn)

    def _on_submit(self):
        if not self._validate():
            return

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

        try:
            with SessionLocal() as db:
                create_employee(
                    db,
                    username=self.username.text().strip(),
                    password=self.password.text(),
                    **data
                )
        except IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует.")
            return
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        QMessageBox.information(self, "Успех", "Сотрудник успешно создан.")
        self.accept()

    def _validate(self) -> bool:
        required = [
            (self.username,  "Логин"),
            (self.password,  "Пароль"),
            (self.first_name, "Имя"),
            (self.last_name,  "Фамилия"),
            (self.position,   "Должность"),
            (self.passport,   "Паспорт")
        ]
        for field, name in required:
            if not field.text().strip():
                QMessageBox.warning(self, "Ошибка", f"Пожалуйста, введите {name}.")
                return False

        pwd = self.password.text()
        if len(pwd) < 8 or not re.search(r"\d", pwd) or not re.search(r"[A-Za-z]", pwd):
            QMessageBox.warning(
                self, "Ошибка",
                "Пароль должен быть не менее 8 символов и содержать буквы и цифры."
            )
            return False

        return True
