"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ===== CREATE DATABASE FOLDER =====
db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database')
os.makedirs(db_dir, exist_ok=True)

# ===== DATABASE URL =====
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(db_dir, 'learnverse.db')}"
)

# ===== ENGINE =====
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# ===== SESSION =====
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===== BASE =====
Base = declarative_base()

# ===== DEPENDENCY =====
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()