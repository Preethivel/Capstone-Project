"""
Course Routes - Listing, Detail, Search, Recommendations
FastAPI Router for course endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
import os

from database import get_db
from models import Course, User
from schemas import CourseCreate, CourseResponse, CourseUpdate
from auth import get_current_user, get_current_instructor, get_current_admin

router = APIRouter()

# ===== TEMPLATES =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ==================== HTML PAGES ====================

@router.get("/page", response_class=HTMLResponse)
async def courses_page(request: Request, db: Session = Depends(get_db)):
    """
    Courses page - HTML rendering.
    """
    courses = db.query(Course).filter(Course.status == "approved").all()
    return templates.TemplateResponse("courses.html", {"request": request, "courses": courses})


@router.get("/page/{course_id}", response_class=HTMLResponse)
async def course_detail_page(request: Request, course_id: int, db: Session = Depends(get_db)):
    """
    Course detail page - HTML rendering.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("course_detail.html", {"request": request, "course": course})


@router.get("/page/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Login page - HTML rendering.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/page/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """
    Signup page - HTML rendering.
    """
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/page/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """
    Dashboard page - HTML rendering.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/page/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """
    Profile page - HTML rendering.
    """
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/page/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    """
    Admin page - HTML rendering.
    """
    courses = db.query(Course).all()
    return templates.TemplateResponse("admin_courses.html", {"request": request, "courses": courses})

# ==================== API ENDPOINTS ====================

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all approved courses.
    
    - **skip**: Number of courses to skip (pagination)
    - **limit**: Maximum number of courses to return
    """
    courses = db.query(Course).filter(Course.status == "approved").offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Get a course by ID.
    
    - **course_id**: The ID of the course to retrieve
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.status == "approved"
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/search")
async def search_courses(
    q: Optional[str] = None,
    domain: Optional[str] = "all",
    level: Optional[str] = "all",
    price: Optional[str] = "all",
    db: Session = Depends(get_db)
):
    """
    Search courses with filters.
    """
    query = db.query(Course).filter(Course.status == "approved")
    
    if q:
        query = query.filter(
            Course.title.contains(q) | Course.description.contains(q)
        )
    if domain and domain != "all":
        query = query.filter(Course.domain == domain)
    if level and level != "all":
        query = query.filter(Course.level == level)
    if price == "free":
        query = query.filter(Course.price == 0)
    elif price == "paid":
        query = query.filter(Course.price > 0)
    
    courses = query.all()
    
    return [{
        "id": c.id,
        "title": c.title,
        "description": c.description[:100] + "..." if c.description and len(c.description) > 100 else (c.description or ""),
        "domain": c.domain,
        "level": c.level,
        "price": c.price,
        "instructor": c.instructor,
        "rating": c.rating,
        "students": c.students,
        "course_url": c.course_url
    } for c in courses]

@router.get("/recommend")
async def recommend_courses(db: Session = Depends(get_db)):
    """
    AI-based course recommendations.
    
    Returns popular courses based on student enrollment count.
    """
    popular = db.query(Course).filter(
        Course.status == "approved"
    ).order_by(Course.students.desc()).limit(4).all()
    
    return [{
        "id": c.id,
        "title": c.title,
        "description": c.description[:100] + "..." if c.description and len(c.description) > 100 else (c.description or ""),
        "domain": c.domain,
        "level": c.level,
        "price": c.price,
        "instructor": c.instructor,
        "rating": c.rating,
        "students": c.students,
        "reason": "🔥 Popular among students",
        "course_url": c.course_url
    } for c in popular]


@router.post("/", response_model=dict)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Create a new course (instructor only).
    
    - **title**: Course title
    - **description**: Course description
    - **domain**: Course domain (Programming, Web Dev, AI & ML, etc.)
    - **level**: Difficulty level (Beginner, Intermediate, Advanced)
    - **price**: Course price (0 for free)
    - **instructor**: Instructor name
    - **course_url**: External course URL (optional)
    """
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
    
    return {
        "success": True,
        "message": "Course created successfully",
        "course_id": new_course.id
    }


@router.put("/{course_id}", response_model=dict)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Update a course (instructor only).
    
    - **course_id**: ID of the course to update
    - **title**: Updated title (optional)
    - **description**: Updated description (optional)
    - **domain**: Updated domain (optional)
    - **level**: Updated level (optional)
    - **price**: Updated price (optional)
    - **instructor**: Updated instructor name (optional)
    - **status**: Updated status (optional)
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id and current_user.email != "admin@learnverse.com":
        raise HTTPException(status_code=403, detail="You do not own this course")
    
    update_data = course_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)
    
    db.commit()
    db.refresh(course)
    
    return {
        "success": True,
        "message": "Course updated successfully",
        "course_id": course.id
    }