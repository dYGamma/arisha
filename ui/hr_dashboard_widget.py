# ui/hr_dashboard_widget.py

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QTableView, QLabel, QFrame, QFileDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from database import SessionLocal
from controllers import list_employees, delete_employee
from reports import export_employees_pdf, export_employees_excel
from ui.utils import icon, icon_label, notify_qt
from ui.models_table import EmployeeTableModel

logger = logging.getLogger(__name__)

class HRDashboardWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("HR: Панель управления")
        self.setFont(QFont("Segoe UI", 10))
        self.setMinimumSize(900, 600)

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Верхняя панель: поиск и экспорт
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

        main_layout.addWidget(top_frame)

        # Таблица сотрудников
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        self.model = EmployeeTableModel([])
        self.table.setModel(self.model)
        self.table.horizontalHeader().setStretchLastSection(True)

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

        # Кнопки редактирования/удаления
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

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

        # Первичная загрузка
        self.refresh()

    def refresh(self):
        try:
            with SessionLocal() as db:
                emps = list_employees(db, self.search.text())
            self.model.update(emps)
            logger.info(f"Loaded {len(emps)} employees")
        except Exception as e:
            logger.error(f"Error loading employees: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список:\n{e}")

    def get_selected_id(self):
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        return self.model._employees[idx.row()].id

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
        try:
            with SessionLocal() as db:
                delete_employee(db, emp_id)
            notify_qt("HR", f"Сотрудник {emp_id} удалён")
            self.refresh()
        except Exception as e:
            logger.error(f"Error deleting employee: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")

    def export(self, fmt):
        # Формируем фильтры расширения и подсказку
        filters = "PDF Files (*.pdf)" if fmt == 'pdf' else "Excel Files (*.xlsx)"
        default_ext = ".pdf" if fmt == 'pdf' else ".xlsx"
        caption = "Сохранить отчёт"

        # Открываем диалог «Сохранить как»
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            caption,
            "",           # стартовая папка (пусто = последний открытый)
            filters
        )
        if not file_path:
            return  # пользователь отменил

        # Добавляем расширение, если забыли
        if not file_path.lower().endswith(default_ext):
            file_path += default_ext

        try:
            with SessionLocal() as db:
                emps = list_employees(db)
            if fmt == 'pdf':
                export_employees_pdf(file_path, emps)
            else:
                export_employees_excel(file_path, emps)
            notify_qt("HR", f"Отчёт сохранён: {file_path}")
        except Exception as e:
            logger.error(f"Error exporting ({fmt}): {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{e}")
