"""
StudyBuddy AI - Agent Orchestrator
====================================
Coordinates all agents for end-to-end workflows.
"""

from typing import Dict, List, Any
import logging
import asyncio

from agents.content_ingestion import ContentIngestionAgent
from agents.concept_extractor import ConceptExtractorAgent
from agents.exam_analyzer import ExamAnalyzerAgent
from agents.quiz_generator import QuizGeneratorAgent
from agents.confusion_detector import ConfusionDetectorAgent
from agents.explanation_builder import ExplanationBuilderAgent
from core.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates all StudyBuddy AI agents."""
    
    def __init__(self):
        self.content_agent = ContentIngestionAgent()
        self.concept_agent = ConceptExtractorAgent()
        self.exam_agent = ExamAnalyzerAgent()
        self.quiz_agent = QuizGeneratorAgent()
        self.confusion_agent = ConfusionDetectorAgent()
        self.explanation_agent = ExplanationBuilderAgent()
        self.vector_store = get_vector_store()
        logger.info("AgentOrchestrator initialized")
    
    async def process_material(self, file_path: str, file_type: str, course_id: str, material_id: str) -> Dict:
        """Full pipeline: ingest → extract concepts → store in vector DB."""
        # 1. Ingest content
        result = await self.content_agent.run(file_path, file_type, material_id)
        
        if not result.get("chunks"):
            return {"success": False, "error": "No content extracted"}
        
        # 2. Store chunks in vector store
        self.vector_store.add_chunks(course_id, result["chunks"])
        
        # 3. Extract concepts
        full_text = result.get("text", "")
        concepts = await self.concept_agent.run(full_text)
        
        # 4. Analyze for exam predictions
        analysis = await self.exam_agent.run(concepts)
        
        return {
            "success": True,
            "chunks": len(result["chunks"]),
            "concepts": concepts,
            "exam_analysis": analysis
        }
    
    async def generate_quiz(self, course_id: str, concepts: List[Dict], num_questions: int = 10) -> List[Dict]:
        """Generate a quiz for a course."""
        return await self.quiz_agent.generate_questions(concepts, num_questions)
    
    async def handle_answer(self, question: str, user_answer: str, correct_answer: str) -> Dict:
        """Handle an answer and detect confusion."""
        confusion = await self.confusion_agent.detect_confusion(question, user_answer, correct_answer)
        
        response = {"is_correct": user_answer.lower() == correct_answer.lower()}
        
        if confusion:
            explanation = await self.explanation_agent.generate_explanation(
                concept=question[:50],
                confusion_type=confusion.get("pattern_type")
            )
            response["confusion"] = confusion
            response["explanation"] = explanation
        
        return response
