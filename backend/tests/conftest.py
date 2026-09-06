import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///./test_learnverse.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient

from database import Base, engine
from main import app


@pytest.fixture(scope="session", autouse=True)
def database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(database):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user_data():
    return {
        "name": "Test Learner",
        "email": "learner@example.com",
        "password": "password123",
        "role": "learner",
    }


@pytest.fixture
def test_instructor_data():
    return {
        "name": "Test Instructor",
        "email": "instructor@example.com",
        "password": "password123",
        "role": "instructor",
    }