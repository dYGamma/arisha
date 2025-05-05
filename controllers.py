# controllers.py

import logging
from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func

from models import Employee, User
from auth import register_user, authenticate
from ui.utils import notify_qt

logger = logging.getLogger(__name__)

def create_employee(db: Session, username: str, password: str, **data) -> Employee:
    """
    Создаёт нового пользователя (роль employee) и соответствующую запись Employee.
    """
    try:
        user = register_user(db, username=username, password=password, role="employee")
        emp = Employee(user_id=user.id, **data)
        db.add(emp)
        db.commit()
        db.refresh(emp)
        logger.info(f"Создан сотрудник: {emp.id} — {emp.first_name} {emp.last_name}")
        notify_qt("HR", f"Создан сотрудник {emp.first_name} {emp.last_name}")
        return emp
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Ошибка при создании сотрудника: {e}")
        raise

def get_employee(db: Session, emp_id: int) -> Optional[Employee]:
    """
    Возвращает сотрудника по его ID, с предзагрузкой User.
    """
    return (
        db.query(Employee)
        .options(selectinload(Employee.user))
        .filter(Employee.id == emp_id)
        .first()
    )

def get_employee_by_user(db: Session, user_id: int) -> Optional[Employee]:
    """
    Возвращает сотрудника, связанного с данным User ID, с предзагрузкой User.
    """
    return (
        db.query(Employee)
        .options(selectinload(Employee.user))
        .filter(Employee.user_id == user_id)
        .first()
    )

def list_employees(db: Session, search: str = "") -> List[Employee]:
    """
    Возвращает список сотрудников с предзагрузкой User.
    Если search — число, фильтрует по точному ID;
    иначе — по логину, имени или фамилии (ilike).
    """
    query = db.query(Employee).options(selectinload(Employee.user))

    if search:
        if search.isdigit():
            query = query.filter(Employee.id == int(search))
        else:
            pattern = f"%{search}%"
            query = (
                query.join(User)
                     .filter(
                         or_(
                             func.lower(User.username).like(func.lower(pattern)),
                             func.lower(Employee.first_name).like(func.lower(pattern)),
                             func.lower(Employee.last_name).like(func.lower(pattern)),
                         )
                     )
            )

    emps = query.order_by(Employee.id).all()
    logger.info(f"Найдено сотрудников: {len(emps)} (search='{search}')")
    return emps

def update_employee(db: Session, emp_id: int, **data) -> None:
    """
    Обновляет данные сотрудника по emp_id.
    """
    emp = get_employee(db, emp_id)
    if not emp:
        raise ValueError(f"Employee with id={emp_id} not found")
    for k, v in data.items():
        setattr(emp, k, v)
    try:
        db.commit()
        logger.info(f"Обновлён сотрудник: {emp.id}")
        notify_qt("HR", f"Обновлён сотрудник {emp.first_name} {emp.last_name}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении сотрудника: {e}")
        raise

def delete_employee(db: Session, emp_id: int) -> None:
    """
    Удаляет пользователя и связанные с ним данные Employee.
    """
    emp = get_employee(db, emp_id)
    if not emp:
        raise ValueError(f"Employee with id={emp_id} not found")
    name = f"{emp.first_name} {emp.last_name}"
    try:
        # удаляем User, каскад удалит Employee
        db.delete(emp.user)
        db.commit()
        logger.info(f"Удалён сотрудник: {emp.id}")
        notify_qt("HR", f"Удалён сотрудник {name}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Ошибка при удалении сотрудника: {e}")
        raise
