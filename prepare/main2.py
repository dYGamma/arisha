# main.py

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QStackedWidget, QSystemTrayIcon, QStyle, QDesktopWidget
)
from PyQt5.QtCore import QLocale, QSize, QRect
from qt_material import apply_stylesheet

from database import init_db, SessionLocal
from auth import register_user
import ui.utils as utils
from ui.login_widget import LoginWidget
from ui.hr_dashboard_widget import HRDashboardWidget
from ui.employee_profile_widget import EmployeeProfileWidget
# Единый формат даты для всего UI
DATE_FORMAT = "dd.MM.yyyy"
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def center_widget(widget):
    """Центрирует widget на экране."""
    screen = QApplication.primaryScreen().availableGeometry()
    fg = widget.frameGeometry()
    fg.moveCenter(screen.center())
    widget.move(fg.topLeft())

def main():
    configure_logging()
    logging.info("Запуск приложения")
    # Инициализируем БД
    init_db()
    # Seed HR-пользователя
    try:
        with SessionLocal() as db:
            register_user(db, username="da", password="da", role="hr")
    except Exception:
        pass

    app = QApplication(sys.argv)
    # Устанавливаем русскую локаль по-умолчанию (даты, числа и т.п.)
    QLocale.setDefault(QLocale(QLocale.Russian, QLocale.Russia))
    apply_stylesheet(app, theme="light_blue.xml")
    # Системный трей
    tray = QSystemTrayIcon(app.style().standardIcon(QStyle.SP_ComputerIcon))
    tray.show()
    utils._tray = tray
    # Стек виджетов
    stack = QStackedWidget()

    # --- Login page setup ---
    login = LoginWidget(on_success=lambda user: on_login(user))
    stack.addWidget(login)
    stack.setCurrentWidget(login)

    # Фикс под логин и центр
    stack.setFixedSize(login.size())
    stack.show()
    app.processEvents()
    center_widget(stack)

    # Сохраняем начальную геометрию (необязательно)
    initial_geom = stack.geometry()

    def logout():
        logging.info("Выход из аккаунта")
        login.le_user.clear()
        login.le_pwd.clear()
        stack.setCurrentWidget(login)
        # фиксируем снова 320×200 и центрируем
        stack.setFixedSize(login.size())
        stack.showNormal()
        center_widget(stack)

    def on_login(user):
        logging.info(f"Пользователь {user.username} вошёл ({user.role})")
        # снимаем фикс‑размер
        stack.setMinimumSize(0, 0)
        stack.setMaximumSize(QSize(16777215, 16777215))

        # выбираем виджет
        if user.role == "hr":
            w = HRDashboardWidget(user, on_logout=logout)
        else:
            w = EmployeeProfileWidget(user, on_logout=logout)

        stack.addWidget(w)
        stack.setCurrentWidget(w)

        # Устанавливаем ровно 1920×1080 и центрируем
        stack.setFixedSize(1524, 768)
        stack.showNormal()      # чтобы убрать maximized
        center_widget(stack)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
