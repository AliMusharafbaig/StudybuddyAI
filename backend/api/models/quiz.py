"""
StudyBuddy AI - Quiz Model
===========================
SQLAlchemy models for quizzes, questions, and answers.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from core.database import Base


class Quiz(Base):
    """Quiz model for generated quizzes."""
    
    __tablename__ = "quizzes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # Quiz info
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    quiz_type = Column(String(50), default="practice")  # practice, exam, cram, adaptive
    difficulty = Column(String(20), default="medium")  # easy, medium, hard, adaptive
    
    # Results
    total_questions = Column(Integer, default=0)
    answered_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score = Column(Float, nullable=True)  # Percentage 0-100
    
    # Timing
    time_limit_seconds = Column(Integer, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    course = relationship("Course", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, score={self.score})>"


class Question(Base):
    """Question model for quiz questions."""
    
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # mcq, true_false, short_answer, problem_solving
    difficulty = Column(String(20), default="medium")
    
    # Options (for MCQ)
    options = Column(JSON, nullable=True)  # ["option1", "option2", "option3", "option4"]
    
    # Answer
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    # User response
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    confidence_level = Column(Integer, nullable=True)  # 1-5 user confidence
    
    # Ordering
    question_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    answered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, type={self.question_type})>"


class ConfusionPattern(Base):
    """Model for tracking confusion patterns."""
    
    __tablename__ = "confusion_patterns"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    
    # Pattern info
    pattern_type = Column(String(100), nullable=False)  # e.g., "overfitting_underfitting_confusion"
    pattern_description = Column(Text, nullable=True)
    confusion_score = Column(Float, default=0.5)  # 0-1 severity
    
    # Simple error tracking (what the user wants)
    user_answer = Column(Text, nullable=True)  # What the user answered
    correct_answer = Column(Text, nullable=True)  # What the correct answer was
    course_name = Column(String(255), nullable=True)  # Course name for display
    topic_name = Column(String(255), nullable=True)  # Topic/concept name for display
    
    # Detection
    trigger_count = Column(Integer, default=1)
    last_triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Intervention
    intervention_shown = Column(Boolean, default=False)
    intervention_type = Column(String(50), nullable=True)  # hint, explanation, mini_lesson
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<ConfusionPattern(id={self.id}, type={self.pattern_type})>"
