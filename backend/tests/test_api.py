import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.db.init_db import get_session
from app.models.test_suite import TestSuite


# Create a test database
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# Create a test client
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_test_suite(client: TestClient):
    response = client.post(
        "/api/test-suites/",
        json={
            "id": "UI",
            "name": "UI Test Suite",
            "format": "json",
            "version": 1,
            "version_string": "1.0",
            "is_final": False
        },
    )
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == "UI"
    assert data["name"] == "UI Test Suite"
    assert data["format"] == "json"
    assert data["version"] == 1
    assert data["version_string"] == "1.0"
    assert data["is_final"] is False


def test_read_test_suites(client: TestClient, session: Session):
    # Create test data
    test_suite_1 = TestSuite(
        id="UI",
        name="UI Test Suite",
        format="json",
        version=1,
        version_string="1.0",
        is_final=False
    )
    test_suite_2 = TestSuite(
        id="AV",
        name="Audio/Video Test Suite",
        format="json",
        version=1,
        version_string="1.0",
        is_final=False
    )
    session.add(test_suite_1)
    session.add(test_suite_2)
    session.commit()

    response = client.get("/api/test-suites/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["id"] == "UI"
    assert data[1]["id"] == "AV"


def test_read_test_suite(client: TestClient, session: Session):
    # Create test data
    test_suite = TestSuite(
        id="UI",
        name="UI Test Suite",
        format="json",
        version=1,
        version_string="1.0",
        is_final=False
    )
    session.add(test_suite)
    session.commit()

    response = client.get("/api/test-suites/UI")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == "UI"
    assert data["name"] == "UI Test Suite"


def test_update_test_suite(client: TestClient, session: Session):
    # Create test data
    test_suite = TestSuite(
        id="UI",
        name="UI Test Suite",
        format="json",
        version=1,
        version_string="1.0",
        is_final=False
    )
    session.add(test_suite)
    session.commit()

    response = client.patch(
        "/api/test-suites/UI",
        json={"name": "Updated UI Test Suite", "is_final": True},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == "UI"
    assert data["name"] == "Updated UI Test Suite"
    assert data["is_final"] is True


def test_delete_test_suite(client: TestClient, session: Session):
    # Create test data
    test_suite = TestSuite(
        id="UI",
        name="UI Test Suite",
        format="json",
        version=1,
        version_string="1.0",
        is_final=False
    )
    session.add(test_suite)
    session.commit()

    response = client.delete("/api/test-suites/UI")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get("/api/test-suites/UI")
    assert response.status_code == 404
