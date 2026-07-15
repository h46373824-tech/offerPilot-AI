import os
from collections.abc import Generator

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-16-characters"
os.environ["ADMIN_EMAILS"] = (
    "student@example.com,phase2@example.com,admin@example.com,owner@example.com"
)
import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
