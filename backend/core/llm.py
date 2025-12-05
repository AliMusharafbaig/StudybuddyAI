"""
StudyBuddy AI - LLM Integration
================================
Google Gemini integration for text generation.
"""

import google.generativeai as genai
from typing import List, Dict, Optional, Any
import logging
import asyncio
from functools import lru_cache
import json
import re

from core.config import settings

logger = logging.getLogger(__name__)


class GeminiLLM:
    """
    Google Gemini LLM wrapper for StudyBuddy AI.
    
    Supports:
    - Text generation
    - Question answering
    - Concept extraction
    - Quiz generation
    - Explanation generation
    """
    
    def __init__(self):
        """Initialize Gemini client."""
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not configured. LLM features will be limited.")
            self.model = None
            return
        
        genai.configure(api_key=settings.gemini_api_key)
        
        # Configure generation settings
        self.generation_config = genai.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )
        
        # Safety settings (relaxed for educational content)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]
        
        try:
            self.model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
            )
            logger.info(f"Gemini model initialized: {settings.gemini_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
    
    async def generate(
        self,
        prompt: str,
        system_instruction: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            temperature: Creativity level (0-1)
            max_tokens: Maximum output tokens
        
        Returns:
            Generated text
        """
        if not self.model:
            return self._fallback_response(prompt)
        
        try:
            # Build the full prompt
            full_prompt = ""
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n"
            full_prompt += prompt
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini")
                return self._fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return self._fallback_response(prompt)
    
    async def extract_concepts(
        self,
        text: str,
        max_concepts: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Extract key concepts from text.
        
        Args:
            text: Source text to analyze
            max_concepts: Maximum number of concepts to extract
        
        Returns:
            List of concept dictionaries with name, definition, importance, difficulty
        """
        prompt = f"""Analyze the following educational text and extract key concepts.

For each concept, provide:
1. name: The concept name (short, clear)
2. definition: A 2-3 sentence explanation
3. importance: Score from 1-10 (10 = most important)
4. difficulty: "easy", "medium", or "hard"
5. category: The topic/category this belongs to

Return ONLY a valid JSON array. Example format:
[
  {{"name": "Neural Network", "definition": "A computing system inspired by biological neural networks...", "importance": 9, "difficulty": "medium", "category": "Machine Learning"}}
]

TEXT TO ANALYZE:
{text[:8000]}

Extract up to {max_concepts} concepts. Return ONLY the JSON array, no other text:"""

        response = await self.generate(prompt, temperature=0.3)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                concepts = json.loads(json_match.group())
                return concepts[:max_concepts]
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse concepts JSON: {e}")
        
        # Fallback: return empty list
        return []
    
    async def generate_quiz_questions(
        self,
        concepts: List[Dict],
        num_questions: int = 10,
        difficulty: str = "medium",
        question_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from concepts.
        
        Args:
            concepts: List of concept dictionaries
            num_questions: Number of questions to generate
            difficulty: Question difficulty level
            question_types: Types of questions (mcq, true_false, short_answer)
        
        Returns:
            List of question dictionaries
        """
        if not question_types:
            question_types = ["mcq", "true_false", "short_answer"]
        
        concepts_text = "\n".join([
            f"- {c['name']}: {c.get('definition', 'No definition')}"
            for c in concepts[:20]
        ])
        
        prompt = f"""Generate {num_questions} quiz questions based on these concepts:

{concepts_text}

Requirements:
- Difficulty: {difficulty}
- Question types: {', '.join(question_types)}
- For MCQ: provide 4 options with one correct answer
- For true_false: provide a statement and the correct answer (true/false)
- For short_answer: provide a question and expected answer

Return ONLY a valid JSON array. Example format:
[
  {{
    "question_text": "What is the primary function of...?",
    "question_type": "mcq",
    "difficulty": "{difficulty}",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "This is correct because...",
    "concept_name": "Related Concept"
  }}
]

Generate exactly {num_questions} questions. Return ONLY the JSON array:"""

        response = await self.generate(prompt, temperature=0.7)
        
        try:
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                questions = json.loads(json_match.group())
                return questions[:num_questions]
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse questions JSON: {e}")
        
        return []
    
    async def generate_explanation(
        self,
        concept: str,
        context: str = None,
        confusion_type: str = None,
        student_level: str = "intermediate"
    ) -> str:
        """
        Generate a detailed explanation for a concept.
        
        Args:
            concept: Concept to explain
            context: Additional context from course materials
            confusion_type: Type of confusion detected
            student_level: Student's expertise level
        
        Returns:
            Detailed explanation text
        """
        prompt = f"""Generate a clear, helpful explanation for the following concept.

CONCEPT: {concept}

{"CONTEXT FROM COURSE MATERIALS:" + chr(10) + context if context else ""}

{"STUDENT CONFUSION:" + chr(10) + confusion_type if confusion_type else ""}

Student level: {student_level}

Provide an explanation that:
1. Starts with a clear, simple definition
2. Explains the core idea in simple terms
3. Provides a real-world analogy or example
4. Includes common misconceptions to avoid
5. Ends with a quick summary

Keep the tone friendly and encouraging. Use markdown formatting."""

        return await self.generate(prompt, temperature=0.7)
    
    async def answer_question(
        self,
        question: str,
        context: List[Dict] = None,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Answer a student's question using RAG context.
        
        Args:
            question: Student's question
            context: Relevant chunks from course materials
            conversation_history: Previous conversation messages
        
        Returns:
            Answer text
        """
        # Build context string
        context_text = ""
        if context:
            context_text = "\n\nRELEVANT COURSE MATERIAL:\n"
            for chunk in context[:5]:
                context_text += f"---\n{chunk.get('text', chunk)}\n"
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n\nPREVIOUS CONVERSATION:\n"
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", str(msg))
                history_text += f"{role.upper()}: {content}\n"
        
        prompt = f"""You are a helpful AI study buddy. Answer the student's question clearly and helpfully.

{context_text}

{history_text}

STUDENT'S QUESTION: {question}

Provide a clear, accurate answer. If you reference course materials, cite them. 
If you're unsure, say so and suggest where to find more information.
Use markdown formatting for clarity."""

        return await self.generate(prompt, temperature=0.7)
    
    async def generate_mnemonic(
        self,
        concept_name: str,
        concept_definition: str,
        mnemonic_type: str = "acronym"
    ) -> Dict[str, str]:
        """
        Generate a mnemonic for a concept.
        
        Args:
            concept_name: Name of the concept
            concept_definition: Definition of the concept
            mnemonic_type: Type of mnemonic (acronym, rhyme, story, visual)
        
        Returns:
            Dictionary with mnemonic details
        """
        prompt = f"""Create a memorable {mnemonic_type} to help remember this concept:

CONCEPT: {concept_name}
DEFINITION: {concept_definition or "A key concept to remember"}

Generate a {mnemonic_type} that is:
- Easy to remember
- Fun and engaging
- Accurately represents the concept

Return as JSON:
{{
  "type": "{mnemonic_type}",
  "mnemonic": "The actual mnemonic text",
  "explanation": "Why this helps you remember",
  "visual_cue": "An emoji or short visual description"
}}

Return ONLY the JSON:"""

        response = await self.generate(prompt, temperature=0.9)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback
        return {
            "type": mnemonic_type,
            "mnemonic": f"Remember {concept_name}!",
            "explanation": "A simple reminder for this concept",
            "visual_cue": "📚"
        }
    
    def _fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when LLM is unavailable."""
        if "concept" in prompt.lower():
            return "I found several important concepts in this material. Please configure the Gemini API key for detailed analysis."
        elif "question" in prompt.lower():
            return "I can help you with that! Please configure the Gemini API key for AI-powered responses."
        elif "explain" in prompt.lower():
            return "Let me explain this concept. For detailed AI-powered explanations, please configure the Gemini API key."
        else:
            return "I'm your AI study buddy! Please configure the Gemini API key for full functionality."


# Singleton instance
@lru_cache(maxsize=1)
def get_llm() -> GeminiLLM:
    """Get the LLM singleton instance."""
    return GeminiLLM()


# Convenience function
async def generate_text(prompt: str, **kwargs) -> str:
    """Generate text using the default LLM."""
    llm = get_llm()
    return await llm.generate(prompt, **kwargs)
