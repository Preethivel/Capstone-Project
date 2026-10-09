"""Authenticated LearnVerse AI endpoint."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Course, Lesson, User
from schemas import AIChatRequest, AIChatResponse
from services.ai_service import AIServiceError, generate_learning_response

router = APIRouter()


def _build_context(payload: AIChatRequest, db: Session) -> str:
    context_parts = []
    if payload.course_id:
        course = db.query(Course).filter(Course.id == payload.course_id).first()
        if course:
            context_parts.append(
                f"Course: {course.title}\nDomain: {course.domain}\nLevel: {course.level}\n"
                f"Description: {course.description}"
            )
    if payload.lesson_id:
        lesson = db.query(Lesson).filter(Lesson.id == payload.lesson_id).first()
        if lesson:
            context_parts.append(
                f"Lesson: {lesson.title}\nDescription: {lesson.description or ''}\n"
                f"Content: {lesson.content or ''}"
            )
    return "\n\n".join(context_parts)


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate an educational answer for an authenticated learner."""
    del current_user
    context = _build_context(payload, db)
    try:
        response = await asyncio.to_thread(generate_learning_response, payload.message, context)
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return {
        "success": True,
        "data": {"response": response},
        "message": "AI response generated successfully",
    }
