# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL для SQLite (файл hr.db находится в корне проекта)
SQLALCHEMY_DATABASE_URL = "sqlite:///hr.db"

# Создаём движок с отключённым check_same_thread, чтобы можно было работать из разных потоков
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для всех моделей
Base = declarative_base()

def init_db():
    """
    Инициализирует базу данных — создаёт все таблицы, описанные в моделях.
    Вызывать при запуске приложения (например, в main.py).
    """
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
