"""
StudyBuddy AI - Analytics Routes
=================================
Study progress, confusion analysis, and exam predictions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import logging
from datetime import datetime, timedelta

from core.database import get_db
from api.models.user import User
from api.models.course import Course
from api.models.quiz import Quiz, Question, ConfusionPattern
from api.models.concept import Concept
from api.schemas import (
    StudyProgressResponse, ConceptMasteryResponse,
    ConfusionAnalysisResponse, ExamPredictionsResponse, ExamPredictionResponse
)
from api.middleware.auth import get_current_user
from api.middleware.error_handler import ResourceNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/progress", response_model=StudyProgressResponse)
async def get_study_progress(
    course_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall study progress for the user.
    
    - **course_id**: Optional filter by course
    """
    # Base query for concepts
    concept_query = select(Concept)
    quiz_query = select(Quiz).where(Quiz.user_id == current_user.id)
    
    if course_id:
        # Verify course ownership
        result = await db.execute(
            select(Course).where(
                Course.id == course_id,
                Course.user_id == current_user.id
            )
        )
        course = result.scalar_one_or_none()
        if not course:
            raise ResourceNotFoundError("Course", course_id)
        
        concept_query = concept_query.where(Concept.course_id == course_id)
        quiz_query = quiz_query.where(Quiz.course_id == course_id)
    else:
        # Get all user's courses
        result = await db.execute(
            select(Course.id).where(Course.user_id == current_user.id)
        )
        course_ids = [c[0] for c in result.all()]
        concept_query = concept_query.where(Concept.course_id.in_(course_ids))
    
    # Get concepts
    result = await db.execute(concept_query)
    concepts = result.scalars().all()
    
    # Calculate concept mastery stats
    concepts_mastered = sum(1 for c in concepts if c.mastery_level >= 80)
    concepts_learning = sum(1 for c in concepts if 30 <= c.mastery_level < 80)
    concepts_weak = sum(1 for c in concepts if c.mastery_level < 30)
    
    # Get quiz stats
    result = await db.execute(quiz_query.where(Quiz.status == "completed"))
    quizzes = result.scalars().all()
    
    total_score = sum(q.score or 0 for q in quizzes)
    average_score = total_score / len(quizzes) if quizzes else 0
    
    # Calculate total study time (from quizzes)
    total_time = sum(q.time_spent_seconds or 0 for q in quizzes) // 60
    
    # Get score history (last 10 quizzes)
    score_history = [
        {
            "date": q.created_at.isoformat(),
            "score": q.score or 0,
            "quiz_type": q.quiz_type
        }
        for q in sorted(quizzes, key=lambda x: x.created_at, reverse=True)[:10]
    ]
    
    # Get recent activity
    recent_activity = []
    for q in sorted(quizzes, key=lambda x: x.created_at, reverse=True)[:5]:
        recent_activity.append({
            "type": "quiz_completed",
            "description": f"Completed {q.title or 'Quiz'} with {q.score:.0f}%" if q.score else f"Completed {q.title or 'Quiz'}",
            "timestamp": q.created_at.isoformat()
        })
    
    return StudyProgressResponse(
        total_study_time_minutes=current_user.total_study_time_minutes + total_time,
        total_quizzes_completed=len(quizzes),
        current_streak_days=current_user.current_streak_days,
        average_score=round(average_score, 1),
        concepts_mastered=concepts_mastered,
        concepts_learning=concepts_learning,
        concepts_weak=concepts_weak,
        recent_activity=recent_activity,
        score_history=score_history
    )


@router.get("/concepts", response_model=List[ConceptMasteryResponse])
async def get_concept_mastery(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get mastery level for all concepts in a course.
    """
    # Verify course ownership
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", course_id)
    
    # Get concepts with mastery info
    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == course_id)
        .order_by(Concept.mastery_level.asc())
    )
    concepts = result.scalars().all()
    
    return [
        ConceptMasteryResponse(
            concept_id=c.id,
            concept_name=c.name,
            mastery_level=c.mastery_level,
            times_reviewed=c.times_reviewed,
            accuracy_rate=(c.times_correct / c.times_reviewed * 100) if c.times_reviewed > 0 else 0,
            last_reviewed=c.last_reviewed_at
        )
        for c in concepts
    ]


@router.get("/confusion", response_model=List[ConfusionAnalysisResponse])
async def get_confusion_analysis(
    course_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get confusion pattern analysis for the user.
    
    Shows common mistakes and recommended actions.
    """
    query = select(ConfusionPattern).where(ConfusionPattern.user_id == current_user.id)
    
    if course_id:
        # Verify course ownership
        result = await db.execute(
            select(Course).where(
                Course.id == course_id,
                Course.user_id == current_user.id
            )
        )
        course = result.scalar_one_or_none()
        if not course:
            raise ResourceNotFoundError("Course", course_id)
        
        # Get concepts in this course
        result = await db.execute(
            select(Concept.id).where(Concept.course_id == course_id)
        )
        concept_ids = [c[0] for c in result.all()]
        query = query.where(ConfusionPattern.concept_id.in_(concept_ids))
    
    result = await db.execute(
        query.order_by(ConfusionPattern.trigger_count.desc()).limit(10)
    )
    patterns = result.scalars().all()
    
    # Get affected concepts
    response = []
    for pattern in patterns:
        affected_concepts = []
        if pattern.concept_id:
            result = await db.execute(
                select(Concept).where(Concept.id == pattern.concept_id)
            )
            concept = result.scalar_one_or_none()
            if concept:
                affected_concepts.append(concept.name)
        
        # Determine recommended action
        if pattern.confusion_score > 0.7:
            action = "Take a mini-lesson on this concept"
        elif pattern.trigger_count > 5:
            action = "Review prerequisite concepts"
        else:
            action = "Practice more questions on this topic"
        
        response.append(ConfusionAnalysisResponse(
            pattern_type=pattern.pattern_type,
            description=pattern.pattern_description or f"Common confusion with {pattern.pattern_type}",
            confusion_score=pattern.confusion_score,
            trigger_count=pattern.trigger_count,
            affected_concepts=affected_concepts,
            recommended_action=action,
            # Simple display fields
            user_answer=pattern.user_answer,
            correct_answer=pattern.correct_answer,
            course_name=pattern.course_name,
            topic_name=pattern.topic_name
        ))
    
    return response


@router.get("/predict/exam", response_model=ExamPredictionsResponse)
async def get_exam_predictions(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get exam predictions for a course.
    
    Predicts likely exam topics and questions based on:
    - Concept importance scores
    - Professor patterns (if available)
    - Topic coverage in materials
    """
    # Verify course ownership
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", course_id)
    
    # Get concepts ordered by exam probability
    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == course_id)
        .order_by(Concept.exam_probability.desc(), Concept.importance_score.desc())
    )
    concepts = result.scalars().all()
    
    if not concepts:
        return ExamPredictionsResponse(
            course_id=course_id,
            predictions=[],
            overall_readiness=0,
            recommended_focus_areas=["Upload and process course materials first"]
        )
    
    # Generate predictions
    predictions = []
    for concept in concepts[:10]:  # Top 10 predictions
        # Calculate study time based on mastery
        study_time = max(5, 30 - int(concept.mastery_level * 0.25))
        
        # Generate sample questions
        sample_questions = [
            f"Explain {concept.name} in your own words.",
            f"What are the key characteristics of {concept.name}?",
            f"Give an example of {concept.name} in practice."
        ]
        
        predictions.append(ExamPredictionResponse(
            topic=concept.name,
            probability=concept.exam_probability,
            importance=concept.importance_score,
            recommended_study_time_minutes=study_time,
            sample_questions=sample_questions[:2]
        ))
    
    # Calculate overall readiness
    avg_mastery = sum(c.mastery_level for c in concepts) / len(concepts) if concepts else 0
    
    # Determine focus areas (low mastery + high importance)
    focus_concepts = sorted(
        concepts,
        key=lambda c: c.importance_score * (100 - c.mastery_level),
        reverse=True
    )[:5]
    recommended_focus = [c.name for c in focus_concepts]
    
    return ExamPredictionsResponse(
        course_id=course_id,
        predictions=predictions,
        overall_readiness=round(avg_mastery, 1),
        recommended_focus_areas=recommended_focus
    )
