# ui/login_widget.py

import logging
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet
from ui.utils import icon, icon_label

logger = logging.getLogger(__name__)

class LoginWidget(QDialog):
    def __init__(self, on_success, parent=None):
        super().__init__(parent)
        self.on_success = on_success

        # Оформление окна
        self.setWindowTitle("Вход в HR-систему")
        self.setFixedSize(320, 200)
        apply_stylesheet(self, theme="light_blue.xml")
        self.setFont(QFont("Segoe UI", 10))

        # Компоновка формы
        layout = QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setVerticalSpacing(12)

        # Поля ввода
        self.le_user = QLineEdit()
        self.le_user.setPlaceholderText("Логин")
        self.le_pwd = QLineEdit()
        self.le_pwd.setEchoMode(QLineEdit.Password)
        self.le_pwd.setPlaceholderText("Пароль")

        # Добавляем иконки слева
        layout.addRow(icon_label("user", 24), self.le_user)
        layout.addRow(icon_label("lock", 24), self.le_pwd)

        # Кнопка входа
        btn = QPushButton(icon("sign-in-alt"), "Войти")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.setStyleSheet(
            "QPushButton { background: #1976d2; color: white; border-radius: 4px; }"
            "QPushButton:hover { background: #1e88e5; }"
        )
        btn.clicked.connect(self._on_login_clicked)

        # Центрируем кнопку под полями
        layout.addRow(QLabel(), btn)

    def _on_login_clicked(self):
        username = self.le_user.text().strip()
        password = self.le_pwd.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            from database import SessionLocal
            from auth import authenticate
            with SessionLocal() as db:
                user = authenticate(db, username, password)
        except Exception as e:
            logger.error(f"Ошибка при попытке входа: {e}")
            QMessageBox.critical(self, "Ошибка", f"Сбой при подключении к БД:\n{e}")
            return

        if not user:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return

        logger.info(f"Успешный вход: {username}")
        self.accept()
        self.on_success(user)