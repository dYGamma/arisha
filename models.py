# models.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role     = Column(String, nullable=False)  # "employee" или "hr"

    # Один к одному: при удалении пользователя удаляется и профиль сотрудника
    employee = relationship(
        "Employee",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )

class Employee(Base):
    __tablename__ = "employees"

    id                  = Column(Integer, primary_key=True, index=True)
    user_id             = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name          = Column(String, nullable=False)
    last_name           = Column(String, nullable=False)
    position            = Column(String, nullable=False)  # Должность
    passport            = Column(String, nullable=False)
    birth_year          = Column(Integer)
    experience_years    = Column(Integer)
    hire_date           = Column(Date)
    phone_mobile        = Column(String)
    phone_work          = Column(String)
    vacation_days_left  = Column(Integer)

    # Связь с пользователем
    user = relationship("User", back_populates="employee")
