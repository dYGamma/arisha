# ui/employee_profile_widget.py

import logging
import os
import shutil
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLabel, QVBoxLayout, QGroupBox,
    QMessageBox, QPushButton, QFileDialog, QHBoxLayout,
    QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal
from controllers import get_employee_by_user
from ui.utils import icon, icon_label

logger = logging.getLogger(__name__)

# Директории для хранения файлов
PROFILE_PHOTOS_DIR = "profile_photos/"
EMPLOYEE_DOCS_DIR  = "employee_docs/"

class EmployeeProfileWidget(QWidget):
    def __init__(self, user, on_logout, show_logout=True):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self.show_logout = show_logout

        self.setWindowTitle("Моя карточка")
        self.setMinimumSize(400, 650)
        self.setFont(QFont("Segoe UI", 10))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Загрузка данных о сотруднике
        try:
            with SessionLocal() as db:
                self.emp = get_employee_by_user(db, user.id)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД при загрузке профиля: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось получить данные из БД.")
            return

        if not self.emp:
            QMessageBox.warning(self, "Нет данных", "Профиль сотрудника не найден.")
            return

        # Фото профиля
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(100, 100)
        self.photo_label.setFrameShape(QLabel.Box)
        self.load_profile_photo()
        btn_upload_photo = QPushButton("Изменить фото")
        btn_upload_photo.clicked.connect(self.change_photo)
        photo_layout.addWidget(self.photo_label)
        photo_layout.addWidget(btn_upload_photo)
        main_layout.addLayout(photo_layout)

        # Информация о сотруднике
        info_box = QGroupBox("Информация о сотруднике")
        info_box.setFont(QFont("Segoe UI", 11, QFont.Bold))
        info_layout = QFormLayout()
        info_layout.setLabelAlignment(Qt.AlignRight)
        info_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        info_layout.setHorizontalSpacing(20)
        info_layout.setVerticalSpacing(12)
        info_box.setLayout(info_layout)
        main_layout.addWidget(info_box)

        date_str = self.emp.hire_date.strftime("%d.%m.%Y") if self.emp.hire_date else ""
        fields = [
            ("ID", self.emp.id),
            ("Логин", self.emp.user.username),
            ("ФИО", f"{self.emp.first_name} {self.emp.last_name}"),
            ("Паспорт", self.emp.passport),
            ("Год рождения", self.emp.birth_year),
            ("Стаж (лет)", self.emp.experience_years),
            ("Дата приёма", date_str),
            ("Телефон (моб.)", self.emp.phone_mobile),
            ("Телефон (раб.)", self.emp.phone_work),
            ("Остаток отпускных", self.emp.vacation_days_left),
        ]
        for label_text, value in fields:
            info_layout.addRow(
                icon_label('id-badge', 20),
                QLabel(f"<b>{label_text}:</b> {value}")
            )

        # Раздел документов
        docs_box = QGroupBox("Документы сотрудника")
        docs_box.setFont(QFont("Segoe UI", 11, QFont.Bold))
        docs_layout = QVBoxLayout()
        docs_box.setLayout(docs_layout)

        self.docs_list = QListWidget()
        self.docs_list.itemDoubleClicked.connect(self.open_document)
        docs_layout.addWidget(self.docs_list)

        btns_layout = QHBoxLayout()
        btn_upload_doc = QPushButton(icon('file-upload'), "Загрузить документ")
        btn_upload_doc.clicked.connect(self.upload_document)
        btn_delete_doc = QPushButton(icon('trash'), "Удалить документ")
        btn_delete_doc.clicked.connect(self.delete_document)
        btns_layout.addWidget(btn_upload_doc)
        btns_layout.addWidget(btn_delete_doc)
        docs_layout.addLayout(btns_layout)

        main_layout.addWidget(docs_box)

        # Кнопка выхода (опционально)
        if self.show_logout:
            btn_logout = QPushButton(icon('sign-out-alt'), "Выход")
            btn_logout.setFixedWidth(140)
            btn_logout.clicked.connect(self.on_logout)
            main_layout.addWidget(btn_logout, alignment=Qt.AlignRight)

        # Загрузка списка документов
        self.load_documents()

    def load_profile_photo(self):
        path = os.path.join(PROFILE_PHOTOS_DIR, f"{self.emp.id}.jpg")
        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.setText("Нет фото")

    def change_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            os.makedirs(PROFILE_PHOTOS_DIR, exist_ok=True)
            dest = os.path.join(PROFILE_PHOTOS_DIR, f"{self.emp.id}.jpg")
            try:
                shutil.copy(file_path, dest)
                self.load_profile_photo()
                QMessageBox.information(self, "Успех", "Фото обновлено.")
            except Exception as e:
                logger.error(f"Ошибка при копировании фото: {e}")
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить фото.")

    def load_documents(self):
        """Сканирует папку и отображает список документов"""
        self.docs_list.clear()
        emp_dir = os.path.join(EMPLOYEE_DOCS_DIR, str(self.emp.id))
        if not os.path.isdir(emp_dir):
            return
        for fname in os.listdir(emp_dir):
            item = QListWidgetItem(QIcon(icon('file')), fname)
            item.setData(Qt.UserRole, os.path.join(emp_dir, fname))
            self.docs_list.addItem(item)

    def upload_document(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите документ", "", "Документы (*.pdf *.docx *.jpg *.png)")
        if file_path:
            emp_dir = os.path.join(EMPLOYEE_DOCS_DIR, str(self.emp.id))
            os.makedirs(emp_dir, exist_ok=True)
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(emp_dir, file_name)
            if os.path.exists(dest_path):
                QMessageBox.warning(self, "Внимание", f"Документ '{file_name}' уже существует.")
                return
            try:
                shutil.copy(file_path, dest_path)
                QMessageBox.information(self, "Успех", f"Документ загружен: {file_name}")
                self.load_documents()
            except Exception as e:
                logger.error(f"Ошибка при загрузке документа: {e}")
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить документ.")

    def delete_document(self):
        item = self.docs_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Удаление", "Выберите документ для удаления.")
            return
        path = item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить документ '{item.text()}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                os.remove(path)
                QMessageBox.information(self, "Успех", "Документ удалён.")
                self.load_documents()
            except Exception as e:
                logger.error(f"Ошибка при удалении документа: {e}")
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить документ.")

    def open_document(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.call(('xdg-open', path))
        except Exception as e:
            logger.error(f"Не удалось открыть документ: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось открыть документ.")
