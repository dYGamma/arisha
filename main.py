# main.py

import sys
import logging
from PyQt5.QtWidgets import QApplication, QStackedWidget, QSystemTrayIcon, QStyle
from qt_material import apply_stylesheet

from database import init_db, SessionLocal
from auth import register_user
import ui.utils as utils

from ui.login_widget import LoginWidget
from ui.hr_dashboard_widget import HRDashboardWidget
from ui.employee_profile_widget import EmployeeProfileWidget

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

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
    apply_stylesheet(app, theme="light_blue.xml")

    # Системный трей
    tray = QSystemTrayIcon(app.style().standardIcon(QStyle.SP_ComputerIcon))
    tray.show()
    utils._tray = tray

    # Стек виджетов
    stack = QStackedWidget()
    def on_login(user):
        logging.info(f"Пользователь {user.username} вошёл ({user.role})")
        if user.role == "hr":
            w = HRDashboardWidget(user)
        else:
            w = EmployeeProfileWidget(user)
        stack.addWidget(w)
        stack.setCurrentWidget(w)
        stack.showMaximized()

    login = LoginWidget(on_success=on_login)
    stack.addWidget(login)
    stack.setCurrentWidget(login)
    stack.resize(login.size())
    stack.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
