# ui/utils.py

import qtawesome as qta
from PyQt5.QtWidgets import QLabel, QSystemTrayIcon
from PyQt5.QtGui import QIcon

# Глобальный объект для системных уведомлений
_tray: QSystemTrayIcon = None

def icon_label(name: str, size: int = 20) -> QLabel:
    """
    Возвращает QLabel с пиксмапом иконки FontAwesome 5 Solid.
    """
    ic = qta.icon(f"fa5s.{name}")
    lbl = QLabel()
    lbl.setPixmap(ic.pixmap(size, size))
    lbl.setFixedSize(size + 4, size + 4)
    return lbl

def icon(name: str) -> QIcon:
    """
    Возвращает QIcon FontAwesome 5 Solid.
    """
    return qta.icon(f"fa5s.{name}")

def notify_qt(title: str, message: str):
    """
    Показ системного уведомления через QSystemTrayIcon.
    Инициализировать в main.py: utils._tray = tray.
    """
    global _tray
    if _tray and _tray.isVisible():
        _tray.showMessage(title, message)
