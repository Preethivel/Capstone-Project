from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Course

router = APIRouter()

@router.get("/recommend")
async def get_recommendations(db: Session = Depends(get_db)):
    """Get AI-based course recommendations"""
    popular = db.query(Course).filter(
        Course.status == "approved"
    ).order_by(Course.students.desc()).limit(4).all()
    
    return [{
        "id": c.id,
        "title": c.title,
        "description": c.description[:100] + "...",
        "domain": c.domain,
        "level": c.level,
        "price": c.price,
        "instructor": c.instructor,
        "rating": c.rating,
        "students": c.students,
        "reason": "🔥 Popular among students",
        "course_url": c.course_url
    } for c in popular]