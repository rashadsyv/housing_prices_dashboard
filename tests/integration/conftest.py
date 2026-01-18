"""
Integration test fixtures.

Provides database, FastAPI client, authentication, and sample data fixtures.
These fixtures require the full application stack.
"""

import os
import sys
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.core.database import Base, get_db  # noqa: E402
from src.core.rate_limiter import limiter  # noqa: E402
from src.main import app  # noqa: E402

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test for isolation."""
    limiter.reset()
    yield


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test with automatic cleanup."""
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def api_key(client: TestClient) -> str:
    """Create an API key and return the plain key."""
    response = client.post(
        "/auth/keys",
        json={"name": "Test API Key", "description": "Key for testing"},
    )
    assert response.status_code == 201, f"Failed to create API key: {response.json()}"
    return response.json()["key"]


@pytest.fixture
def auth_headers(client: TestClient, api_key: str) -> dict[str, str]:
    """Get authentication headers with a valid JWT token."""
    response = client.post("/auth/token", json={"api_key": api_key})
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_house_features() -> dict:
    """Sample house features - Input 1 from README. Expected: 320201.58554044"""
    return {
        "longitude": -122.64,
        "latitude": 38.01,
        "housing_median_age": 36.0,
        "total_rooms": 1336.0,
        "total_bedrooms": 258.0,
        "population": 678.0,
        "households": 249.0,
        "median_income": 5.5789,
        "ocean_proximity": "NEAR OCEAN",
    }


@pytest.fixture
def sample_house_features_2() -> dict:
    """Sample house features - Input 2 from README. Expected: 58815.45033765"""
    return {
        "longitude": -115.73,
        "latitude": 33.35,
        "housing_median_age": 23.0,
        "total_rooms": 1586.0,
        "total_bedrooms": 448.0,
        "population": 338.0,
        "households": 182.0,
        "median_income": 1.2132,
        "ocean_proximity": "INLAND",
    }


@pytest.fixture
def sample_house_features_3() -> dict:
    """Sample house features - Input 3 from README. Expected: 192575.77355635"""
    return {
        "longitude": -117.96,
        "latitude": 33.89,
        "housing_median_age": 24.0,
        "total_rooms": 1332.0,
        "total_bedrooms": 252.0,
        "population": 625.0,
        "households": 230.0,
        "median_income": 4.4375,
        "ocean_proximity": "<1H OCEAN",
    }
