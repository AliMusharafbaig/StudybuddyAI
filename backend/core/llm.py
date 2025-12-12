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
        
        # Configure generation settings - optimized for faster, concise responses
        self.generation_config = genai.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=1000,  # Balanced for speed + quality
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
        max_tokens: int = 1000  # Balanced for speed + quality
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
        
        # Retry parameters
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries + 1):
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
                    if attempt < max_retries:
                         logger.warning(f"Empty response from Gemini. Retrying in {base_delay}s...")
                         await asyncio.sleep(base_delay)
                         base_delay *= 2
                         continue
                    return self._fallback_response(prompt)
                    
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < max_retries:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"Gemini Rate Limit (429). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                
                logger.error(f"Gemini generation error: {e}")
                if attempt == max_retries:
                    return self._fallback_response(prompt, error=e)
        
        # Fallback if all retries exhausted without explicit return
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

Extract up to {max_concepts} concepts. Return ONLY the JSON array.
    
CRITICAL INSTRUCTIONS:
- IGNORE headers, footers, page numbers, and citations.
- IGNORE generic terms like "Chapter", "Figure", "Table", "Section", "Summary", "References".
- IGNORE common verbs or adjectives used as nouns (e.g. "Cross" from "Cross-reference", "General", "Basic").
- ONLY extract substantive educational topics / technical terms defined in the text.
- Definitions MUST be complete sentences from the text, not just "A concept".

Return ONLY the JSON array:"""

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

Generate exactly {num_questions} questions. 
    
QUALITY CONTROL:
- Questions MUST be specific to the concept definition provided.
- NO generic questions like "What is X?". Use "What is the primary function of X in the context of Y?"
- Distractors/Options must be plausible and related to the subject matter.
- Do NOT use "All of the above" or "None of the above".
- Ensure the correct answer is unambiguously correct based on the definition.

Return ONLY the JSON array:"""

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
        has_relevant_context = False
        
        if context and len(context) > 0:
            # Check if we have meaningful context (not empty strings)
            meaningful_chunks = [c for c in context[:5] if c and (
                (isinstance(c, dict) and c.get('text', '').strip()) or 
                (isinstance(c, str) and c.strip())
            )]
            
            if meaningful_chunks:
                has_relevant_context = True
                context_text = "\n\nRELEVANT COURSE MATERIAL (use as primary source):\n"
                for chunk in meaningful_chunks:
                    if isinstance(chunk, dict):
                        chunk_text = chunk.get('text', str(chunk))
                    else:
                        chunk_text = str(chunk)
                    context_text += f"---\n{chunk_text}\n"
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n\nPREVIOUS CONVERSATION:\n"
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", str(msg))
                history_text += f"{role.upper()}: {content}\n"
        
        # Build a more helpful prompt that encourages the AI to always help
        if has_relevant_context:
            prompt = f"""You are an expert AI study tutor. Give CONCISE, well-structured answers.

{context_text}

{history_text}

STUDENT'S QUESTION: {question}

INSTRUCTIONS:
1. Be BRIEF and to the point - aim for 3-5 bullet points or 2-3 short paragraphs max.
2. Use course materials when relevant.
3. Structure your answer clearly with bullet points.
4. If the topic is complex, give a quick summary and ask "Would you like me to explain any part in more detail?"
5. NO long essays - keep it scannable and easy to read.

FORMAT:
- Use **bold** for key terms
- Use bullet points (not long paragraphs)
- Keep each point to 1-2 sentences
- End with "Need more detail on any point?" if topic is complex

Give a CONCISE, structured answer."""
        else:
            # No course context - check if user already confirmed they want general knowledge
            # Look for confirmation patterns in conversation history
            user_confirmed = False
            if conversation_history:
                for msg in conversation_history[-3:]:  # Check last 3 messages
                    content = msg.get("content", "").lower()
                    if msg.get("role") == "user" and any(word in content for word in ["yes", "proceed", "go ahead", "sure", "okay", "ok", "continue", "please do", "yep", "yeah"]):
                        user_confirmed = True
                        break
            
            if user_confirmed:
                # User confirmed - give answer but keep it concise
                prompt = f"""You are an expert AI study tutor. Give CONCISE, well-structured answers.

{history_text}

STUDENT'S QUESTION: {question}

The student wants you to answer using your general knowledge.

INSTRUCTIONS:
1. Be BRIEF - aim for 3-5 bullet points or 2-3 short paragraphs max.
2. Give the KEY information they need, not everything you know.
3. Use simple, clear language.
4. If topic is complex, give quick summary and offer: "Want me to explain [specific aspect] in more detail?"
5. NO long essays - keep it scannable.

FORMAT:
- Use **bold** for key terms
- Use bullet points (not long paragraphs)
- Keep each point to 1-2 sentences
- End with offer to expand if needed

Give a CONCISE, helpful answer."""
            else:
                # First time asking about topic not in materials - ask for confirmation
                prompt = f"""You are an expert AI study tutor.

{history_text}

STUDENT'S QUESTION: {question}

IMPORTANT: I searched your uploaded course materials but couldn't find specific information about this topic.

Your response should be:
1. Acknowledge that this specific topic doesn't appear to be covered in their uploaded course materials.
2. Ask if they would like you to proceed with answering using your general knowledge.
3. Keep it brief and friendly.

Example format:
"I noticed that **[topic]** isn't covered in your uploaded course materials. 

Would you like me to proceed and explain this topic using my general knowledge? Just say **yes** and I'll give you a complete explanation! 📚"

Keep your response SHORT - just ask for confirmation."""

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
    
    def _fallback_response(self, prompt: str, error: Exception = None) -> str:
        """Generate a fallback response when LLM is unavailable."""
        if error:
            error_msg = str(error)
            if "429" in error_msg:
                return "⚠️ **Rate Limit Exceeded**: The AI service is currently busy. Please wait a moment and try again."
            elif "404" in error_msg and "Not Found" in error_msg:
                 return f"⚠️ **Model Not Found**: The configured model is not available. Error: {error_msg}"
            return f"⚠️ **AI Error**: {error_msg}"

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
