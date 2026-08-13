"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ===== AUTH SCHEMAS =====
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "learner"
    organization: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_name: str
    user_role: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ===== COURSE SCHEMAS =====
class CourseCreate(BaseModel):
    title: str
    description: str
    domain: str
    level: str
    price: float = 0.0
    instructor: str
    course_url: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    level: Optional[str] = None
    price: Optional[float] = None
    instructor: Optional[str] = None
    status: Optional[str] = None

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    domain: str
    level: str
    price: float
    instructor: str
    rating: float
    students: int
    course_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ===== ENROLLMENT SCHEMAS =====
class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    progress: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    course: Optional[CourseResponse] = None

    class Config:
        from_attributes = True

# ===== REVIEW SCHEMAS =====
class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ===== MODULE SCHEMAS =====
class ModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0

class ModuleResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    order: int
    created_at: datetime

    class Config:
        from_attributes = True

# ===== LESSON SCHEMAS =====
class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    content: Optional[str] = None
    order: int = 0

class LessonResponse(BaseModel):
    id: int
    module_id: int
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    content: Optional[str] = None
    order: int
    created_at: datetime

    class Config:
        from_attributes = True

# ===== API RESPONSE =====
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None