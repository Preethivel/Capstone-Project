"""SQLAlchemy ORM models used by the application."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String(200),
        nullable=False,
    )

    role = Column(
        String(20),
        default="learner",
        nullable=False,
    )

    organization = Column(
        String(200),
        nullable=True,
    )

    title = Column(
        String(100),
        nullable=True,
    )

    bio = Column(
        Text,
        nullable=True,
    )

    xp = Column(
        Integer,
        default=0,
    )

    level = Column(
        Integer,
        default=1,
    )

    badges = Column(
        JSON,
        default=list,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    payments = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    courses_created = relationship(
        "Course",
        back_populates="creator",
        foreign_keys="Course.instructor_id",
    )

    reviews = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    lesson_completions = relationship(
        "LessonCompletion",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    domain = Column(
        String(50),
        nullable=False,
    )

    level = Column(
        String(20),
        nullable=False,
    )

    price = Column(
        Float,
        default=0.0,
    )

    instructor = Column(
        String(100),
        nullable=False,
    )

    instructor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    rating = Column(
        Float,
        default=0.0,
    )

    students = Column(
        Integer,
        default=0,
    )

    status = Column(
        String(20),
        default="approved",
    )

    course_url = Column(
        String(500),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    modules = relationship(
        "Module",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Module.order",
    )

    reviews = relationship(
        "Review",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    payments = relationship(
        "Payment",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    creator = relationship(
        "User",
        back_populates="courses_created",
        foreign_keys=[instructor_id],
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    progress = Column(
        Integer,
        default=0,
    )

    completed_lessons = Column(
        Integer,
        default=0,
    )

    total_lessons = Column(
        Integer,
        default=0,
    )

    enrolled_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    last_accessed = Column(
        DateTime,
        default=datetime.utcnow,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            name="uq_enrollment_user_course",
        ),
    )

    user = relationship(
        "User",
        back_populates="enrollments",
    )

    course = relationship(
        "Course",
        back_populates="enrollments",
    )


class Module(Base):
    __tablename__ = "modules"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    order = Column(
        Integer,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    course = relationship(
        "Course",
        back_populates="modules",
    )

    lessons = relationship(
        "Lesson",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Lesson.order",
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    module_id = Column(
        Integer,
        ForeignKey("modules.id"),
        nullable=False,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    video_url = Column(
        String(500),
        nullable=True,
    )

    content = Column(
        Text,
        nullable=True,
    )

    order = Column(
        Integer,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    module = relationship(
        "Module",
        back_populates="lessons",
    )

    completions = relationship(
        "LessonCompletion",
        back_populates="lesson",
        cascade="all, delete-orphan",
    )


class LessonCompletion(Base):
    __tablename__ = "lesson_completions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False,
    )

    completed_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "lesson_id",
            name="uq_completion_user_lesson",
        ),
    )

    user = relationship(
        "User",
        back_populates="lesson_completions",
    )

    lesson = relationship(
        "Lesson",
        back_populates="completions",
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    status = Column(
        String(20),
        default="pending",
    )

    payment_method = Column(
        String(50),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="payments",
    )

    course = relationship(
        "Course",
        back_populates="payments",
    )


class Review(Base):
    __tablename__ = "reviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    rating = Column(
        Integer,
        nullable=False,
    )

    comment = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            name="uq_review_user_course",
        ),
    )

    user = relationship(
        "User",
        back_populates="reviews",
    )

    course = relationship(
        "Course",
        back_populates="reviews",
    )