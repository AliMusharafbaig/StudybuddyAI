"""
StudyBuddy AI - Course Model
=============================
SQLAlchemy model for courses and materials.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from core.database import Base


class Course(Base):
    """Course model representing a student's course."""
    
    __tablename__ = "courses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(50), nullable=True)  # e.g., "CS4063"
    instructor = Column(String(255), nullable=True)
    color = Column(String(7), default="#6366F1")  # Hex color for UI
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_progress = Column(Integer, default=0)  # 0-100
    
    # Statistics
    total_concepts = Column(Integer, default=0)
    total_materials = Column(Integer, default=0)
    mastery_percentage = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="courses")
    materials = relationship("Material", back_populates="course", cascade="all, delete-orphan")
    concepts = relationship("Concept", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Course(id={self.id}, name={self.name})>"


class Material(Base):
    """Material model for uploaded course materials."""
    
    __tablename__ = "materials"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, mp4, etc.
    file_size = Column(Integer, default=0)  # bytes
    file_path = Column(String(500), nullable=False)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    
    # Extracted content
    text_content = Column(Text, nullable=True)
    num_pages = Column(Integer, nullable=True)  # For PDFs
    duration_seconds = Column(Integer, nullable=True)  # For audio/video
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    course = relationship("Course", back_populates="materials")
    
    def __repr__(self) -> str:
        return f"<Material(id={self.id}, filename={self.filename})>"
