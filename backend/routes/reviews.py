"""Course review endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Course, Enrollment, Review, User
from schemas import ReviewCreate

router = APIRouter()


@router.get("/{course_id}")
async def list_reviews(course_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.course_id == course_id).order_by(Review.created_at.desc()).all()
    return {"success": True, "data": reviews, "message": "Reviews loaded"}


@router.post("/{course_id}")
async def create_review(
    course_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(status_code=404, detail="Course not found")
    enrolled = db.query(Enrollment).filter_by(user_id=current_user.id, course_id=course_id).first()
    if not enrolled:
        raise HTTPException(status_code=403, detail="Enroll before reviewing a course")
    review = db.query(Review).filter_by(user_id=current_user.id, course_id=course_id).first()
    if review:
        review.rating = review_data.rating
        review.comment = review_data.comment
    else:
        review = Review(user_id=current_user.id, course_id=course_id, rating=review_data.rating, comment=review_data.comment)
        db.add(review)
    course = db.query(Course).filter(Course.id == course_id).first()
    db.flush()
    ratings = [item.rating for item in db.query(Review).filter_by(course_id=course_id).all()]
    course.rating = sum(ratings) / len(ratings) if ratings else 0
    db.commit()
    return {"success": True, "data": {"id": review.id, "rating": review.rating}, "message": "Review saved"}
