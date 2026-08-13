"""
LearnVerse - FastAPI Application
AI-Powered Online Learning Platform - REST API Only
"""

from fastapi import FastAPI, Depends, Request, Form, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime
from typing import Optional

# ===== DATABASE SETUP =====
from database import engine, Base, get_db, SessionLocal
from models import User, Course
from auth import get_password_hash, authenticate_user

# ===== IMPORT ROUTES (FROM ROUTES FOLDER) =====
from routes.auth import router as auth_router
from routes.courses import router as courses_router
from routes.admin import router as admin_router
from routes.enrollment import router as enrollment_router

# ===== GET ABSOLUTE PATHS =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

# ===== APP SETUP =====
app = FastAPI(
    title="LearnVerse API",
    description="AI-Powered Online Learning Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== TEMPLATES & STATIC FILES =====
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CREATE DATABASE TABLES =====
Base.metadata.create_all(bind=engine)

# ===== REGISTER ROUTES FROM ROUTES FOLDER =====
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(courses_router, prefix="/api/courses", tags=["Courses"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(enrollment_router, prefix="/api/enroll", tags=["Enrollment"])

# ==================== HELPER FUNCTIONS ====================
def get_session_from_cookie(user_id: Optional[str] = Cookie(None)):
    """Get user session from cookie."""
    session_data = {
        'user_id': None,
        'user_name': None,
        'user_email': None,
        'user_role': None
    }
    
    print(f"🔍 Cookie user_id: {user_id}")  # Debug print
    
    if user_id:
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.id == int(user_id)).first()
            db.close()
            if user:
                session_data = {
                    'user_id': user.id,
                    'user_name': user.name,
                    'user_email': user.email,
                    'user_role': user.role
                }
                print(f"✅ User found: {user.name}")
            else:
                print(f"❌ No user found with id: {user_id}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return session_data

def get_user_from_session(session_data):
    """Get user object from session data."""
    if session_data.get('user_id'):
        db = SessionLocal()
        user = db.query(User).filter(User.id == session_data['user_id']).first()
        db.close()
        return user
    return None

# ==================== HTML PAGES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    user = get_user_from_session(session)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "session": session,
        "user": user
    })

@app.get("/courses", response_class=HTMLResponse)
async def courses_page(
    request: Request, 
    user_id: Optional[str] = Cookie(None), 
    db: Session = Depends(get_db)
):
    print(f"📚 Courses page - Cookie user_id: {user_id}")  # Debug
    session = get_session_from_cookie(user_id)
    print(f"📚 Session: {session}")  # Debug
    
    courses = db.query(Course).filter(Course.status == "approved").all()
    return templates.TemplateResponse("courses.html", {
        "request": request,
        "session": session,
        "courses": courses,
        "enrollments_count": 0
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    if session['user_id']:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "session": session
    })

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    if session['user_id']:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("signup.html", {
        "request": request,
        "session": session
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    user = get_user_from_session(session)
    
    if not user:
        user = {
            'id': 1,
            'name': 'Guest',
            'email': 'guest@example.com',
            'role': 'learner',
            'xp': 0,
            'level': 1
        }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "session": session,
        "user": user
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    user = get_user_from_session(session)
    
    if not user:
        user = {
            'id': 1,
            'name': 'Guest',
            'email': 'guest@example.com',
            'role': 'learner',
            'xp': 0,
            'level': 1
        }
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "session": session,
        "user": user
    })

@app.get("/course/{course_id}", response_class=HTMLResponse)
async def course_detail_page(
    request: Request, 
    course_id: int, 
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    session = get_session_from_cookie(user_id)
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "session": session
        }, status_code=404)
    
    return templates.TemplateResponse("course_detail.html", {
        "request": request,
        "session": session,
        "course": course
    })

@app.get("/payment", response_class=HTMLResponse)
async def payment_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    return templates.TemplateResponse("payment.html", {
        "request": request,
        "session": session
    })

@app.get("/admin/courses", response_class=HTMLResponse)
async def admin_courses_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    return templates.TemplateResponse("admin_courses.html", {
        "request": request,
        "session": session
    })

@app.get("/admin/course/add", response_class=HTMLResponse)
async def admin_add_course_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    return templates.TemplateResponse("add_course.html", {
        "request": request,
        "session": session
    })

@app.get("/instructor/dashboard", response_class=HTMLResponse)
async def instructor_dashboard_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    return templates.TemplateResponse("instructor_dashboard.html", {
        "request": request,
        "session": session
    })

@app.get("/instructor/course/create", response_class=HTMLResponse)
async def instructor_create_course_page(request: Request, user_id: Optional[str] = Cookie(None)):
    session = get_session_from_cookie(user_id)
    return templates.TemplateResponse("instructor_create_course.html", {
        "request": request,
        "session": session
    })

# ==================== FORM HANDLERS ====================

@app.post("/signup")
async def signup_post(
    request: Request,
    response: Response,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("learner"),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        session = get_session_from_cookie(None)
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "session": session,
            "flash_message": "Email already registered!",
            "flash_type": "danger"
        })
    
    new_user = User(
        name=name,
        email=email,
        password_hash=get_password_hash(password),
        role=role
    )
    db.add(new_user)
    db.commit()
    
    session = get_session_from_cookie(None)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "session": session,
        "flash_message": "Account created! Please login.",
        "flash_type": "success"
    })
@app.post("/login")
async def login_post(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        session = get_session_from_cookie(None)
        return templates.TemplateResponse("login.html", {
            "request": request,
            "session": session,
            "flash_message": "Invalid email or password!",
            "flash_type": "danger"
        })
    
    # Set cookies - make sure these are being set
    response.set_cookie(key="user_id", value=str(user.id), httponly=False)
    response.set_cookie(key="user_name", value=user.name, httponly=False)
    response.set_cookie(key="user_email", value=user.email, httponly=False)
    response.set_cookie(key="user_role", value=user.role, httponly=False)
    
    print(f"✅ Cookies set for user: {user.name} (ID: {user.id})")  # Debug
    
    session = get_session_from_cookie(str(user.id))
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "session": session,
        "flash_message": f"Welcome back, {user.name}!",
        "flash_type": "success"
    })

@app.get("/logout")
async def logout_post(response: Response):
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    response.delete_cookie("user_email")
    response.delete_cookie("user_role")
    return RedirectResponse(url="/", status_code=303)

# ==================== API ENDPOINTS ====================

@app.get("/api/courses/recommend")
async def recommend_courses(db: Session = Depends(get_db)):
    popular = db.query(Course).filter(
        Course.status == "approved"
    ).order_by(Course.students.desc()).limit(4).all()
    
    return [{
        "id": c.id,
        "title": c.title,
        "description": c.description[:100] + "..." if c.description else "",
        "domain": c.domain,
        "level": c.level,
        "price": c.price,
        "instructor": c.instructor,
        "rating": c.rating,
        "students": c.students,
        "reason": "🔥 Popular among students",
        "course_url": c.course_url
    } for c in popular]

@app.get("/api/courses/search")
async def search_courses_api(
    q: Optional[str] = None,
    domain: Optional[str] = "all",
    level: Optional[str] = "all",
    price: Optional[str] = "all",
    db: Session = Depends(get_db)
):
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

# ==================== HEALTH ====================

@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "message": "LearnVerse API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api")
async def root():
    return {
        "name": "LearnVerse API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# ===== RUN APP =====
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )