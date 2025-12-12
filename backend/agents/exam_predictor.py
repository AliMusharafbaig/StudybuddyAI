"""
StudyBuddy AI - Exam Prediction Agent
======================================
Predicts likely exam questions based on course content analysis.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import re

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ExamPredictorAgent(BaseAgent):
    """
    Agent for predicting likely exam questions.
    
    Features:
    - Analyzes concepts by exam_probability and importance
    - Uses RAG to find key exam-worthy content
    - Generates realistic exam-style questions
    - Provides detailed solutions on request
    """
    
    def __init__(self):
        super().__init__("ExamPredictorAgent")
    
    async def run(
        self,
        course_id: str,
        concepts: List[Dict[str, Any]],
        num_predictions: int = 10,
        include_solutions: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Predict likely exam questions for a course.
        
        Args:
            course_id: Course to predict for
            concepts: List of concepts with exam_probability scores
            num_predictions: Number of questions to predict
            include_solutions: Whether to include detailed solutions
        
        Returns:
            List of predicted exam questions
        """
        self._log_action("Predicting exam questions", {
            "num_predictions": num_predictions,
            "num_concepts": len(concepts)
        })
        
        # Sort concepts by exam probability and importance
        sorted_concepts = sorted(
            concepts,
            key=lambda c: (c.get("exam_probability", 0) * 0.6 + c.get("importance_score", 0) * 0.4),
            reverse=True
        )
        
        # Get top concepts for exam prediction
        top_concepts = sorted_concepts[:num_predictions * 2]
        
        # Generate predictions using RAG
        predictions = await self._generate_predictions(
            course_id=course_id,
            concepts=top_concepts,
            num_predictions=num_predictions,
            include_solutions=include_solutions
        )
        
        self._log_action("Predictions generated", {"count": len(predictions)})
        
        return predictions
    
    async def _generate_predictions(
        self,
        course_id: str,
        concepts: List[Dict[str, Any]],
        num_predictions: int,
        include_solutions: bool
    ) -> List[Dict[str, Any]]:
        """Generate exam predictions using RAG context."""
        
        # Get RAG context for concepts
        from core.vector_store import get_vector_store
        vector_store = get_vector_store()
        
        # Build concept context
        concept_contexts = []
        for concept in concepts[:num_predictions * 2]:
            concept_name = concept.get("name", "")
            concept_def = concept.get("definition", "")
            exam_prob = concept.get("exam_probability", 0)
            importance = concept.get("importance_score", 0)
            
            # Get RAG context
            rag_text = ""
            try:
                chunks = vector_store.search(
                    course_id=course_id,
                    query=f"{concept_name} {concept_def}",
                    top_k=2
                )
                if chunks:
                    rag_text = "\n".join([c.get("text", "")[:300] for c in chunks])
            except Exception as e:
                logger.warning(f"RAG retrieval failed for {concept_name}: {e}")
            
            concept_contexts.append({
                "name": concept_name,
                "definition": concept_def,
                "exam_probability": exam_prob,
                "importance": importance,
                "context": rag_text
            })
        
        # Sort by exam probability
        concept_contexts.sort(key=lambda x: x.get("exam_probability", 0), reverse=True)
        
        # Build prompt
        concepts_text = ""
        for i, c in enumerate(concept_contexts[:15], 1):
            concepts_text += f"\n### Concept {i}: {c['name']}\n"
            concepts_text += f"Exam Probability: {c['exam_probability']:.0f}%\n"
            concepts_text += f"Importance: {c['importance']}/10\n"
            concepts_text += f"Definition: {c['definition']}\n"
            if c.get("context"):
                concepts_text += f"Source Material:\n{c['context']}\n"
        
        solution_instruction = """
- Include detailed step-by-step solutions
- Show formulas, derivations, or reasoning
- Provide examples where applicable""" if include_solutions else "- Do NOT include solutions (solutions will be provided separately if requested)"
        
        prompt = f"""You are an expert professor creating exam questions.

Based on the following high-probability exam topics, predict {num_predictions} questions that are MOST LIKELY to appear on an exam.

{concepts_text}

EXAM QUESTION REQUIREMENTS:
- Questions should be exam-realistic and test deep understanding
- Focus on HIGH exam probability concepts (listed above with percentages)
- Mix question types: conceptual, application, problem-solving
- Questions should be challenging but fair
- Reference specific formulas, algorithms, or examples from the source material
{solution_instruction}

QUALITY STANDARDS:
- Questions should be clear and unambiguous
- Each question should test a specific learning objective
- Difficulty should match exam standards
- Questions should require understanding, not just memorization

Return ONLY a valid JSON array:
[
  {{
    "question_text": "Derive the gradient descent update rule for logistic regression and explain how it minimizes the cross-entropy loss.",
    "question_type": "problem_solving",
    "exam_probability": 95,
    "difficulty": "hard",
    "concept_name": "Gradient Descent",
    "solution": "{("Detailed step-by-step solution..." if include_solutions else "")}"
  }}
]

Generate exactly {num_predictions} high-probability exam questions. Return ONLY the JSON array:"""

        try:
            response = await self.llm.generate(prompt, temperature=0.6)
            
            # Extract JSON
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                import json
                predictions = json.loads(json_match.group())
                return predictions[:num_predictions]
        except Exception as e:
            logger.error(f"Exam prediction generation failed: {e}")
        
        return []
    
    async def generate_solution(
        self,
        question: str,
        concept_name: str,
        course_id: str = None
    ) -> str:
        """
        Generate detailed solution for a predicted exam question.
        
        Args:
            question: The exam question
            concept_name: The concept being tested
            course_id: Optional course ID for RAG context
        
        Returns:
            Detailed solution text
        """
        # Get RAG context if course_id provided
        context = ""
        if course_id:
            try:
                from core.vector_store import get_vector_store
                vector_store = get_vector_store()
                chunks = vector_store.search(
                    course_id=course_id,
                    query=f"{concept_name} {question}",
                    top_k=3
                )
                if chunks:
                    context = "\n\n".join([c.get("text", "") for c in chunks])
            except Exception as e:
                logger.warning(f"Failed to get RAG context for solution: {e}")
        
        # Build context section (avoid backslash in f-string for Python 3.11 compatibility)
        context_section = f"Relevant course material:\n{context}" if context else ""
        
        prompt = f"""You are an expert professor providing detailed exam solutions.

Question: {question}
Concept: {concept_name}

{context_section}

Provide a DETAILED, STEP-BY-STEP solution that:
1. Breaks down the problem clearly
2. Shows all mathematical derivations or logical reasoning
3. Explains WHY each step is taken
4. Provides the final answer with context
5. Includes key formulas or concepts used

Make the solution educational and thorough, as if explaining to a student who wants to deeply understand the concept."""

        try:
            solution = await self.llm.generate(prompt, temperature=0.4)
            return solution
        except Exception as e:
            logger.error(f"Solution generation failed: {e}")
            return "Solution generation failed. Please refer to course materials."
