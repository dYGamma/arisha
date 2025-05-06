# services/employee_service.py

from typing import List, Optional
from sqlalchemy.orm import Session

from controllers import (
    list_employees as ctrl_list,
    get_employee as ctrl_get,
    create_employee as ctrl_create,
    update_employee as ctrl_update,
    delete_employee as ctrl_delete,
)
from models import Employee

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, search: str = "") -> List[Employee]:
        """Вернуть список сотрудников с учётом фильтра."""
        return ctrl_list(self.db, search)

    def get(self, emp_id: int) -> Optional[Employee]:
        """Вернуть одного сотрудника."""
        return ctrl_get(self.db, emp_id)

    def create(self, username: str, password: str, **data) -> Employee:
        """Создать сотрудника."""
        return ctrl_create(self.db, username, password, **data)

    def update(self, emp_id: int, **data) -> None:
        """Обновить сотрудника."""
        ctrl_update(self.db, emp_id, **data)

    def delete(self, emp_id: int) -> None:
        """Удалить сотрудника."""
        ctrl_delete(self.db, emp_id)
