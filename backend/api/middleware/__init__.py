"""
StudyBuddy AI - Middleware Module
==================================
"""

from api.middleware.auth import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from api.middleware.error_handler import (
    StudyBuddyException,
    ContentExtractionError,
    RAGRetrievalError,
    AgentExecutionError,
    QuizGenerationError,
    LLMError,
    ResourceNotFoundError,
    PermissionDeniedError,
    RateLimitError,
    setup_exception_handlers
)
from api.middleware.logging import (
    setup_logging,
    RequestLoggingMiddleware
)

__all__ = [
    # Auth
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    # Exceptions
    "StudyBuddyException",
    "ContentExtractionError",
    "RAGRetrievalError",
    "AgentExecutionError",
    "QuizGenerationError",
    "LLMError",
    "ResourceNotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "setup_exception_handlers",
    # Logging
    "setup_logging",
    "RequestLoggingMiddleware",
]
