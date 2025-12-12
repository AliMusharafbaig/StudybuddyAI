"""
StudyBuddy AI - Quiz Routes
============================
Quiz generation, answering, and results endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
from datetime import datetime

from core.config import settings
from core.database import get_db
from api.models.user import User
from api.models.course import Course
from api.models.quiz import Quiz, Question, ConfusionPattern
from api.models.concept import Concept
from api.schemas import (
    QuizCreate, QuizResponse, QuizWithQuestionsResponse,
    QuestionResponse, QuestionAnswerRequest, QuestionAnswerResponse,
    QuizResultsResponse
)
from api.middleware.auth import get_current_user
from api.middleware.error_handler import ResourceNotFoundError, QuizGenerationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/generate", response_model=QuizWithQuestionsResponse)
async def generate_quiz(
    quiz_request: QuizCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a personalized quiz for a course.
    
    - **course_id**: Course to generate quiz for
    - **title**: Optional quiz title
    - **quiz_type**: practice, exam, cram, or adaptive
    - **difficulty**: easy, medium, hard, or adaptive
    - **num_questions**: Number of questions (1-50)
    - **topics**: Optional list of concept IDs to focus on
    - **time_limit_minutes**: Optional time limit
    """
    # Verify course ownership
    result = await db.execute(
        select(Course).where(
            Course.id == quiz_request.course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", quiz_request.course_id)
    
    # Get concepts for the course
    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == quiz_request.course_id)
        .order_by(Concept.importance_score.desc())
    )
    concepts = result.scalars().all()
    
    if not concepts:
        raise QuizGenerationError("No concepts found for this course. Please upload and process materials first.")
    
    # Create quiz
    quiz = Quiz(
        user_id=current_user.id,
        course_id=quiz_request.course_id,
        title=quiz_request.title or f"Quiz - {course.name}",
        quiz_type=quiz_request.quiz_type,
        difficulty=quiz_request.difficulty.value,
        total_questions=quiz_request.num_questions,
        time_limit_seconds=quiz_request.time_limit_minutes * 60 if quiz_request.time_limit_minutes else None
    )
    
    db.add(quiz)
    await db.flush()  # Get quiz ID
    
    # Generate questions using the Quiz Generator Agent
    try:
        from agents.quiz_generator import QuizGeneratorAgent
        
        quiz_agent = QuizGeneratorAgent()
        questions_data = await quiz_agent.generate_questions(
            concepts=concepts[:quiz_request.num_questions * 2],  # Get more concepts than needed
            num_questions=quiz_request.num_questions,
            difficulty=quiz_request.difficulty.value,
            question_types=["mcq"],  # Force MCQ-only for better quiz experience
            course_id=quiz_request.course_id  # Pass course_id for RAG context
        )
        
        # Create question records
        for i, q_data in enumerate(questions_data[:quiz_request.num_questions]):
            question = Question(
                quiz_id=quiz.id,
                concept_id=q_data.get("concept_id"),
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                difficulty=q_data.get("difficulty", quiz_request.difficulty.value),
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation"),
                question_order=i
            )
            db.add(question)
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        # Fallback: create terminology-based MCQ questions
        # Since definitions may be placeholders, use concept NAMES as options
        import random
        shuffled_concepts = list(concepts)
        random.shuffle(shuffled_concepts)
        
        # Helper to check if a definition is just a placeholder
        def is_placeholder_definition(definition):
            if not definition:
                return True
            placeholder_patterns = [
                "important concept mentioned",
                "key topic or section",
                "a key concept in this subject",
                "times in the material",
            ]
            def_lower = definition.lower()
            return any(pattern in def_lower for pattern in placeholder_patterns)
        
        # Track used questions to prevent duplicates
        used_concept_ids = set()
        questions_created = 0
        
        # Terminology question templates - ask which TERM matches a description
        term_question_templates = [
            "Which of the following terms relates to neural network computations?",
            "Which concept is fundamental to machine learning optimization?", 
            "Which term is associated with deep learning architectures?",
            "Which of these is a key concept in this subject area?",
            "Which term describes a core technique in this field?",
        ]
        
        for i, concept in enumerate(shuffled_concepts):
            if questions_created >= quiz_request.num_questions:
                break
            
            # Skip if concept already used
            if concept.id in used_concept_ids:
                continue
            
            used_concept_ids.add(concept.id)
            
            # Get other concepts for wrong options (use their NAMES, not definitions)
            other_concepts = [c for c in shuffled_concepts if c.id != concept.id and c.id not in used_concept_ids]
            
            if len(other_concepts) >= 3:
                random.shuffle(other_concepts)
                wrong_options = [c.name for c in other_concepts[:3]]
            else:
                # Generate plausible fake concept names as wrong options
                fake_terms = [
                    "Regression Analysis", "Data Normalization", "Feature Engineering",
                    "Model Validation", "Cross-Validation", "Hyperparameter Tuning",
                    "Batch Processing", "Error Propagation", "Loss Optimization"
                ]
                random.shuffle(fake_terms)
                wrong_options = fake_terms[:3]
            
            # Correct answer is the concept NAME
            correct_answer = concept.name
            
            # Build options
            options = [correct_answer] + wrong_options[:3]
            random.shuffle(options)
            
            # Create a meaningful question about this concept
            # If concept has a real definition, use it in the question
            concept_def = concept.definition
            if concept_def and not is_placeholder_definition(concept_def):
                # Has real definition - ask "Which term describes [definition]?"
                truncated_def = concept_def[:120] if len(concept_def) > 120 else concept_def
                question_text = f"Which term best describes: \"{truncated_def}\"?"
                explanation = f"Correct! {concept.name}: {concept_def}"
            else:
                # No real definition - use generic terminology question
                question_text = random.choice(term_question_templates)
                explanation = f"The correct answer is {concept.name}."
            
            question = Question(
                quiz_id=quiz.id,
                concept_id=concept.id,
                question_text=question_text,
                question_type="mcq",
                difficulty=quiz_request.difficulty.value,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                question_order=questions_created
            )
            db.add(question)
            questions_created += 1
        
        logger.info(f"Fallback created {questions_created} questions from {len(concepts)} concepts")
    
    await db.commit()
    await db.refresh(quiz)
    
    # Load questions
    result = await db.execute(
        select(Question)
        .where(Question.quiz_id == quiz.id)
        .order_by(Question.question_order)
    )
    questions = result.scalars().all()
    
    logger.info(f"Quiz generated: {quiz.id} with {len(questions)} questions")
    
    return QuizWithQuestionsResponse(
        id=quiz.id,
        title=quiz.title,
        quiz_type=quiz.quiz_type,
        difficulty=quiz.difficulty,
        total_questions=len(questions),
        answered_questions=0,
        correct_answers=0,
        status=quiz.status,
        time_limit_seconds=quiz.time_limit_seconds,
        created_at=quiz.created_at,
        questions=[QuestionResponse.model_validate(q) for q in questions]
    )


@router.get("/{quiz_id}", response_model=QuizWithQuestionsResponse)
async def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a quiz with its questions.
    """
    result = await db.execute(
        select(Quiz).where(
            Quiz.id == quiz_id,
            Quiz.user_id == current_user.id
        )
    )
    quiz = result.scalar_one_or_none()
    
    if not quiz:
        raise ResourceNotFoundError("Quiz", quiz_id)
    
    result = await db.execute(
        select(Question)
        .where(Question.quiz_id == quiz_id)
        .order_by(Question.question_order)
    )
    questions = result.scalars().all()
    
    return QuizWithQuestionsResponse(
        id=quiz.id,
        title=quiz.title,
        quiz_type=quiz.quiz_type,
        difficulty=quiz.difficulty,
        total_questions=quiz.total_questions,
        answered_questions=quiz.answered_questions,
        correct_answers=quiz.correct_answers,
        score=quiz.score,
        status=quiz.status,
        time_limit_seconds=quiz.time_limit_seconds,
        time_spent_seconds=quiz.time_spent_seconds,
        created_at=quiz.created_at,
        completed_at=quiz.completed_at,
        questions=[QuestionResponse.model_validate(q) for q in questions]
    )


@router.post("/{quiz_id}/questions/{question_id}/answer", response_model=QuestionAnswerResponse)
async def answer_question(
    quiz_id: str,
    question_id: str,
    answer_data: QuestionAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an answer for a quiz question.
    
    Returns immediate feedback including:
    - Whether the answer is correct
    - The correct answer
    - An explanation
    - Any detected confusion patterns
    """
    logger.info(f"Answer submission: quiz_id={quiz_id}, question_id={question_id}, answer={answer_data.answer[:50] if answer_data.answer else 'None'}...")
    
    # Verify quiz ownership
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.course))  # Eager load course relationship
        .where(
            Quiz.id == quiz_id,
            Quiz.user_id == current_user.id
        )
    )
    quiz = result.scalar_one_or_none()
    
    if not quiz:
        logger.warning(f"Quiz not found: {quiz_id}")
        raise ResourceNotFoundError("Quiz", quiz_id)
    
    if quiz.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz is already completed"
        )
    
    # Get question
    result = await db.execute(
        select(Question).where(
            Question.id == question_id,
            Question.quiz_id == quiz_id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        logger.warning(f"Question not found: {question_id} in quiz {quiz_id}")
        raise ResourceNotFoundError("Question", question_id)
    
    if question.user_answer is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question already answered"
        )
    
    # Check answer
    is_correct = answer_data.answer.strip().lower() == question.correct_answer.strip().lower()
    
    # For MCQ, also check by option index
    if question.question_type == "mcq" and question.options:
        try:
            answer_index = int(answer_data.answer)
            if 0 <= answer_index < len(question.options):
                is_correct = question.options[answer_index].strip().lower() == question.correct_answer.strip().lower()
        except (ValueError, TypeError):
            # Answer is text, compare directly
            is_correct = answer_data.answer.strip().lower() == question.correct_answer.strip().lower()
    
    # Update question
    question.user_answer = answer_data.answer
    question.is_correct = is_correct
    question.time_taken_seconds = answer_data.time_taken_seconds
    question.confidence_level = answer_data.confidence_level
    question.answered_at = datetime.utcnow()
    
    # Update quiz stats
    quiz.answered_questions += 1
    if is_correct:
        quiz.correct_answers += 1
    if answer_data.time_taken_seconds:
        quiz.time_spent_seconds += answer_data.time_taken_seconds
    
    # Calculate score
    if quiz.answered_questions > 0:
        quiz.score = (quiz.correct_answers / quiz.answered_questions) * 100
    
    # Check if quiz is complete
    if quiz.answered_questions >= quiz.total_questions:
        quiz.status = "completed"
        quiz.completed_at = datetime.utcnow()
        
        # Update user stats
        current_user.total_quizzes_completed += 1
    
    # Update concept mastery
    if question.concept_id:
        result = await db.execute(
            select(Concept).where(Concept.id == question.concept_id)
        )
        concept = result.scalar_one_or_none()
        if concept:
            concept.times_reviewed += 1
            if is_correct:
                concept.times_correct += 1
                concept.mastery_level = min(100, concept.mastery_level + 5)
            else:
                concept.times_incorrect += 1
                concept.mastery_level = max(0, concept.mastery_level - 3)
            concept.last_reviewed_at = datetime.utcnow()
    
    # Detect confusion patterns (if wrong) - run in BACKGROUND to avoid lag
    confusion_detected = False
    confusion_pattern = None
    intervention_message = None
    
    # Skip confusion detection for now - it causes lag
    # We'll record wrong answers but skip the LLM-based analysis
    # The confusion can be analyzed in batch later
    if not is_correct and question.concept_id:
        # Just record basic confusion without LLM analysis
        try:
            course_name = quiz.course.name if quiz.course else None
            
            # Get concept name
            concept_result = await db.execute(
                select(Concept).where(Concept.id == question.concept_id)
            )
            concept = concept_result.scalar_one_or_none()
            topic_name = concept.name if concept else "Unknown"
            
            # Store simple confusion pattern (no LLM call)
            cp = ConfusionPattern(
                user_id=current_user.id,
                concept_id=question.concept_id,
                pattern_type="incorrect_answer",
                pattern_description=f"Answered incorrectly on {topic_name}",
                confusion_score=0.5,
                user_answer=answer_data.answer,
                correct_answer=question.correct_answer,
                course_name=course_name,
                topic_name=topic_name
            )
            db.add(cp)
        except Exception as e:
            logger.warning(f"Confusion recording failed: {e}")
    
    await db.commit()
    
    return QuestionAnswerResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        confusion_detected=confusion_detected,
        confusion_pattern=confusion_pattern,
        intervention_message=intervention_message
    )


@router.get("/{quiz_id}/results", response_model=QuizResultsResponse)
async def get_quiz_results(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed quiz results including analysis and recommendations.
    """
    result = await db.execute(
        select(Quiz).where(
            Quiz.id == quiz_id,
            Quiz.user_id == current_user.id
        )
    )
    quiz = result.scalar_one_or_none()
    
    if not quiz:
        raise ResourceNotFoundError("Quiz", quiz_id)
    
    # Get questions
    result = await db.execute(
        select(Question)
        .where(Question.quiz_id == quiz_id)
        .order_by(Question.question_order)
    )
    questions = result.scalars().all()
    
    # Get confusion patterns from this quiz
    wrong_concept_ids = [q.concept_id for q in questions if q.is_correct == False and q.concept_id]
    
    result = await db.execute(
        select(Concept)
        .where(Concept.id.in_(wrong_concept_ids))
    )
    weak_concepts = result.scalars().all()
    
    # Generate recommendations
    recommendations = []
    concepts_to_review = []
    
    if quiz.score and quiz.score < 50:
        recommendations.append("Consider reviewing the course materials before retaking the quiz.")
    elif quiz.score and quiz.score < 70:
        recommendations.append("Focus on the concepts you got wrong and practice more.")
    else:
        recommendations.append("Great job! Keep practicing to maintain your knowledge.")
    
    for concept in weak_concepts:
        concepts_to_review.append(concept.name)
    
    if concepts_to_review:
        recommendations.append(f"Review these concepts: {', '.join(concepts_to_review[:5])}")
    
    # Get confusion patterns
    confusion_patterns = []
    result = await db.execute(
        select(ConfusionPattern)
        .where(
            ConfusionPattern.user_id == current_user.id,
            ConfusionPattern.concept_id.in_(wrong_concept_ids) if wrong_concept_ids else False
        )
    )
    patterns = result.scalars().all()
    confusion_patterns = [p.pattern_type for p in patterns]
    
    return QuizResultsResponse(
        quiz=QuizResponse.model_validate(quiz),
        questions=[QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            difficulty=q.difficulty,
            options=q.options,
            question_order=q.question_order,
            user_answer=q.user_answer,
            is_correct=q.is_correct
        ) for q in questions],
        confusion_patterns=confusion_patterns,
        recommendations=recommendations,
        concepts_to_review=concepts_to_review
    )


@router.post("/adaptive", response_model=QuestionResponse)
async def get_adaptive_question(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the next adaptive question based on user's performance.
    
    The question difficulty and topic are selected based on:
    - User's weak concepts
    - Concepts not recently reviewed
    - Optimal difficulty for learning
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
    
    # Find weak concepts (low mastery, many incorrect answers)
    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == course_id)
        .order_by(Concept.mastery_level.asc(), Concept.times_incorrect.desc())
        .limit(5)
    )
    weak_concepts = result.scalars().all()
    
    if not weak_concepts:
        raise QuizGenerationError("No concepts available for adaptive learning")
    
    # Select concept with lowest mastery
    target_concept = weak_concepts[0]
    
    # Determine difficulty based on mastery
    if target_concept.mastery_level < 30:
        difficulty = "easy"
    elif target_concept.mastery_level < 60:
        difficulty = "medium"
    else:
        difficulty = "hard"
    
    # Generate question
    try:
        from agents.quiz_generator import QuizGeneratorAgent
        
        quiz_agent = QuizGeneratorAgent()
        questions = await quiz_agent.generate_questions(
            concepts=[target_concept],
            num_questions=1,
            difficulty=difficulty,
            question_types=["mcq"]
        )
        
        if questions:
            q_data = questions[0]
            return QuestionResponse(
                id=str(uuid.uuid4()),
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                difficulty=difficulty,
                options=q_data.get("options"),
                question_order=0
            )
    except Exception as e:
        logger.warning(f"Adaptive question generation failed: {e}")
    
    # Fallback
    return QuestionResponse(
        id=str(uuid.uuid4()),
        question_text=f"Explain the concept of {target_concept.name} in your own words.",
        question_type="short_answer",
        difficulty=difficulty,
        question_order=0
    )


# Import uuid at the top
import uuid
