"""
StudyBuddy AI - Base Agent
===========================
Base class for all AI agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

from core.llm import get_llm, GeminiLLM
from core.rag import get_rag_system, RAGSystem

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for StudyBuddy AI agents.
    
    All agents have access to:
    - LLM for generation
    - RAG system for retrieval
    - Logging
    - Error handling
    """
    
    def __init__(self, name: str = "BaseAgent"):
        """
        Initialize the agent.
        
        Args:
            name: Agent name for logging
        """
        self.name = name
        self.llm: GeminiLLM = get_llm()
        self.rag: RAGSystem = get_rag_system()
        self.logger = logging.getLogger(f"studybuddy.agents.{name}")
        
        self.logger.info(f"{name} initialized")
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """
        Main entry point for the agent.
        
        Must be implemented by subclasses.
        """
        pass
    
    async def _generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional generation parameters
        
        Returns:
            Generated text
        """
        try:
            return await self.llm.generate(prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            raise
    
    async def _retrieve(
        self,
        query: str,
        course_id: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant content using RAG.
        
        Args:
            query: Search query
            course_id: Course to search in
            top_k: Number of results
        
        Returns:
            List of relevant chunks
        """
        try:
            return await self.rag.query(query, course_id, top_k)
        except Exception as e:
            self.logger.error(f"Retrieval failed: {e}")
            return []
    
    def _log_action(self, action: str, details: Dict[str, Any] = None) -> None:
        """
        Log an agent action.
        
        Args:
            action: Action description
            details: Additional details
        """
        log_entry = {
            "agent": self.name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        self.logger.info(f"{action}", extra=log_entry)
