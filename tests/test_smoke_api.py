from collections.abc import Generator
import os
import re

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("db_user", "test_user")
os.environ.setdefault("db_pass", "test_pass")
os.environ.setdefault("db_name", "test_db")
os.environ.setdefault("db_host", "localhost")
os.environ.setdefault("db_port", "5432")

from app.db.base import Base
from app.db.session import get_db
from app.main import app


SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db


def teardown_module() -> None:
    app.dependency_overrides.clear()


def _participant_payload(email: str = "user@example.com") -> dict[str, object]:
    return {
        "fullName": "Ivan Petrov",
        "status": "participant",
        "transport": "Общественный транспорт",
        "carNumber": None,
        "passport": "4010123456",
        "adult18": "Да",
        "region": "Moscow",
        "participantStatus": "Высшее образование",
        "email": email,
        "track": "finance",
    }


def test_post_registration_created() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/registrations", json=_participant_payload("created@example.com"))

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "created"
    assert payload["id"]
    assert payload["numericKey"]
    assert re.fullmatch(r"\d{6}", payload["numericKey"])
    assert payload["createdAt"]


def test_post_registration_numeric_key_collision_retry(monkeypatch) -> None:
    client = TestClient(app)
    generated_keys = iter(["000111", "000111", "000222"])

    monkeypatch.setattr(
        "app.api.v1.registrations.generate_numeric_key",
        lambda: next(generated_keys),
    )

    first_response = client.post("/api/v1/registrations", json=_participant_payload("retry-a@example.com"))
    assert first_response.status_code == 201
    assert first_response.json()["numericKey"] == "000111"

    second_response = client.post("/api/v1/registrations", json=_participant_payload("retry-b@example.com"))
    assert second_response.status_code == 201
    assert second_response.json()["numericKey"] == "000222"


def test_post_registration_duplicate() -> None:
    client = TestClient(app)
    payload = _participant_payload("dup@example.com")
    client.post("/api/v1/registrations", json=payload)
    response = client.post("/api/v1/registrations", json=payload)

    assert response.status_code == 409
    payload = response.json()
    assert payload["status"] == "duplicate"
    assert payload["errors"]


def test_post_registration_validation_error() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/registrations",
        json={"status": "guest"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["status"] == "validation_error"
    assert isinstance(payload["errors"], list)
