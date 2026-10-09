"""Learner lesson completion and progress endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Enrollment, Lesson, LessonCompletion, User

router = APIRouter()


@router.get("/")
async def get_completions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    completions = db.query(LessonCompletion).filter(
        LessonCompletion.user_id == current_user.id
    ).all()
    return {"success": True, "data": [
        {"id": item.id, "lesson_id": item.lesson_id, "completed_at": item.completed_at}
        for item in completions
    ], "message": "Completions loaded"}


@router.post("/")
async def complete_lesson(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesson_id = payload.get("lesson_id")
    course_id = payload.get("course_id")
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id,
    ).first()
    if not lesson or not enrollment or lesson.module.course_id != course_id:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")

    completion = db.query(LessonCompletion).filter_by(
        user_id=current_user.id, lesson_id=lesson_id
    ).first()
    if not completion:
        completion = LessonCompletion(user_id=current_user.id, lesson_id=lesson_id)
        db.add(completion)
        current_user.xp = (current_user.xp or 0) + 10

    total_lessons = db.query(Lesson).join(Lesson.module).filter(
        Lesson.module.has(course_id=course_id)
    ).count()
    completed_lessons = db.query(LessonCompletion).join(LessonCompletion.lesson).filter(
        LessonCompletion.user_id == current_user.id,
        Lesson.module.has(course_id=course_id),
    ).count() + (0 if completion.id else 1)
    enrollment.total_lessons = total_lessons
    enrollment.completed_lessons = completed_lessons
    enrollment.progress = round((completed_lessons / total_lessons) * 100) if total_lessons else 0
    enrollment.last_accessed = datetime.utcnow()
    if enrollment.progress >= 100:
        enrollment.completed_at = datetime.utcnow()
    db.commit()
    return {"success": True, "data": {"lesson_id": lesson_id, "progress": enrollment.progress}, "message": "Lesson completed"}
