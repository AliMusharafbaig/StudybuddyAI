import asyncio
import logging
from sqlalchemy import select
from core.database import async_session_maker
from api.models.quiz import Quiz, Question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def inspect_quiz(quiz_id):
    async with async_session_maker() as db:
        try:
            # Get Quiz
            result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
            quiz = result.scalar_one_or_none()
            
            if not quiz:
                logger.error(f"Quiz {quiz_id} NOT FOUND.")
                return
                
            logger.info(f"Quiz Found: {quiz.id}, Status: {quiz.status}")
            
            # Get Questions
            result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
            questions = result.scalars().all()
            
            logger.info(f"Found {len(questions)} questions.")
            
            for q in questions:
                logger.info(f"Q: {q.question_text[:50]}... | ID: {q.id} | ConceptID: {q.concept_id}")
                
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_quiz("73a21679-4e1a-4451-9872-d22c019720ac"))
