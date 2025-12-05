"""
StudyBuddy AI - Course Routes
==============================
Course management and material upload endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import os
import uuid
import aiofiles
import logging
from datetime import datetime

from core.config import settings
from core.database import get_db
from api.models.user import User
from api.models.course import Course, Material
from api.models.concept import Concept
from api.schemas import (
    CourseCreate, CourseUpdate, CourseResponse,
    MaterialResponse, ConceptResponse, UploadResponse
)
from api.middleware.auth import get_current_user
from api.middleware.error_handler import ResourceNotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/courses", tags=["Courses"])


# ============================================
# Course CRUD
# ============================================

@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new course.
    
    - **name**: Course name (required)
    - **description**: Course description
    - **code**: Course code (e.g., "CS4063")
    - **instructor**: Instructor name
    - **color**: Hex color for UI (e.g., "#6366F1")
    """
    course = Course(
        user_id=current_user.id,
        name=course_data.name,
        description=course_data.description,
        code=course_data.code,
        instructor=course_data.instructor,
        color=course_data.color or "#6366F1"
    )
    
    db.add(course)
    await db.commit()
    await db.refresh(course)
    
    logger.info(f"Course created: {course.name} by user {current_user.id}")
    
    return CourseResponse.model_validate(course)


@router.get("", response_model=List[CourseResponse])
async def list_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all courses for the current user.
    """
    result = await db.execute(
        select(Course)
        .where(Course.user_id == current_user.id)
        .order_by(Course.created_at.desc())
    )
    courses = result.scalars().all()
    
    return [CourseResponse.model_validate(c) for c in courses]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific course by ID.
    """
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", course_id)
    
    return CourseResponse.model_validate(course)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a course.
    """
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", course_id)
    
    # Update fields
    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    await db.commit()
    await db.refresh(course)
    
    return CourseResponse.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a course and all its materials.
    """
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", course_id)
    
    await db.delete(course)
    await db.commit()
    
    logger.info(f"Course deleted: {course_id} by user {current_user.id}")


# ============================================
# Material Upload
# ============================================

@router.post("/{course_id}/upload", response_model=UploadResponse)
async def upload_material(
    course_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload course material (PDF, DOCX, PPTX, MP4, MP3, images).
    
    The file will be processed asynchronously to extract text and concepts.
    """
    # Verify course exists and belongs to user
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise ResourceNotFoundError("Course", course_id)
    
    # Validate file type
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in settings.allowed_file_types_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_ext}' not allowed. Allowed types: {settings.allowed_file_types}"
        )
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}.{file_ext}"
    file_path = os.path.join(settings.upload_dir, course_id, filename)
    
    # Create directory if needed
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    file_size = 0
    async with aiofiles.open(file_path, 'wb') as out_file:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            file_size += len(chunk)
            if file_size > settings.max_upload_size_bytes:
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
                )
            await out_file.write(chunk)
    
    # Create material record
    material = Material(
        course_id=course_id,
        filename=filename,
        original_filename=file.filename,
        file_type=file_ext,
        file_size=file_size,
        file_path=file_path,
        processing_status="pending"
    )
    
    db.add(material)
    
    # Update course material count
    course.total_materials += 1
    
    await db.commit()
    await db.refresh(material)
    
    # Trigger background processing
    if background_tasks:
        from services.content_processor import process_material
        background_tasks.add_task(process_material, material.id)
    
    logger.info(f"Material uploaded: {file.filename} to course {course_id}")
    
    return UploadResponse(
        material_id=material.id,
        filename=file.filename,
        file_type=file_ext,
        file_size=file_size
    )


@router.get("/{course_id}/materials", response_model=List[MaterialResponse])
async def list_materials(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all materials for a course.
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
    
    result = await db.execute(
        select(Material)
        .where(Material.course_id == course_id)
        .order_by(Material.created_at.desc())
    )
    materials = result.scalars().all()
    
    return [MaterialResponse.model_validate(m) for m in materials]


# ============================================
# Concepts
# ============================================

@router.get("/{course_id}/concepts", response_model=List[ConceptResponse])
async def list_concepts(
    course_id: str,
    category: str = None,
    min_importance: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all extracted concepts for a course.
    
    - **category**: Filter by category
    - **min_importance**: Filter by minimum importance score (1-10)
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
    
    # Build query
    query = select(Concept).where(Concept.course_id == course_id)
    
    if category:
        query = query.where(Concept.category == category)
    if min_importance:
        query = query.where(Concept.importance_score >= min_importance)
    
    query = query.order_by(Concept.importance_score.desc())
    
    result = await db.execute(query)
    concepts = result.scalars().all()
    
    return [ConceptResponse.model_validate(c) for c in concepts]


@router.post("/{course_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def trigger_processing(
    course_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger processing of all unprocessed materials in a course.
    
    This will extract text, identify concepts, and build the knowledge graph.
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
    
    # Get unprocessed materials
    result = await db.execute(
        select(Material).where(
            Material.course_id == course_id,
            Material.is_processed == False
        )
    )
    materials = result.scalars().all()
    
    if not materials:
        return {"message": "All materials already processed", "pending": 0}
    
    # Queue processing tasks
    for material in materials:
        from services.content_processor import process_material
        background_tasks.add_task(process_material, material.id)
    
    logger.info(f"Processing triggered for {len(materials)} materials in course {course_id}")
    
    return {
        "message": "Processing started",
        "pending": len(materials)
    }
