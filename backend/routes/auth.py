"""
Authentication Routes - Login, Signup, Logout
FastAPI Router for authentication endpoints.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ADMIN_EMAIL,
)
from services.email_service import send_welcome_email

router = APIRouter()


@router.post("/signup", response_model=dict)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    User registration.
    
    - **name**: Full name
    - **email**: Valid email address
    - **password**: Password (will be hashed)
    - **role**: learner or instructor (default: learner)
    - **organization**: Organization name (optional)
    - **title**: Job title (optional)
    - **bio**: About the user (optional)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role="admin" if user_data.email.lower() == ADMIN_EMAIL else user_data.role,
        organization=user_data.organization,
        title=user_data.title,
        bio=user_data.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    send_welcome_email(db_user.name, db_user.email)
    
    return {
        "success": True,
        "message": "Account created! Please login.",
        "user_id": db_user.id
    }


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    User login - returns JWT token and sets cookies.
    
    - **email**: Registered email address
    - **password**: Account password
    """
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Keep legacy cookies compatible while protecting them from script access.
    secure = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    for key, value in {
        "user_id": str(user.id),
        "user_name": user.name,
        "user_email": user.email,
        "user_role": user.role,
    }.items():
        response.set_cookie(key=key, value=value, httponly=True, secure=secure, samesite="lax")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "user_name": user.name,
        "user_role": user.role
    }


@router.get("/logout")
async def logout(response: Response):
    """
    User logout - clears cookies and redirects to home.
    """
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    response.delete_cookie("user_email")
    response.delete_cookie("user_role")
    return {"success": True, "data": None, "message": "Logged out"}


@router.post("/logout")
async def logout_post(response: Response):
    """
    User logout (POST) - clears cookies and redirects to home.
    """
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    response.delete_cookie("user_email")
    response.delete_cookie("user_role")
    return {"success": True, "data": None, "message": "Logged out"}