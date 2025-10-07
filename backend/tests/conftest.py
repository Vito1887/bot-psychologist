import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Установим тестовые переменные окружения ДО импорта приложения
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.local")
os.environ.setdefault("ADMIN_PASSWORD", "adminpass")

from app.main import app  # noqa: E402
from app.database import Base  # noqa: E402
from app import database as db_mod  # noqa: E402

# Создаём тестовый движок и сессии
engine = create_engine(
    os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Подменим движок и фабрику сессий в модуле database
db_mod.engine = engine
db_mod.SessionLocal = TestingSessionLocal

# Создадим таблицы
Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client():
    # Переопределяем зависимость get_db
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[db_mod.get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
