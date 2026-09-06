"""
Admin Routes — Course and User Management.
FastAPI Router for admin-only endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Course, Enrollment, User
from schemas import CourseCreate, CourseResponse, UserResponse
from auth import get_current_admin

router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get platform-wide statistics (admin only)."""
    total_users = db.query(User).count()
    total_courses = db.query(Course).count()
    total_enrollments = db.query(Enrollment).count()
    total_revenue = sum(
        e.course.price or 0
        for e in db.query(Enrollment).all()
        if e.course
    )
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_revenue": total_revenue,
    }


@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)."""
    return db.query(User).all()


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email == current_user.email:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
    return {"success": True, "message": "User deleted"}


@router.get("/courses", response_model=list[CourseResponse])
async def get_all_courses(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get all courses (admin only)."""
    return db.query(Course).all()


@router.post("/courses", response_model=dict)
async def create_course_admin(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a course (admin only)."""
    new_course = Course(
        title=course_data.title,
        description=course_data.description,
        domain=course_data.domain,
        level=course_data.level,
        price=course_data.price,
        instructor=course_data.instructor,
        instructor_id=current_user.id,
        course_url=course_data.course_url,
        status="approved",
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {
        "success": True,
        "message": "Course created",
        "course_id": new_course.id,
    }


@router.patch("/courses/{course_id}/status", response_model=dict)
async def update_course_status(
    course_id: int,
    status: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Approve or reject a course (admin only)."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.status = status
    db.commit()
    return {"success": True, "message": f"Course {status}"}


@router.delete("/courses/{course_id}", response_model=dict)
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete a course (admin only)."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"success": True, "message": "Course deleted"}