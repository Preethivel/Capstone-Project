from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import User
from services.recommendation_service import get_personalized_recommendations

router = APIRouter()


@router.get("/")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recommend approved courses using the authenticated learner's course history."""
    return get_personalized_recommendations(db, current_user)