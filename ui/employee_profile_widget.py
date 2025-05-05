# ui/employee_profile_widget.py

import logging
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLabel, QVBoxLayout, QGroupBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from controllers import get_employee_by_user
from ui.utils import icon_label

logger = logging.getLogger(__name__)

class EmployeeProfileWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Моя карточка")
        self.setMinimumSize(360, 400)
        self.setFont(QFont("Segoe UI", 10))

        # Основная вёрстка
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Группа полей
        info_box = QGroupBox("Информация о сотруднике")
        info_box.setFont(QFont("Segoe UI", 11, QFont.Bold))
        info_layout = QFormLayout()
        info_layout.setLabelAlignment(Qt.AlignRight)
        info_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        info_layout.setHorizontalSpacing(20)
        info_layout.setVerticalSpacing(12)
        info_box.setLayout(info_layout)
        main_layout.addWidget(info_box)

        # Загрузка данных
        try:
            with SessionLocal() as db:
                emp = get_employee_by_user(db, user.id)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД при загрузке профиля: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось получить данные из БД.")
            return

        if not emp:
            QMessageBox.warning(self, "Нет данных", "Профиль сотрудника не найден.")
            return

        # Поля для показа
        fields = [
            ("ID",                   emp.id),
            ("Логин",                emp.user.username),
            ("ФИО",                  f"{emp.first_name} {emp.last_name}"),
            ("Паспорт",              emp.passport),
            ("Год рождения",         emp.birth_year),
            ("Стаж (лет)",           emp.experience_years),
            ("Дата приёма",          emp.hire_date.strftime("%d.%m.%Y") if emp.hire_date else ""),
            ("Телефон (моб.)",       emp.phone_mobile),
            ("Телефон (раб.)",       emp.phone_work),
            ("Остаток отпускных",    emp.vacation_days_left),
        ]

        for label_text, value in fields:
            # иконка слева, текст справа
            info_layout.addRow(
                icon_label('id-badge', 20),
                QLabel(f"<b>{label_text}:</b> {value}")
            )
