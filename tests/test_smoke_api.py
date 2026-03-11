from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

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
        "track": "track_1",
    }


def test_post_registration_created() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/registrations", json=_participant_payload("created@example.com"))

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "created"
    assert payload["id"]
    assert payload["createdAt"]


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
