"""
Instructor Routes - FastAPI version
Handles instructor-only operations for course management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Course, User, Enrollment, Module, Lesson, Review, Payment
from auth import get_current_user, get_current_instructor
from schemas import CourseCreate, CourseResponse, ModuleCreate, LessonCreate

router = APIRouter()


# ==================== DASHBOARD STATS ====================

@router.get("/dashboard/stats")
async def get_instructor_dashboard_stats(
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics for the instructor.
    Includes: total courses, students, revenue, ratings, recent enrollments.
    """
    # Get instructor's courses
    courses = db.query(Course).filter(Course.instructor_id == current_user.id).all()
    course_ids = [c.id for c in courses]
    
    # Total courses
    total_courses = len(courses)
    
    # Total students (unique enrollments across all courses)
    total_students = 0
    total_revenue = 0
    course_stats = []
    
    for course in courses:
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
        student_count = len(enrollments)
        total_students += student_count
        total_revenue += student_count * (course.price or 0)
        
        # Course specific stats
        completed = sum(1 for e in enrollments if e.progress == 100)
        completion_rate = (completed / student_count * 100) if student_count > 0 else 0
        
        course_stats.append({
            "id": course.id,
            "title": course.title,
            "students": student_count,
            "rating": course.rating or 0,
            "price": course.price,
            "level": course.level,
            "completion_rate": round(completion_rate, 1),
            "status": "active"
        })
    
    # Average rating across all courses
    avg_rating = 0
    if courses:
        total_rating = sum(c.rating or 0 for c in courses)
        avg_rating = total_rating / len(courses)
    
    # Recent enrollments (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_enrollments = 0
    if course_ids:
        recent_enrollments = db.query(Enrollment).filter(
            Enrollment.course_id.in_(course_ids),
            Enrollment.enrolled_at >= week_ago
        ).count()
    
    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_revenue": total_revenue,
        "average_rating": round(avg_rating, 1),
        "recent_enrollments": recent_enrollments,
        "courses": course_stats
    }


@router.get("/stats")
async def get_instructor_stats(
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get basic instructor statistics (legacy endpoint).
    """
    courses = db.query(Course).filter(Course.instructor_id == current_user.id).all()
    
    total_courses = len(courses)
    total_students = 0
    total_revenue = 0
    
    for course in courses:
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
        total_students += len(enrollments)
        total_revenue += len(enrollments) * (course.price or 0)
    
    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_revenue": total_revenue
    }


# ==================== COURSE MANAGEMENT ====================

@router.get("/courses")
async def get_instructor_courses(
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get all courses created by the current instructor with detailed information.
    """
    courses = db.query(Course).filter(Course.instructor_id == current_user.id).all()
    
    result = []
    for course in courses:
        # Get module and lesson counts
        modules = db.query(Module).filter(Module.course_id == course.id).all()
        lesson_count = 0
        for module in modules:
            lessons = db.query(Lesson).filter(Lesson.module_id == module.id).count()
            lesson_count += lessons
        
        result.append({
            "id": course.id,
            "title": course.title,
            "description": course.description[:150] + "..." if len(course.description) > 150 else course.description,
            "domain": course.domain,
            "level": course.level,
            "price": course.price,
            "students": course.students or 0,
            "rating": course.rating or 0,
            "modules_count": len(modules),
            "lessons_count": lesson_count,
            "image_url": getattr(course, 'image_url', None) or "https://via.placeholder.com/300x200",
            "course_url": course.course_url,
            "status": getattr(course, 'status', 'active')
        })
    
    return result


@router.get("/courses/{course_id}")
async def get_instructor_course(
    course_id: int,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get a specific course by ID (instructor only).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    return course


@router.get("/courses/{course_id}/analytics")
async def get_course_analytics(
    course_id: int,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific course including:
    - Enrollment stats
    - Completion rates
    - Student progress
    - Reviews and ratings
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    # Get enrollments
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    total_students = len(enrollments)
    
    # Completion rate
    completed = sum(1 for e in enrollments if e.progress == 100)
    completion_rate = (completed / total_students * 100) if total_students > 0 else 0
    
    # Average progress
    avg_progress = sum(e.progress for e in enrollments) / total_students if total_students > 0 else 0
    
    # Progress distribution
    progress_distribution = {
        "0-25": 0,
        "26-50": 0,
        "51-75": 0,
        "76-99": 0,
        "100": 0
    }
    
    for enrollment in enrollments:
        if enrollment.progress == 100:
            progress_distribution["100"] += 1
        elif enrollment.progress >= 76:
            progress_distribution["76-99"] += 1
        elif enrollment.progress >= 51:
            progress_distribution["51-75"] += 1
        elif enrollment.progress >= 26:
            progress_distribution["26-50"] += 1
        else:
            progress_distribution["0-25"] += 1
    
    # Recent reviews
    reviews = db.query(Review).filter(Review.course_id == course_id).order_by(
        Review.created_at.desc()
    ).limit(5).all()
    
    # Payment stats
    payments = db.query(Payment).filter(
        Payment.course_id == course_id,
        Payment.status == "completed"
    ).all()
    total_revenue = sum(p.amount for p in payments)
    
    return {
        "total_students": total_students,
        "completion_rate": round(completion_rate, 1),
        "average_progress": round(avg_progress, 1),
        "total_revenue": total_revenue,
        "average_rating": course.rating or 0,
        "total_reviews": len(reviews),
        "progress_distribution": progress_distribution,
        "recent_reviews": [
            {
                "user_name": r.user.name,
                "rating": r.rating,
                "comment": r.comment[:100] + "..." if len(r.comment) > 100 else r.comment,
                "date": r.created_at.strftime("%Y-%m-%d")
            }
            for r in reviews
        ]
    }


@router.post("/courses")
async def create_instructor_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Create a new course (instructor only).
    """
    # Create course URL from title
    course_url = f"/courses/{course_data.title.lower().replace(' ', '-').replace('/', '-')}"
    
    new_course = Course(
        title=course_data.title,
        description=course_data.description,
        domain=course_data.domain,
        level=course_data.level,
        price=course_data.price,
        instructor=current_user.name,
        instructor_id=current_user.id,
        course_url=course_url,
        students=0,
        rating=0,
        status="active"
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return {
        "success": True,
        "message": "Course created successfully",
        "course_id": new_course.id,
        "course": {
            "id": new_course.id,
            "title": new_course.title,
            "course_url": new_course.course_url
        }
    }


@router.put("/courses/{course_id}")
async def update_instructor_course(
    course_id: int,
    course_data: CourseCreate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Update an existing course (instructor only).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    # Update fields
    course.title = course_data.title
    course.description = course_data.description
    course.domain = course_data.domain
    course.level = course_data.level
    course.price = course_data.price
    
    db.commit()
    db.refresh(course)
    
    return {
        "success": True,
        "message": "Course updated successfully",
        "course_id": course.id
    }


@router.delete("/courses/{course_id}")
async def delete_instructor_course(
    course_id: int,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Delete a course (instructor only).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    # Delete associated enrollments
    db.query(Enrollment).filter(Enrollment.course_id == course_id).delete()
    
    # Delete associated modules and lessons
    modules = db.query(Module).filter(Module.course_id == course_id).all()
    for module in modules:
        db.query(Lesson).filter(Lesson.module_id == module.id).delete()
    db.query(Module).filter(Module.course_id == course_id).delete()
    
    # Delete the course
    db.delete(course)
    db.commit()
    
    return {"success": True, "message": "Course deleted successfully"}


# ==================== MODULE & LESSON MANAGEMENT ====================

@router.get("/courses/{course_id}/modules")
async def get_instructor_course_modules(
    course_id: int,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get all modules for a specific course (instructor only).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    modules = db.query(Module).filter(Module.course_id == course_id).order_by(Module.order).all()
    
    result = []
    for module in modules:
        lessons = db.query(Lesson).filter(Lesson.module_id == module.id).order_by(Lesson.order).all()
        result.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "order": module.order,
            "lessons": [
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "video_url": lesson.video_url,
                    "content": lesson.content,
                    "order": lesson.order
                }
                for lesson in lessons
            ]
        })
    
    return result


@router.post("/courses/{course_id}/modules")
async def create_instructor_module(
    course_id: int,
    module_data: ModuleCreate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Add a new module to a course (instructor only).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    module_count = db.query(Module).filter(Module.course_id == course_id).count()
    
    new_module = Module(
        course_id=course_id,
        title=module_data.title,
        description=module_data.description,
        order=module_count + 1
    )
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    
    return {
        "success": True,
        "message": "Module added successfully",
        "module_id": new_module.id,
        "module": {
            "id": new_module.id,
            "title": new_module.title,
            "order": new_module.order
        }
    }


@router.put("/modules/{module_id}")
async def update_instructor_module(
    module_id: int,
    module_data: ModuleCreate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Update an existing module (instructor only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    module.title = module_data.title
    module.description = module_data.description
    
    db.commit()
    db.refresh(module)
    
    return {
        "success": True,
        "message": "Module updated successfully",
        "module_id": module.id
    }


@router.delete("/modules/{module_id}")
async def delete_instructor_module(
    module_id: int,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Delete a module (instructor only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    # Delete associated lessons
    db.query(Lesson).filter(Lesson.module_id == module_id).delete()
    
    db.delete(module)
    db.commit()
    
    return {"success": True, "message": "Module deleted successfully"}


@router.post("/modules/{module_id}/lessons")
async def create_instructor_lesson(
    module_id: int,
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Add a new lesson to a module (instructor only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    lesson_count = db.query(Lesson).filter(Lesson.module_id == module_id).count()
    
    new_lesson = Lesson(
        module_id=module_id,
        title=lesson_data.title,
        description=lesson_data.description,
        video_url=lesson_data.video_url,
        content=lesson_data.content,
        order=lesson_count + 1
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    
    return {
        "success": True,
        "message": "Lesson added successfully",
        "lesson_id": new_lesson.id,
        "lesson": {
            "id": new_lesson.id,
            "title": new_lesson.title,
            "order": new_lesson.order
        }
    }


@router.put("/lessons/{lesson_id}")
async def update_instructor_lesson(
    lesson_id: int,
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Update an existing lesson (instructor only).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    lesson.title = lesson_data.title
    lesson.description = lesson_data.description
    lesson.video_url = lesson_data.video_url
    lesson.content = lesson_data.content
    
    db.commit()
    db.refresh(lesson)
    
    return {
        "success": True,
        "message": "Lesson updated successfully",
        "lesson_id": lesson.id
    }


@router.delete("/lessons/{lesson_id}")
async def delete_instructor_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Delete a lesson (instructor only).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    db.delete(lesson)
    db.commit()
    
    return {"success": True, "message": "Lesson deleted successfully"}


# ==================== STUDENT MANAGEMENT ====================

@router.get("/courses/{course_id}/students")
async def get_course_students(
    course_id: int,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get all students enrolled in a specific course (instructor only).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).join(User).all()
    
    result = []
    for enrollment in enrollments:
        user = db.query(User).filter(User.id == enrollment.user_id).first()
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "progress": enrollment.progress,
            "completed_lessons": enrollment.completed_lessons,
            "enrolled_at": enrollment.enrolled_at.strftime("%Y-%m-%d %H:%M"),
            "last_active": getattr(enrollment, 'last_active', None)
        })
    
    return result


@router.get("/students/performance")
async def get_students_performance(
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db),
    limit: int = 10,
    sort_by: str = "progress"  # progress, name, enrolled_at
):
    """
    Get top performing students across all instructor's courses.
    """
    # Get instructor's courses
    course_ids = db.query(Course.id).filter(
        Course.instructor_id == current_user.id
    ).all()
    course_ids = [c[0] for c in course_ids]
    
    if not course_ids:
        return []
    
    # Get enrollments with user info
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id.in_(course_ids)
    ).join(User).all()
    
    # Aggregate by student
    student_stats = {}
    for enrollment in enrollments:
        user_id = enrollment.user_id
        if user_id not in student_stats:
            user = db.query(User).filter(User.id == user_id).first()
            student_stats[user_id] = {
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "total_progress": 0,
                "course_count": 0,
                "completed_courses": 0,
                "courses": []
            }
        
        student_stats[user_id]["total_progress"] += enrollment.progress
        student_stats[user_id]["course_count"] += 1
        if enrollment.progress == 100:
            student_stats[user_id]["completed_courses"] += 1
        student_stats[user_id]["courses"].append({
            "course_id": enrollment.course_id,
            "progress": enrollment.progress
        })
    
    # Calculate average progress and sort
    result = []
    for user_id, stats in student_stats.items():
        avg_progress = stats["total_progress"] / stats["course_count"]
        result.append({
            **stats,
            "average_progress": round(avg_progress, 1)
        })
        del result[-1]["total_progress"]
    
    # Sort by specified field
    if sort_by == "progress":
        result.sort(key=lambda x: x["average_progress"], reverse=True)
    elif sort_by == "name":
        result.sort(key=lambda x: x["name"])
    
    return result[:limit]