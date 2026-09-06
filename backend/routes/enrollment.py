"""
Enrollment Routes - Enroll, My Courses, Progress
FastAPI Router for enrollment endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Course, Enrollment, Payment, User
from schemas import EnrollmentResponse, EnrollmentCreate
from auth import get_current_user
from services.email_service import send_enrollment_confirmation

router = APIRouter()


@router.post("/{course_id}", response_model=dict)
async def enroll_course(
    course_id: int,
    payment_method: str = Query(default="manual"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")

    if course.price and course.price > 0 and payment_method != "demo":
        raise HTTPException(
            status_code=400,
            detail="Complete the demo checkout before enrolling in a paid course",
        )

    # Keep payment and enrollment in the same transaction for paid courses.
    if course.price and course.price > 0:
        db.add(Payment(
            user_id=current_user.id,
            course_id=course.id,
            amount=course.price,
            status="completed",
            payment_method=payment_method,
            completed_at=datetime.utcnow(),
        ))

    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    db.add(enrollment)
    course.students = db.query(Enrollment).filter(Enrollment.course_id == course_id).count() + 1
    db.commit()
    db.refresh(enrollment)
    send_enrollment_confirmation(current_user.name, current_user.email, course.title)
    
    return {"success": True, "message": f"Enrolled in {course.title}", "enrollment_id": enrollment.id}


@router.get("/", response_model=list[EnrollmentResponse])
async def get_enrollments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's enrollments."""
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).all()
    return enrollments


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific enrollment."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.user_id == current_user.id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.put("/{enrollment_id}/progress", response_model=dict)
async def update_progress(
    enrollment_id: int,
    progress: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update course progress."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.user_id == current_user.id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    if progress < 0 or progress > 100:
        raise HTTPException(status_code=422, detail="Progress must be between 0 and 100")
    enrollment.progress = progress
    enrollment.last_accessed = datetime.utcnow()
    if progress >= 100:
        enrollment.completed_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Progress updated", "progress": progress}