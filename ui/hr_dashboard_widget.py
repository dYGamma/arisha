# ui/hr_dashboard_widget.py

import logging
import os
import shutil
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QTableView, QFrame, QFileDialog, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from database import SessionLocal
from services.employee_service import EmployeeService
from controllers import get_employee
from reports import export_employees_pdf, export_employees_excel
from ui.utils import icon, icon_label, notify_qt
from ui.models_table import EmployeeTableModel
from ui.employee_profile_widget import (
    EmployeeProfileWidget,
    PROFILE_PHOTOS_DIR,
    EMPLOYEE_DOCS_DIR
)

logger = logging.getLogger(__name__)

class HRDashboardWidget(QWidget):
    def __init__(self, user, on_logout):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self.profile_window = None

        self.setWindowTitle("HR: Панель управления")
        self.setFont(QFont("Segoe UI", 10))
        self.setMinimumSize(900, 600)

        # UI
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Верхняя панель
        top_frame = QFrame()
        top_frame.setFrameShape(QFrame.StyledPanel)
        top_frame.setStyleSheet("background: #fafafa; border-radius: 8px;")
        tf_layout = QHBoxLayout(top_frame)
        tf_layout.setContentsMargins(12, 12, 12, 12)
        tf_layout.setSpacing(12)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по ID, ФИО или логину")
        self.search.setClearButtonEnabled(True)
        self.search.setFixedHeight(32)
        self.search.textChanged.connect(self.refresh)

        tf_layout.addWidget(icon_label('search', 20))
        tf_layout.addWidget(self.search)

        btn_add = QPushButton(icon('user-plus'), "")
        btn_add.setToolTip("Добавить сотрудника")
        btn_add.setFixedSize(32, 32)
        btn_add.clicked.connect(self.add_emp)
        tf_layout.addWidget(btn_add)

        btn_pdf = QPushButton("PDF")
        btn_pdf.setToolTip("Экспорт в PDF")
        btn_pdf.setFixedHeight(28)
        btn_pdf.clicked.connect(lambda: self.export('pdf'))
        tf_layout.addWidget(btn_pdf)

        btn_xlsx = QPushButton("XLSX")
        btn_xlsx.setToolTip("Экспорт в Excel")
        btn_xlsx.setFixedHeight(28)
        btn_xlsx.clicked.connect(lambda: self.export('xlsx'))
        tf_layout.addWidget(btn_xlsx)

        btn_logout = QPushButton(icon('sign-out-alt'), "")
        btn_logout.setToolTip("Сменить аккаунт")
        btn_logout.setFixedSize(32, 32)
        btn_logout.clicked.connect(self.on_logout)
        tf_layout.addWidget(btn_logout)

        main_layout.addWidget(top_frame)

        # Таблица
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.view_emp)

        # Модель и настройки так, чтобы текст не урезался
        self.model = EmployeeTableModel([])
        self.table.setModel(self.model)

        # Включаем перенос строк и отключаем обрезку текста
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.ElideNone)

        # Автоматически подгоняем ширину столбцов под содержимое
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # Стилизация таблицы
        self.table.setStyleSheet("""
            QHeaderView::section {
                background: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
            }
            QTableView {
                gridline-color: #ddd;
                background: #fff;
            }
        """)
        main_layout.addWidget(self.table)

        # Кнопки просмотра/редактирования/удаления
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_view = QPushButton(icon('eye'), "")
        btn_view.setToolTip("Просмотр профиля")
        btn_view.setFixedSize(32, 32)
        btn_view.clicked.connect(self.view_emp)
        btn_layout.addWidget(btn_view)

        btn_edit = QPushButton(icon('edit'), "")
        btn_edit.setToolTip("Редактировать")
        btn_edit.setFixedSize(32, 32)
        btn_edit.clicked.connect(self.edit_emp)
        btn_layout.addWidget(btn_edit)

        btn_del = QPushButton(icon('trash'), "")
        btn_del.setToolTip("Удалить")
        btn_del.setFixedSize(32, 32)
        btn_del.clicked.connect(self.del_emp)
        btn_layout.addWidget(btn_del)

        main_layout.addLayout(btn_layout)

        # Загрузка данных
        self.refresh()

    def refresh(self):
        """Обновить таблицу по текущему фильтру."""
        try:
            with SessionLocal() as db:
                service = EmployeeService(db)
                emps = service.list(self.search.text())
            self.model.update(emps)
            logger.info(f"Loaded {len(emps)} employees (filter='{self.search.text()}')")
        except Exception as e:
            logger.error(f"Error loading employees: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список:\n{e}")

    def get_selected_id(self):
        idx = self.table.currentIndex()
        return None if not idx.isValid() else self.model._employees[idx.row()].id

    def view_emp(self, index=None):
        emp_id = self.get_selected_id()
        if not emp_id:
            return
        try:
            with SessionLocal() as db:
                emp = get_employee(db, emp_id)
            if self.profile_window:
                self.profile_window.close()
            self.profile_window = EmployeeProfileWidget(
                emp.user,
                on_logout=self.on_logout,
                show_logout=False
            )
            self.profile_window.show()
        except Exception as e:
            logger.error(f"Error opening profile: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть профиль:\n{e}")

    def add_emp(self):
        from ui.register_widget import RegisterWidget
        dlg = RegisterWidget(self)
        if dlg.exec_() == dlg.Accepted:
            self.refresh()

    def edit_emp(self):
        emp_id = self.get_selected_id()
        if not emp_id:
            return
        from ui.edit_widget import EditWidget
        dlg = EditWidget(emp_id, self)
        if dlg.exec_() == dlg.Accepted:
            self.refresh()

    def del_emp(self):
        emp_id = self.get_selected_id()
        if not emp_id:
            return
        # Подтверждение удаления
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить сотрудника {emp_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            # Удаляем из БД
            with SessionLocal() as db:
                service = EmployeeService(db)
                service.delete(emp_id)

            # Удаляем аватар
            photo_path = os.path.join(PROFILE_PHOTOS_DIR, f"{emp_id}.jpg")
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except Exception as e:
                    logger.warning(f"Не удалось удалить аватар {photo_path}: {e}")

            # Удаляем папку с документами
            docs_dir = os.path.join(EMPLOYEE_DOCS_DIR, str(emp_id))
            if os.path.isdir(docs_dir):
                try:
                    shutil.rmtree(docs_dir)
                except Exception as e:
                    logger.warning(f"Не удалось удалить папку документов {docs_dir}: {e}")

            notify_qt("HR", f"Сотрудник {emp_id} удалён")
            self.refresh()
        except Exception as e:
            logger.error(f"Error deleting employee: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")

    def export(self, fmt):
        """Экспорт текущего (отфильтрованного) списка."""
        filters = "PDF Files (*.pdf)" if fmt == 'pdf' else "Excel Files (*.xlsx)"
        default_ext = ".pdf" if fmt == 'pdf' else ".xlsx"
        caption = "Сохранить отчёт"
        path, _ = QFileDialog.getSaveFileName(self, caption, "", filters)
        if not path:
            return
        if not path.lower().endswith(default_ext):
            path += default_ext

        try:
            with SessionLocal() as db:
                service = EmployeeService(db)
                emps = service.list(self.search.text())
            if fmt == 'pdf':
                export_employees_pdf(path, emps)
            else:
                export_employees_excel(path, emps)
            notify_qt("HR", f"Отчёт сохранён: {path}")
        except Exception as e:
            logger.error(f"Error exporting ({fmt}): {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{e}")
