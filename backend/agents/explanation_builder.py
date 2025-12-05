"""
StudyBuddy AI - Explanation Builder Agent
==========================================
Generates custom explanations targeting confusion points.
"""

from typing import Dict, List, Any, Optional
import logging

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ExplanationBuilderAgent(BaseAgent):
    """Agent for generating custom explanations and mnemonics."""
    
    def __init__(self):
        super().__init__("ExplanationBuilderAgent")
    
    async def run(self, concept: str, confusion_type: str = None, context: str = None) -> str:
        return await self.generate_explanation(concept, confusion_type, context)
    
    async def generate_explanation(self, concept: str, confusion_type: str = None, context: str = None) -> str:
        """Generate a detailed explanation for a concept."""
        return await self.llm.generate_explanation(
            concept=concept,
            context=context,
            confusion_type=confusion_type
        )
    
    async def answer_question(self, question: str, context: List[Dict] = None, conversation_history: List = None) -> str:
        """Answer a question using RAG context."""
        return await self.llm.answer_question(
            question=question,
            context=context,
            conversation_history=conversation_history
        )
    
    async def generate_mnemonic(self, concept_name: str, concept_definition: str, mnemonic_type: str = "acronym") -> Dict:
        """Generate a mnemonic for a concept."""
        return await self.llm.generate_mnemonic(
            concept_name=concept_name,
            concept_definition=concept_definition,
            mnemonic_type=mnemonic_type
        )
