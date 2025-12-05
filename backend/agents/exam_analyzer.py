"""
StudyBuddy AI - Exam Analyzer Agent
=====================================
Analyzes exam patterns and predicts likely questions.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import re

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ExamAnalyzerAgent(BaseAgent):
    """
    Agent for analyzing exam patterns and predicting questions.
    
    Features:
    - Analyzes past exam patterns (if available)
    - Predicts likely exam topics
    - Assigns probability scores to concepts
    - Identifies high-value study areas
    """
    
    def __init__(self):
        super().__init__("ExamAnalyzerAgent")
    
    async def run(
        self,
        concepts: List[Dict[str, Any]],
        past_exams: List[str] = None,
        course_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze course and predict exam content.
        
        Args:
            concepts: List of extracted concepts
            past_exams: Optional list of past exam texts
            course_info: Optional course metadata
        
        Returns:
            Analysis results with predictions
        """
        self._log_action("Analyzing exam patterns", {
            "num_concepts": len(concepts),
            "has_past_exams": bool(past_exams)
        })
        
        if past_exams:
            analysis = await self._analyze_past_exams(past_exams, concepts)
        else:
            analysis = await self._predict_without_history(concepts, course_info)
        
        # Update concept probabilities
        for concept in concepts:
            name = concept.get("name", "").lower()
            if name in analysis.get("topic_weights", {}):
                concept["exam_probability"] = analysis["topic_weights"][name]
        
        self._log_action("Analysis complete", {
            "predictions": len(analysis.get("predicted_topics", []))
        })
        
        return analysis
    
    async def _analyze_past_exams(
        self,
        exams: List[str],
        concepts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze past exams to find patterns.
        
        Args:
            exams: List of past exam texts
            concepts: Course concepts
        
        Returns:
            Analysis with patterns and predictions
        """
        # Combine all exam text
        exam_text = "\n\n=== EXAM ===\n\n".join(exams)
        concept_names = [c.get("name", "") for c in concepts]
        
        prompt = f"""Analyze these past exams and identify patterns for predicting future exam content.

PAST EXAMS:
{exam_text[:8000]}

KNOWN CONCEPTS:
{json.dumps(concept_names[:50], indent=2)}

Analyze and provide:
1. Question types commonly used (MCQ, short answer, essay, problem-solving)
2. Topics that appear frequently
3. Professor's question style
4. Difficulty distribution
5. Topics likely to appear in next exam

Return as JSON:
{{
  "question_types": {{"mcq": 0.4, "short_answer": 0.3, "essay": 0.2, "problem_solving": 0.1}},
  "frequent_topics": ["topic1", "topic2"],
  "professor_style": "Description of question style",
  "difficulty_distribution": {{"easy": 0.2, "medium": 0.5, "hard": 0.3}},
  "predicted_topics": [
    {{"topic": "Topic Name", "probability": 0.85, "reason": "Why this is likely"}}
  ],
  "topic_weights": {{"topic1": 0.9, "topic2": 0.7}}
}}

Return ONLY the JSON:"""

        try:
            response = await self.llm.generate(prompt, temperature=0.3)
            json_match = re.search(r'\{[\s\S]*\}', response)
            
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Past exam analysis failed: {e}")
        
        # Fallback
        return self._basic_analysis(concepts)
    
    async def _predict_without_history(
        self,
        concepts: List[Dict[str, Any]],
        course_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Predict exam content without past exams.
        
        Uses heuristics based on:
        - Concept importance scores
        - Concept difficulty
        - Common exam patterns
        """
        # Sort by importance
        sorted_concepts = sorted(
            concepts,
            key=lambda c: c.get("importance_score", 5) * (1 + c.get("times_reviewed", 0) * 0.1),
            reverse=True
        )
        
        predicted_topics = []
        topic_weights = {}
        
        for concept in sorted_concepts[:20]:
            importance = concept.get("importance_score", 5)
            difficulty = concept.get("difficulty", "medium")
            
            # Calculate probability based on importance
            base_prob = importance / 10.0
            
            # Adjust for difficulty (medium difficulty more likely)
            if difficulty == "medium":
                base_prob *= 1.1
            elif difficulty == "hard":
                base_prob *= 0.9
            
            prob = min(0.95, base_prob)
            name = concept.get("name", "Unknown")
            
            predicted_topics.append({
                "topic": name,
                "probability": round(prob, 2),
                "reason": f"High importance ({importance}/10), {difficulty} difficulty"
            })
            
            topic_weights[name.lower()] = prob
        
        return {
            "question_types": {
                "mcq": 0.4,
                "short_answer": 0.3,
                "problem_solving": 0.2,
                "essay": 0.1
            },
            "frequent_topics": [t["topic"] for t in predicted_topics[:5]],
            "professor_style": "Unknown - no past exams available",
            "difficulty_distribution": {
                "easy": 0.25,
                "medium": 0.50,
                "hard": 0.25
            },
            "predicted_topics": predicted_topics,
            "topic_weights": topic_weights
        }
    
    def _basic_analysis(self, concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback analysis without LLM."""
        topic_weights = {}
        
        for concept in concepts:
            name = concept.get("name", "").lower()
            importance = concept.get("importance_score", 5)
            topic_weights[name] = importance / 10.0
        
        return {
            "question_types": {"mcq": 0.5, "short_answer": 0.3, "essay": 0.2},
            "frequent_topics": [],
            "professor_style": "Unknown",
            "difficulty_distribution": {"easy": 0.3, "medium": 0.4, "hard": 0.3},
            "predicted_topics": [],
            "topic_weights": topic_weights
        }
    
    async def generate_predicted_questions(
        self,
        concepts: List[Dict[str, Any]],
        num_questions: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Generate predicted exam questions.
        
        Args:
            concepts: Course concepts with probabilities
            num_questions: Number of questions to generate
        
        Returns:
            List of predicted questions
        """
        # Sort by exam probability
        sorted_concepts = sorted(
            concepts,
            key=lambda c: c.get("exam_probability", 0.5),
            reverse=True
        )
        
        # Select top concepts
        top_concepts = sorted_concepts[:min(num_questions, len(sorted_concepts))]
        
        prompt = f"""Generate {num_questions} predicted exam questions based on these high-probability topics:

TOPICS (with probability of appearing):
{json.dumps([{"topic": c.get("name"), "probability": c.get("exam_probability", 0.5)} for c in top_concepts], indent=2)}

Generate exam-style questions that cover these topics.
Vary question types: MCQ, short answer, essay, problem-solving.

Return as JSON array:
[
  {{
    "question": "Question text",
    "type": "mcq|short_answer|essay|problem_solving",
    "topic": "Related topic",
    "difficulty": "easy|medium|hard",
    "probability": 0.85
  }}
]

Return ONLY the JSON array:"""

        try:
            response = await self.llm.generate(prompt, temperature=0.7)
            json_match = re.search(r'\[[\s\S]*\]', response)
            
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Question generation failed: {e}")
        
        # Fallback questions
        return [
            {
                "question": f"Explain the concept of {c.get('name', 'Unknown')}.",
                "type": "short_answer",
                "topic": c.get("name", "Unknown"),
                "difficulty": c.get("difficulty", "medium"),
                "probability": c.get("exam_probability", 0.5)
            }
            for c in top_concepts
        ]
