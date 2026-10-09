import sys
import types
from types import SimpleNamespace
from uuid import uuid4

import pytest

from database import SessionLocal
from models import Course, Enrollment, Payment, User
from routes import auth as auth_routes
from routes import enrollment as enrollment_routes
from services import ai_service, email_service


def unique_user(role="learner"):
    return {
        "name": "Integration User",
        "email": f"{uuid4().hex}@example.com",
        "password": "password123",
        "role": role,
    }


def token_for(client, user):
    assert client.post("/auth/signup", json=user).status_code == 200
    response = client.post("/auth/login", json={"email": user["email"], "password": user["password"]})
    return response.json()["access_token"]


def test_ai_requires_authentication(client):
    response = client.post("/api/ai/chat", json={"message": "Explain recursion"})
    assert response.status_code == 401


def test_ai_rejects_empty_message(client):
    token = token_for(client, unique_user())
    response = client.post(
        "/api/ai/chat",
        json={"message": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_ai_successful_mocked_response(client, monkeypatch):
    token = token_for(client, unique_user())
    captured = {}

    def fake_generate(message, context):
        captured.update(message=message, context=context)
        return "Recursion is a function solving a smaller version of the same problem."

    monkeypatch.setattr("routes.ai.generate_learning_response", fake_generate)
    response = client.post(
        "/api/ai/chat",
        json={"message": "Explain recursion", "course_id": 1, "lesson_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["response"].startswith("Recursion")
    assert captured["message"] == "Explain recursion"


def test_ai_provider_failure_returns_clean_error(client, monkeypatch):
    token = token_for(client, unique_user())

    def fail_generate(message, context):
        raise ai_service.AIServiceError("AI service is unavailable")

    monkeypatch.setattr("routes.ai.generate_learning_response", fail_generate)
    response = client.post(
        "/api/ai/chat",
        json={"message": "Explain this"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "AI service is unavailable"


def test_ai_missing_key_is_handled(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ai_service.AIServiceError, match="not configured"):
        ai_service.generate_learning_response("Explain this")


def test_gemini_sdk_response_is_parsed(monkeypatch):
    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: SimpleNamespace(text="Mocked Gemini answer")
        )
    )
    fake_google = types.ModuleType("google")
    fake_google.genai = SimpleNamespace(Client=lambda api_key: fake_client)
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    assert ai_service.generate_learning_response("Explain this") == "Mocked Gemini answer"


def test_resend_success_is_mocked(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

    monkeypatch.setenv("RESEND_API_KEY", "test-key")
    monkeypatch.setenv("RESEND_FROM_EMAIL", "LearnVerse <noreply@example.com>")
    called = {}

    def fake_post(url, **kwargs):
        called.update(url=url, kwargs=kwargs)
        return Response()

    monkeypatch.setattr(email_service.requests, "post", fake_post)
    assert email_service.send_welcome_email("Learner", "learner@example.com") is True
    assert called["url"] == email_service.RESEND_URL


def test_resend_failure_is_safe(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "test-key")
    monkeypatch.setenv("RESEND_FROM_EMAIL", "noreply@example.com")

    def fail_post(*args, **kwargs):
        raise email_service.requests.RequestException("down")

    monkeypatch.setattr(email_service.requests, "post", fail_post)
    assert email_service.send_welcome_email("Learner", "learner@example.com") is False


def test_signup_succeeds_when_welcome_email_fails(client, monkeypatch):
    monkeypatch.setattr(auth_routes, "send_welcome_email", lambda *args: False)
    response = client.post("/auth/signup", json=unique_user())
    assert response.status_code == 200


def test_enrollment_succeeds_when_confirmation_email_fails(client, monkeypatch):
    user = unique_user()
    token = token_for(client, user)
    db = SessionLocal()
    try:
        course = Course(
            title="Integration Course",
            description="Course for integration testing",
            domain="Programming",
            level="Beginner",
            price=0,
            instructor="Integration Instructor",
            status="approved",
        )
        db.add(course)
        db.commit()
        db.refresh(course)
        monkeypatch.setattr(enrollment_routes, "send_enrollment_confirmation", lambda *args: False)
        response = client.post(
            f"/api/enroll/{course.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
    finally:
        db.close()


def test_paid_enrollment_requires_demo_checkout(client):
    user = unique_user()
    token = token_for(client, user)
    db = SessionLocal()
    try:
        course = Course(
            title="Paid Integration Course",
            description="Course for paid enrollment integration testing",
            domain="Programming",
            level="Beginner",
            price=25,
            instructor="Integration Instructor",
            status="approved",
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(f"/api/enroll/{course.id}", headers=headers)
        assert response.status_code == 400
        assert db.query(Enrollment).filter_by(course_id=course.id).count() == 0
        assert db.query(Payment).filter_by(course_id=course.id).count() == 0

        response = client.post(
            f"/api/enroll/{course.id}?payment_method=demo",
            headers=headers,
        )
        assert response.status_code == 200
        assert db.query(Enrollment).filter_by(course_id=course.id).count() == 1
        assert db.query(Payment).filter_by(course_id=course.id).count() == 1
    finally:
        db.close()


def test_recommendations_prioritize_enrolled_domains_and_exclude_enrolled_courses(client):
    user_data = unique_user()
    token = token_for(client, user_data)
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=user_data["email"]).one()
        enrolled_courses = [
            Course(
                title=f"Enrolled Programming Course {uuid4().hex}",
                description="Programming course",
                domain="Programming",
                level="Beginner",
                price=0,
                instructor="Integration Instructor",
                status="approved",
            )
            for _ in range(2)
        ]
        enrolled_courses.append(
            Course(
                title=f"Enrolled AI Course {uuid4().hex}",
                description="AI course",
                domain="AI & ML",
                level="Beginner",
                price=0,
                instructor="Integration Instructor",
                status="approved",
            )
        )
        candidate_courses = [
            Course(
                title=f"Programming Recommendation {uuid4().hex}",
                description="Recommended programming course",
                domain="Programming",
                level="Beginner",
                price=0,
                instructor="Integration Instructor",
                students=1,
                status="approved",
            ),
            Course(
                title=f"AI Recommendation {uuid4().hex}",
                description="Popular AI course",
                domain="AI & ML",
                level="Beginner",
                price=0,
                instructor="Integration Instructor",
                students=100,
                status="approved",
            ),
            Course(
                title=f"Enrolled Domain Recommendation {uuid4().hex}",
                description="Already enrolled programming course",
                domain="Programming",
                level="Beginner",
                price=0,
                instructor="Integration Instructor",
                students=1000,
                status="approved",
            ),
        ]
        db.add_all(enrolled_courses + candidate_courses)
        db.commit()
        for course in enrolled_courses:
            db.add(Enrollment(user_id=user.id, course_id=course.id))
        db.add(Enrollment(user_id=user.id, course_id=candidate_courses[2].id))
        db.commit()

        response = client.get(
            "/api/recommendations/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        recommendations = response.json()
        recommendation_ids = [item["id"] for item in recommendations]
        assert recommendation_ids.index(candidate_courses[0].id) < recommendation_ids.index(
            candidate_courses[1].id
        )
        assert candidate_courses[2].id not in {item["id"] for item in recommendations}
        programming_recommendation = next(
            item for item in recommendations if item["id"] == candidate_courses[0].id
        )
        assert programming_recommendation["reason"] == "Based on your interest in Programming"
    finally:
        db.close()
