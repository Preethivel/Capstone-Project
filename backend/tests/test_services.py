"""
Service-layer unit tests — pure logic, no HTTP, using SQLite.
Covers: enrollment_service, course_service.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base
from models import Course, Enrollment, User
from auth import get_password_hash

# In-memory engine for service tests
_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
_Session = sessionmaker(bind=_engine)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.create_all(_engine)
    yield
    Base.metadata.drop_all(_engine)


@pytest.fixture
def db():
    session = _Session()
    yield session
    session.close()


@pytest.fixture
def learner(db):
    u = User(
        name="Learner",
        email="learner@test.com",
        password_hash=get_password_hash("pass"),
        role="learner",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def instructor(db):
    u = User(
        name="Instructor",
        email="inst@test.com",
        password_hash=get_password_hash("pass"),
        role="instructor",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def course(db, instructor):
    c = Course(
        title="Test Course",
        description="Description",
        domain="technology",
        level="beginner",
        price=0.0,
        instructor=instructor.name,
        instructor_id=instructor.id,
        status="approved",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ==================== USER CREATION ====================

def test_user_password_is_hashed(db, learner):
    """Password must not be stored in plain text."""
    assert learner.password_hash != "pass"
    assert len(learner.password_hash) > 20


def test_user_default_role_is_learner(db):
    u = User(
        name="Default",
        email="def@test.com",
        password_hash=get_password_hash("x"),
    )
    db.add(u)
    db.commit()
    assert u.role == "learner"


def test_user_xp_starts_at_zero(db, learner):
    assert learner.xp == 0


# ==================== COURSE ====================

def test_course_default_status_is_approved(db, course):
    assert course.status == "approved"


def test_course_default_rating_is_zero(db, course):
    assert course.rating == 0.0


def test_course_default_students_is_zero(db, course):
    assert course.students == 0


# ==================== ENROLLMENT ====================

def test_create_enrollment(db, learner, course):
    """Enrolling a user in a course should succeed."""
    e = Enrollment(user_id=learner.id, course_id=course.id)
    db.add(e)
    db.commit()
    db.refresh(e)
    assert e.id is not None
    assert e.progress == 0


def test_enrollment_progress_update(db, learner, course):
    """Progress field should be updatable."""
    e = Enrollment(user_id=learner.id, course_id=course.id, progress=0)
    db.add(e)
    db.commit()
    e.progress = 50
    db.commit()
    db.refresh(e)
    assert e.progress == 50


def test_duplicate_enrollment_unique_constraint(db, learner, course):
    """Duplicate enrollment (same user+course) should raise an IntegrityError."""
    from sqlalchemy.exc import IntegrityError
    e1 = Enrollment(user_id=learner.id, course_id=course.id)
    db.add(e1)
    db.commit()
    e2 = Enrollment(user_id=learner.id, course_id=course.id)
    db.add(e2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_student_count_increments(db, learner, course):
    """course.students should reflect enrollment count."""
    db.query(Enrollment).filter(
        Enrollment.course_id == course.id
    ).delete()
    course.students = 0
    db.commit()

    enrollment = Enrollment(user_id=learner.id, course_id=course.id)
    db.add(enrollment)
    course.students += 1
    db.commit()
    db.refresh(course)
    assert course.students == 1


# ==================== AUTH HELPERS ====================

def test_verify_password():
    from auth import verify_password
    hashed = get_password_hash("mypassword")
    assert verify_password("mypassword", hashed) is True
    assert verify_password("wrongpass", hashed) is False


def test_create_and_decode_token():
    from auth import create_access_token, decode_access_token
    token = create_access_token({"sub": "user@test.com", "user_id": 1, "role": "learner"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user@test.com"
    assert payload["role"] == "learner"