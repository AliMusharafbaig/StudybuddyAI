"""
StudyBuddy AI - Exam Prediction Routes
=======================================
Endpoints for predicting exam questions and generating solutions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from core.database import get_db
from api.models.user import User
from api.models.course import Course
from api.models.concept import Concept
from api.schemas import ExamPredictionRequest, ExamPredictionResponse, ExamQuestionResponse
from api.middleware.auth import get_current_user
from api.middleware.error_handler import ResourceNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exam", tags=["Exam Prediction"])


@router.post("/predict", response_model=ExamPredictionResponse)
async def predict_exam_questions(
    request: ExamPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🎯 EXAM PREDICTION 🎯
    
    Predict likely exam questions based on course content analysis.
    
    - **course_id**: Course to predict for
    - **num_predictions**: Number of questions to predict (default: 10)
    - **include_solutions**: Whether to include solutions (default: False)
    
    The predictions are based on:
    - Concept exam probability scores
    - Importance ratings
    - RAG analysis of course materials
    """
    # Verify course ownership
    result = await db.execute(
        select(Course).where(
            Course.id == request.course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", request.course_id)
    
    # Get concepts
    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == request.course_id)
        .order_by(Concept.exam_probability.desc(), Concept.importance_score.desc())
    )
    concepts = result.scalars().all()
    
    if not concepts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No concepts found for this course. Please upload and process materials first."
        )
    
    # Convert to dicts
    concept_dicts = [
        {
            "id": c.id,
            "name": c.name,
            "definition": c.definition,
            "exam_probability": c.exam_probability or 50,
            "importance_score": c.importance_score or 5
        }
        for c in concepts
    ]
    
    # Generate predictions
    try:
        from agents.exam_predictor import ExamPredictorAgent
        
        predictor = ExamPredictorAgent()
        predictions = await predictor.run(
            course_id=request.course_id,
            concepts=concept_dicts,
            num_predictions=request.num_predictions,
            include_solutions=request.include_solutions
        )
        
        return ExamPredictionResponse(
            id=str(uuid.uuid4()),
            course_id=request.course_id,
            predicted_questions=[
                ExamQuestionResponse(
                    question_text=q.get("question_text", ""),
                    question_type=q.get("question_type", "problem_solving"),
                    exam_probability=q.get("exam_probability", 70),
                    difficulty=q.get("difficulty", "medium"),
                    concept_name=q.get("concept_name", ""),
                    solution=q.get("solution") if request.include_solutions else None
                )
                for q in predictions
            ],
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Exam prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate exam predictions: {str(e)}"
        )


@router.post("/predict/{course_id}/solution")
async def generate_solution(
    course_id: str,
    question_text: str,
    concept_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate detailed solution for a predicted exam question.
    
    - **question_text**: The exam question
    - **concept_name**: The concept being tested
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
    
    try:
        from agents.exam_predictor import ExamPredictorAgent
        
        predictor = ExamPredictorAgent()
        solution = await predictor.generate_solution(
            question=question_text,
            concept_name=concept_name,
            course_id=course_id
        )
        
        return {
            "question_text": question_text,
            "concept_name": concept_name,
            "solution": solution
        }
        
    except Exception as e:
        logger.error(f"Solution generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate solution: {str(e)}"
        )
