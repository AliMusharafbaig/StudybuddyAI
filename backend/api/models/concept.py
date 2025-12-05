"""
StudyBuddy AI - Concept Model
==============================
SQLAlchemy model for extracted concepts and knowledge graph.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from core.database import Base


class Concept(Base):
    """Concept model for extracted key concepts."""
    
    __tablename__ = "concepts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # Concept info
    name = Column(String(255), nullable=False)
    definition = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "Machine Learning", "Neural Networks"
    
    # Scoring
    importance_score = Column(Integer, default=5)  # 1-10 scale
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    exam_probability = Column(Float, default=0.5)  # 0-1 probability of appearing in exam
    
    # Student progress
    mastery_level = Column(Integer, default=0)  # 0-100
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    times_incorrect = Column(Integer, default=0)
    
    # Related concepts (stored as comma-separated IDs)
    prerequisites = Column(Text, nullable=True)
    related_concepts = Column(Text, nullable=True)
    
    # Source tracking
    source_material_id = Column(String(36), nullable=True)
    source_page = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    course = relationship("Course", back_populates="concepts")
    
    def __repr__(self) -> str:
        return f"<Concept(id={self.id}, name={self.name})>"


class ConceptRelation(Base):
    """Model for relationships between concepts (knowledge graph edges)."""
    
    __tablename__ = "concept_relations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    target_concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    
    # Relation type
    relation_type = Column(String(50), nullable=False)  # prerequisite, related, part_of, example_of
    strength = Column(Float, default=1.0)  # 0-1 relationship strength
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<ConceptRelation(source={self.source_concept_id}, target={self.target_concept_id}, type={self.relation_type})>"
