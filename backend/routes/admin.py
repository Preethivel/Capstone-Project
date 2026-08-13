"""
Admin Routes - Course Management
FastAPI Router for admin endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Course, User
from schemas import CourseResponse, CourseCreate
from auth import get_current_admin

router = APIRouter()


@router.get("/courses", response_model=list[CourseResponse])
async def get_all_courses(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all courses (admin only)."""
    courses = db.query(Course).all()
    return courses


@router.post("/courses", response_model=dict)
async def create_course_admin(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
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
        status="approved"
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return {"success": True, "message": "Course created successfully", "course_id": new_course.id}


@router.delete("/courses/{course_id}", response_model=dict)
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a course (admin only)."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return {"success": True, "message": "Course deleted successfully"}