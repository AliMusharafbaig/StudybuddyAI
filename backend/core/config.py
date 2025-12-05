"""
StudyBuddy AI - Core Configuration
===================================
Centralized configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "StudyBuddy AI"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = Field(
        default="change-this-super-secret-key-in-production-min-32-chars",
        min_length=32
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # PostgreSQL
    database_url: str = "sqlite+aiosqlite:///./studybuddy.db"
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "studybuddy_patterns"
    
    # Redis
    redis_url: Optional[str] = None
    
    # Google Gemini AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # File Upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 100
    allowed_file_types: str = "pdf,docx,pptx,mp4,mp3,wav,png,jpg,jpeg"
    
    # FAISS
    faiss_index_dir: str = "./faiss_indices"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Content Processing
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_chunks_per_query: int = 10
    
    # Quiz
    default_quiz_size: int = 10
    max_quiz_size: int = 50
    
    # Whisper
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [ft.strip().lower() for ft in self.allowed_file_types.split(",")]
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.faiss_index_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings


# Global settings instance
settings = get_settings()
