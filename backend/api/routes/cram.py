"""
StudyBuddy AI - Emergency Cram Mode Routes
==========================================
Generate optimized study plans for last-minute exam preparation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
from datetime import datetime
import uuid

from core.database import get_db
from api.models.user import User
from api.models.course import Course
from api.models.concept import Concept
from api.schemas import (
    CramPlanRequest, CramPlanResponse, CramTopicPlan,
    MnemonicRequest, MnemonicResponse
)
from api.middleware.auth import get_current_user
from api.middleware.error_handler import ResourceNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cram", tags=["Emergency Cram Mode"])


@router.post("/generate", response_model=CramPlanResponse)
async def generate_cram_plan(
    request: CramPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🚨 EMERGENCY CRAM MODE 🚨
    
    Generate an optimized study plan when you're short on time.
    
    - **course_id**: Course to study for
    - **hours_available**: Time until exam (0.5-24 hours)
    - **focus_topics**: Optional specific topics to focus on
    
    The plan will:
    - Prioritize high-value topics (most likely on exam)
    - Skip low-probability content
    - Generate condensed study notes
    - Create quick-review cheat sheets
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
    
    # Get concepts ordered by exam importance
    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == request.course_id)
        .order_by(Concept.exam_probability.desc(), Concept.importance_score.desc())
    )
    all_concepts = result.scalars().all()
    
    if not all_concepts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No concepts found for this course. Please upload and process materials first."
        )
    
    total_minutes = int(request.hours_available * 60)
    
    # Calculate ROI for each topic
    # ROI = (exam_probability * importance_score) / estimated_study_time
    # Concepts with low mastery need more time
    topic_plans = []
    skip_topics = []
    used_minutes = 0
    
    for concept in all_concepts:
        # Estimate study time based on mastery
        base_time = 15  # Base 15 minutes per concept
        mastery_factor = (100 - concept.mastery_level) / 100
        estimated_time = int(base_time * (0.5 + mastery_factor))
        
        # Calculate ROI
        roi = (concept.exam_probability * concept.importance_score) / max(estimated_time, 1)
        
        # Check if we have time for this concept
        if used_minutes + estimated_time <= total_minutes and concept.importance_score >= 5:
            # Generate key points
            key_points = [
                f"Definition: {concept.definition[:100]}..." if concept.definition else f"Key concept: {concept.name}",
                f"Importance: {'High' if concept.importance_score >= 8 else 'Medium' if concept.importance_score >= 5 else 'Low'}",
                f"Difficulty: {concept.difficulty.capitalize()}"
            ]
            
            # Generate quick review notes
            if concept.definition:
                quick_notes = f"📌 {concept.name}: {concept.definition[:200]}..."
            else:
                quick_notes = f"📌 {concept.name}: A key concept you should understand."
            
            topic_plans.append(CramTopicPlan(
                topic=concept.name,
                allocated_minutes=estimated_time,
                priority=concept.importance_score,
                key_points=key_points,
                quick_review_notes=quick_notes
            ))
            
            used_minutes += estimated_time
        else:
            # Skip low-priority or time-exceeding topics
            if concept.importance_score < 5:
                skip_topics.append(concept.name)
    
    # Sort by priority
    topic_plans.sort(key=lambda x: x.priority, reverse=True)
    
    # Generate cheat sheet
    cheat_sheet_lines = ["# 📝 CRAM CHEAT SHEET\n"]
    cheat_sheet_lines.append(f"**Course:** {course.name}\n")
    cheat_sheet_lines.append(f"**Study Time:** {request.hours_available} hours\n")
    cheat_sheet_lines.append("---\n")
    
    for i, plan in enumerate(topic_plans[:10], 1):
        cheat_sheet_lines.append(f"## {i}. {plan.topic}\n")
        for point in plan.key_points[:2]:
            cheat_sheet_lines.append(f"- {point}\n")
        cheat_sheet_lines.append("\n")
    
    cheat_sheet = "".join(cheat_sheet_lines)
    
    # Get high priority concepts
    high_priority = [p.topic for p in topic_plans if p.priority >= 8][:5]
    
    logger.info(f"Cram plan generated for course {course.name}: {len(topic_plans)} topics in {used_minutes} minutes")
    
    return CramPlanResponse(
        id=str(uuid.uuid4()),
        course_id=request.course_id,
        total_minutes=used_minutes,
        topics=topic_plans,
        cheat_sheet=cheat_sheet,
        high_priority_concepts=high_priority,
        skip_topics=skip_topics[:10],  # Limit skip list
        created_at=datetime.utcnow()
    )


@router.get("/plan/{plan_id}", response_model=CramPlanResponse)
async def get_cram_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a previously generated cram plan.
    
    Note: Plans are not persisted to database in this version.
    Generate a new plan instead.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Cram plans are not persisted. Please generate a new plan."
    )


# ============================================
# Mnemonic Generation
# ============================================

mnemonic_router = APIRouter(prefix="/mnemonics", tags=["Memory Aids"])


@mnemonic_router.post("/generate", response_model=MnemonicResponse)
async def generate_mnemonic(
    request: MnemonicRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🏰 MEMORY PALACE BUILDER 🏰
    
    Generate mnemonics to help remember concepts.
    
    Types available:
    - **acronym**: Create memorable acronyms
    - **rhyme**: Create rhyming memory aids
    - **story**: Create narrative connections
    - **visual**: Create visual associations
    """
    # Get concept
    result = await db.execute(
        select(Concept).where(Concept.id == request.concept_id)
    )
    concept = result.scalar_one_or_none()
    
    if not concept:
        raise ResourceNotFoundError("Concept", request.concept_id)
    
    # Verify course ownership
    result = await db.execute(
        select(Course).where(
            Course.id == concept.course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this concept"
        )
    
    mnemonic_type = request.mnemonic_type or "acronym"
    
    # Generate mnemonic based on type
    # In production, this would use the LLM
    try:
        from agents.explanation_builder import ExplanationBuilderAgent
        
        agent = ExplanationBuilderAgent()
        result = await agent.generate_mnemonic(
            concept_name=concept.name,
            concept_definition=concept.definition,
            mnemonic_type=mnemonic_type
        )
        
        return MnemonicResponse(
            concept_id=concept.id,
            concept_name=concept.name,
            mnemonic_type=result["type"],
            mnemonic_text=result["mnemonic"],
            explanation=result["explanation"],
            visual_cue=result.get("visual_cue")
        )
    except Exception as e:
        logger.warning(f"Mnemonic generation failed: {e}")
        
        # Fallback mnemonics
        if mnemonic_type == "acronym":
            # Generate simple acronym from concept name
            words = concept.name.split()
            acronym = "".join(w[0].upper() for w in words)
            mnemonic_text = f"{acronym} = {concept.name}"
            explanation = f"Remember '{acronym}' which stands for each word in {concept.name}"
        elif mnemonic_type == "rhyme":
            mnemonic_text = f"To {concept.name} we must attend, understanding to the end!"
            explanation = "A simple rhyme to help remember this concept"
        elif mnemonic_type == "story":
            mnemonic_text = f"Imagine yourself discovering {concept.name}. You're solving a puzzle and the answer appears..."
            explanation = "Create a mental story around learning this concept"
        else:
            mnemonic_text = f"Picture {concept.name} as a glowing light bulb in your mind"
            explanation = "Visual association to remember this concept"
        
        return MnemonicResponse(
            concept_id=concept.id,
            concept_name=concept.name,
            mnemonic_type=mnemonic_type,
            mnemonic_text=mnemonic_text,
            explanation=explanation,
            visual_cue="💡" if mnemonic_type == "visual" else None
        )


@mnemonic_router.get("/{concept_id}", response_model=MnemonicResponse)
async def get_mnemonic(
    concept_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get or generate a mnemonic for a specific concept.
    """
    return await generate_mnemonic(
        MnemonicRequest(concept_id=concept_id),
        current_user,
        db
    )
