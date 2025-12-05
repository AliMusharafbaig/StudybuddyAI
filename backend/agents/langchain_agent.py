"""
StudyBuddy AI - LangChain Integration
======================================
LangChain-based agent framework for multi-agent workflows.
"""

from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import Tool, StructuredTool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema import Document
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class StudyBuddyToolInput(BaseModel):
    """Input schema for StudyBuddy tools."""
    query: str = Field(description="The user's question or request")
    course_id: Optional[str] = Field(default=None, description="Optional course ID for context")


class LangChainStudyAgent:
    """
    LangChain-based Study Agent implementing multi-agent workflow.
    
    This agent orchestrates:
    - RAG retrieval for context
    - Quiz generation
    - Explanation generation
    - Concept extraction
    """
    
    def __init__(self, llm=None, rag_system=None):
        from core.llm import get_llm
        from core.rag import get_rag_system
        
        self.llm = llm or get_llm()
        self.rag = rag_system or get_rag_system()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._create_tools()
        logger.info("LangChain StudyAgent initialized")
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools for the agent."""
        
        async def search_knowledge(query: str, course_id: str = None) -> str:
            """Search course materials using RAG."""
            try:
                results = await self.rag.query(query, course_id=course_id, top_k=5)
                return results.get("answer", "No relevant information found.")
            except Exception as e:
                return f"Search failed: {str(e)}"
        
        async def generate_quiz_question(concept: str) -> str:
            """Generate a quiz question for a concept."""
            from agents.quiz_generator import QuizGeneratorAgent
            agent = QuizGeneratorAgent()
            questions = await agent.generate_questions(
                [{"name": concept, "definition": concept}],
                num_questions=1
            )
            if questions:
                q = questions[0]
                return f"Q: {q['question']}\nOptions: {q.get('options', [])}"
            return "Could not generate question."
        
        async def explain_concept(concept: str) -> str:
            """Generate an explanation for a concept."""
            from agents.explanation_builder import ExplanationBuilderAgent
            agent = ExplanationBuilderAgent()
            return await agent.generate_explanation(concept)
        
        return [
            Tool(
                name="search_knowledge",
                description="Search course materials and knowledge base. Use this to find relevant information about a topic.",
                func=lambda q: "Use async version",
                coroutine=search_knowledge
            ),
            Tool(
                name="generate_quiz",
                description="Generate a quiz question about a specific concept. Use this when user wants to test their knowledge.",
                func=lambda q: "Use async version",
                coroutine=generate_quiz_question
            ),
            Tool(
                name="explain_concept",
                description="Generate a detailed explanation for a concept. Use this when user needs help understanding something.",
                func=lambda q: "Use async version",
                coroutine=explain_concept
            )
        ]
    
    async def run(self, user_input: str, course_id: str = None) -> str:
        """
        Run the LangChain agent with the given input.
        
        Args:
            user_input: The user's question or request
            course_id: Optional course ID for context
            
        Returns:
            Agent's response
        """
        try:
            # Add context if course specified
            context = ""
            if course_id:
                context = f"[Context: Course ID {course_id}] "
            
            # For now, use a simple chain since we're using Gemini
            # In production, this would use AgentExecutor with tools
            
            # Determine intent
            if any(word in user_input.lower() for word in ["quiz", "test", "question"]):
                from agents.quiz_generator import QuizGeneratorAgent
                agent = QuizGeneratorAgent()
                questions = await agent.generate_questions(
                    [{"name": user_input, "definition": ""}],
                    num_questions=1
                )
                if questions:
                    q = questions[0]
                    return f"Here's a quiz question:\n\n**{q['question']}**\n\nOptions:\n" + \
                           "\n".join(f"  {chr(65+i)}. {opt}" for i, opt in enumerate(q.get('options', [])))
            
            elif any(word in user_input.lower() for word in ["explain", "what is", "how does", "define"]):
                from agents.explanation_builder import ExplanationBuilderAgent
                agent = ExplanationBuilderAgent()
                return await agent.generate_explanation(user_input)
            
            else:
                # Default: RAG query
                result = await self.rag.query(user_input, course_id=course_id)
                return result.get("answer", "I'm not sure about that. Could you rephrase your question?")
                
        except Exception as e:
            logger.error(f"LangChain agent error: {e}")
            return f"I encountered an error processing your request. Please try again."
    
    def add_to_memory(self, human_message: str, ai_message: str):
        """Add messages to conversation memory."""
        self.memory.chat_memory.add_user_message(human_message)
        self.memory.chat_memory.add_ai_message(ai_message)
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()


# Singleton instance
_langchain_agent: Optional[LangChainStudyAgent] = None


def get_langchain_agent() -> LangChainStudyAgent:
    """Get or create the LangChain study agent."""
    global _langchain_agent
    if _langchain_agent is None:
        _langchain_agent = LangChainStudyAgent()
    return _langchain_agent
