"""
Unit tests for LearnVerse FastAPI — auth, courses, enrollment, health.
Tests the service/route layer against an in-memory SQLite database.
"""

import pytest
from fastapi.testclient import TestClient


# ==================== HEALTH ====================

def test_health_check(client: TestClient):
    """GET /health should return 200 with status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_api_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "LearnVerse API"}


def test_api_root(client: TestClient):
    """GET /api should return API info."""
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ==================== AUTH ====================

def test_signup_success(client: TestClient, test_user_data):
    """POST /auth/signup should create a new user."""
    response = client.post("/auth/signup", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "user_id" in data


def test_signup_duplicate_email(client: TestClient, test_user_data):
    """POST /auth/signup with existing email should return 400."""
    # First signup
    client.post("/auth/signup", json=test_user_data)
    # Duplicate
    response = client.post("/auth/signup", json=test_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client: TestClient, test_user_data):
    """POST /auth/login with valid credentials should return a JWT token."""
    client.post("/auth/signup", json=test_user_data)
    response = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_role"] == "learner"


def test_login_invalid_credentials(client: TestClient):
    """POST /auth/login with wrong password should return 401."""
    response = client.post(
        "/auth/login",
        json={"email": "nobody@learnverse.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


# ==================== COURSES ====================

def _get_token(client: TestClient, user_data: dict) -> str:
    """Helper: register and log in, return JWT token."""
    client.post("/auth/signup", json=user_data)
    login_resp = client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    return login_resp.json()["access_token"]


def test_get_courses_public(client: TestClient):
    """GET /api/courses/ should be accessible without auth."""
    response = client.get("/api/courses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_courses(client: TestClient):
    """GET /api/courses/search should accept q param."""
    response = client.get("/api/courses/search?q=python")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_courses_no_query(client: TestClient):
    """GET /api/courses/search without q should return all courses."""
    response = client.get("/api/courses/search")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_recommend_courses_requires_authentication(client: TestClient):
    """Recommendations use the authenticated learner's enrollment history."""
    response = client.get("/api/courses/recommend")
    assert response.status_code == 401


def test_get_course_not_found(client: TestClient):
    """GET /api/courses/99999 should return 404."""
    response = client.get("/api/courses/99999")
    assert response.status_code == 404


# ==================== INSTRUCTOR — COURSE CRUD ====================

def test_instructor_create_course(client: TestClient, test_instructor_data):
    """POST /api/instructor/courses should create a course for an instructor."""
    token = _get_token(client, test_instructor_data)
    course_payload = {
        "title": "Pytest Basics",
        "description": "Learn testing with pytest",
        "domain": "technology",
        "level": "beginner",
        "price": 0.0,
        "instructor": test_instructor_data["name"],
    }
    response = client.post(
        "/api/instructor/courses",
        json=course_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "course_id" in data


def test_learner_cannot_create_course(client: TestClient, test_user_data):
    """Learners should get 403 when trying to create a course."""
    token = _get_token(client, test_user_data)
    response = client.post(
        "/api/instructor/courses",
        json={
            "title": "Hack Course",
            "description": "Should fail",
            "domain": "technology",
            "level": "beginner",
            "price": 0.0,
            "instructor": "hacker",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ==================== ENROLLMENT ====================

def test_enroll_requires_auth(client: TestClient):
    """POST /api/enroll/1 without token should return 401."""
    response = client.post("/api/enroll/1")
    assert response.status_code == 401


def test_get_enrollments_requires_auth(client: TestClient):
    """GET /api/enroll/ without token should return 401."""
    response = client.get("/api/enroll/")
    assert response.status_code == 401