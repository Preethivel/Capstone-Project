"""Enrollment-history-based course recommendations."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Course, Enrollment, User


def get_personalized_recommendations(
    db: Session,
    user: User,
    limit: int = 4,
) -> list[dict]:
    """Rank un-enrolled courses by the learner's domain preferences and popularity."""
    domain_preferences = dict(
        db.query(Course.domain, func.count(Enrollment.id))
        .join(Enrollment, Enrollment.course_id == Course.id)
        .filter(Enrollment.user_id == user.id)
        .group_by(Course.domain)
        .all()
    )
    enrolled_course_ids = {
        course_id
        for (course_id,) in db.query(Enrollment.course_id)
        .filter(Enrollment.user_id == user.id)
        .all()
    }
    courses = (
        db.query(Course)
        .filter(Course.status == "approved", Course.id.notin_(enrolled_course_ids))
        .all()
    )
    courses.sort(
        key=lambda course: (
            domain_preferences.get(course.domain, 0),
            course.students or 0,
            course.rating or 0,
            course.id,
        ),
        reverse=True,
    )

    recommendations = []
    for course in courses[:limit]:
        matching_domain = domain_preferences.get(course.domain, 0) > 0
        recommendations.append({
            "id": course.id,
            "title": course.title,
            "description": (
                course.description[:100] + "..."
                if course.description and len(course.description) > 100
                else (course.description or "")
            ),
            "domain": course.domain,
            "level": course.level,
            "price": course.price,
            "instructor": course.instructor,
            "rating": course.rating,
            "students": course.students,
            "reason": (
                f"Based on your interest in {course.domain}"
                if matching_domain
                else "Popular among students"
            ),
            "course_url": course.course_url,
        })
    return recommendations
