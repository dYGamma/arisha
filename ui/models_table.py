# ui/models_table.py

from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant

class EmployeeTableModel(QAbstractTableModel):
    """
    Табличная модель сотрудников с колонками:
    ID, Логин, ФИО, Должность, Дата приёма, Отпуск (дн.).
    """
    headers = ["ID", "Логин", "ФИО", "Должность", "Дата приёма", "Отпуск (дн.)"]

    def __init__(self, employees=None):
        super().__init__()
        self._employees = employees or []

    def rowCount(self, parent=None):
        return len(self._employees)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return QVariant()

        emp = self._employees[index.row()]
        col = index.column()

        if col == 0:
            return emp.id
        elif col == 1:
            return emp.user.username
        elif col == 2:
            # ФИО
            return f"{emp.first_name} {emp.last_name}"
        elif col == 3:
            # Должность
            return emp.position
        elif col == 4:
            # Дата приёма
            return emp.hire_date.strftime("%d.%m.%Y") if emp.hire_date else ""
        elif col == 5:
            return emp.vacation_days_left

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QVariant()

    def update(self, employees):
        """
        Обновляет список сотрудников и перерисовывает таблицу.
        """
        self.beginResetModel()
        self._employees = employees
        self.endResetModel()
