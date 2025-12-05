"""
StudyBuddy AI - Content Processor Service
===========================================
Background service for processing uploaded materials.
"""

import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_factory
from api.models.course import Material, Course
from api.models.concept import Concept
from agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


async def process_material(material_id: str) -> bool:
    """
    Process a material in the background.
    
    Pipeline:
    1. Extract text from file
    2. Chunk and store in vector DB
    3. Extract concepts
    4. Update material and course records
    """
    logger.info(f"Starting processing for material {material_id}")
    
    async with async_session_factory() as db:
        try:
            # Get material
            result = await db.execute(select(Material).where(Material.id == material_id))
            material = result.scalar_one_or_none()
            
            if not material:
                logger.error(f"Material {material_id} not found")
                return False
            
            # Update status
            material.processing_status = "processing"
            await db.commit()
            
            # Process with orchestrator
            orchestrator = AgentOrchestrator()
            
            result = await orchestrator.process_material(
                file_path=material.file_path,
                file_type=material.file_type,
                course_id=material.course_id,
                material_id=material_id
            )
            
            if not result.get("success"):
                material.processing_status = "failed"
                material.processing_error = result.get("error", "Unknown error")
                await db.commit()
                return False
            
            # Store extracted text
            material.text_content = result.get("text", "")[:50000]  # Limit stored text
            material.is_processed = True
            material.processing_status = "completed"
            material.processed_at = datetime.utcnow()
            
            # Store concepts
            concepts_data = result.get("concepts", [])
            for c_data in concepts_data:
                concept = Concept(
                    course_id=material.course_id,
                    name=c_data.get("name", "Unknown"),
                    definition=c_data.get("definition"),
                    category=c_data.get("category"),
                    importance_score=c_data.get("importance", 5),
                    difficulty=c_data.get("difficulty", "medium"),
                    source_material_id=material_id
                )
                db.add(concept)
            
            # Update course stats
            course_result = await db.execute(select(Course).where(Course.id == material.course_id))
            course = course_result.scalar_one_or_none()
            if course:
                course.total_concepts += len(concepts_data)
                course.is_processed = True
            
            await db.commit()
            logger.info(f"Material {material_id} processed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing material {material_id}: {e}")
            material.processing_status = "failed"
            material.processing_error = str(e)
            await db.commit()
            return False
