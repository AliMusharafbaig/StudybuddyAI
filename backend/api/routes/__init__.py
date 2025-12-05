"""
StudyBuddy AI - API Routes Module
==================================
"""

from api.routes.auth import router as auth_router
from api.routes.courses import router as courses_router
from api.routes.quiz import router as quiz_router
from api.routes.analytics import router as analytics_router
from api.routes.cram import router as cram_router, mnemonic_router
from api.routes.chat import router as chat_router

__all__ = [
    "auth_router",
    "courses_router",
    "quiz_router",
    "analytics_router",
    "cram_router",
    "mnemonic_router",
    "chat_router",
]
