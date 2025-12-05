"""
StudyBuddy AI - Main Application
==================================
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config import settings
from core.database import engine, Base
from core.monitoring import MetricsMiddleware, get_metrics
from api.middleware.logging import setup_logging, RequestLoggingMiddleware
from api.middleware.error_handler import setup_exception_handlers
from api.routes import (
    auth_router,
    courses_router,
    quiz_router,
    analytics_router,
    cram_router,
    mnemonic_router,
    chat_router
)

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("🚀 Starting StudyBuddy AI...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created")
    logger.info(f"📚 StudyBuddy AI is ready! Environment: {settings.environment}")
    
    yield
    
    logger.info("👋 Shutting down StudyBuddy AI...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="StudyBuddy AI",
    description="🎓 AI-Powered Study Platform - Your intelligent study companion",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Metrics middleware
app.add_middleware(MetricsMiddleware)

# Exception handlers
setup_exception_handlers(app)

# Register routers
app.include_router(auth_router, prefix="/api")
app.include_router(courses_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(cram_router, prefix="/api")
app.include_router(mnemonic_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "StudyBuddy AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.environment}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
