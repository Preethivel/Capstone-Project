"""
Routes Package - Import all route modules
"""

from .auth import router as auth_router
from .courses import router as courses_router
from .admin import router as admin_router
from .enrollment import router as enrollment_router