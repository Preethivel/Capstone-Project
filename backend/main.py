"""LearnVerse FastAPI application entry point."""

import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes.admin import router as admin_router
from routes.ai import router as ai_router
from routes.auth import router as auth_router
from routes.courses import router as courses_router
from routes.enrollment import router as enrollment_router
from routes.instructor import router as instructor_router
from routes.lesson_completions import router as lesson_completion_router
from routes.recommendations import router as recommendations_router
from routes.reviews import router as reviews_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("learnverse")

app = FastAPI(
    title="LearnVerse API",
    description="AI-powered online learning platform API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

frontend_urls = [
    origin.strip()
    for origin in __import__("os").getenv(
        "FRONTEND_URLS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_urls,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(ai_router, prefix="/api/ai", tags=["LearnVerse AI"])
app.include_router(courses_router, prefix="/api/courses", tags=["Courses"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(enrollment_router, prefix="/api/enroll", tags=["Enrollment"])
app.include_router(instructor_router, prefix="/api/instructor", tags=["Instructor"])
app.include_router(lesson_completion_router, prefix="/api/lesson-completions", tags=["Learning Progress"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(reviews_router, prefix="/api/reviews", tags=["Reviews"])


@app.get("/api")
async def api_root():
    return {
        "success": True,
        "data": {"name": "LearnVerse API", "version": app.version, "docs": "/docs", "health": "/api/health"},
        "message": "LearnVerse API is running",
    }


@app.get("/health", include_in_schema=False)
async def health_check():
    return {
        "success": True,
        "data": {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "version": app.version},
        "message": "LearnVerse API is running",
    }


@app.get("/api/health")
async def api_health_check():
    return {"status": "ok", "service": "LearnVerse API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
