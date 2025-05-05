# auth.py

import bcrypt
import logging
from sqlalchemy.orm import Session
from models import User

logger = logging.getLogger(__name__)

def hash_password(plain: str) -> str:
    """
    Хэширует пароль с помощью bcrypt и возвращает строку.
    """
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """
    Проверяет, соответствует ли plain-пароль сохранённому хэшу.
    """
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError as e:
        logger.error(f"Ошибка проверки пароля: {e}")
        return False

def authenticate(db: Session, username: str, password: str):
    """
    Аутентификация пользователя:
    - ищет User по username,
    - проверяет пароль,
    - возвращает объект User или None.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        logger.info(f"Аутентификация успешна: {username}")
        return user
    logger.warning(f"Аутентификация не удалась: {username}")
    return None

def register_user(db: Session, username: str, password: str, role: str = "employee"):
    """
    Регистрирует нового пользователя с указанной ролью.
    Возвращает созданный объект User.
    """
    hashed = hash_password(password)
    user = User(username=username, password=hashed, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Зарегистрирован пользователь: {username} ({role})")
    return user
