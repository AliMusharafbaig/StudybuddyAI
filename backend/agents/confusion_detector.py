"""
StudyBuddy AI - Confusion Detector Agent
==========================================
Detects learning confusion patterns from student responses using LLM analysis.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import re

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ConfusionDetectorAgent(BaseAgent):
    """
    Agent for detecting student confusion patterns using LLM.
    
    Features:
    - LLM-based analysis of wrong answers
    - Identifies specific misconceptions
    - Provides targeted interventions
    - Tracks patterns by concept area
    """
    
    def __init__(self):
        super().__init__("ConfusionDetectorAgent")
    
    async def run(
        self, 
        question: str, 
        user_answer: str, 
        correct_answer: str, 
        concept_id: str = None,
        concept_name: str = None
    ) -> Optional[Dict]:
        """Detect confusion from a quiz answer."""
        return await self.detect_confusion(
            question, user_answer, correct_answer, concept_id, concept_name
        )
    
    async def detect_confusion(
        self, 
        question: str, 
        user_answer: str, 
        correct_answer: str, 
        concept_id: str = None,
        concept_name: str = None
    ) -> Optional[Dict]:
        """
        Analyze incorrect answers to identify confusion patterns.
        
        Uses LLM to provide more intelligent analysis than keyword matching.
        """
        # If answer is correct, no confusion
        if user_answer.strip().lower() == correct_answer.strip().lower():
            return None
        
        # Use LLM for intelligent confusion analysis
        try:
            pattern = await self._analyze_with_llm(
                question, user_answer, correct_answer, concept_name
            )
            if pattern:
                return pattern
        except Exception as e:
            logger.warning(f"LLM confusion analysis failed: {e}")
        
        # Fallback: Generate meaningful pattern from the question/concept
        return self._generate_meaningful_pattern(question, concept_name, user_answer, correct_answer)
    
    async def _analyze_with_llm(
        self,
        question: str,
        user_answer: str, 
        correct_answer: str,
        concept_name: str = None
    ) -> Optional[Dict]:
        """Use LLM to analyze the confusion pattern."""
        
        prompt = f"""Analyze this incorrect quiz answer and identify the specific confusion or misconception.

QUESTION: {question}
STUDENT'S WRONG ANSWER: {user_answer}
CORRECT ANSWER: {correct_answer}
TOPIC AREA: {concept_name or 'General'}

Identify:
1. What specific misconception led to this wrong answer?
2. What concept are they confusing this with?
3. A brief, helpful intervention tip

Return as JSON:
{{
  "pattern_type": "brief_pattern_name",
  "description": "Specific description of the misconception",
  "confused_with": "What they likely confused this with",
  "intervention": "Brief helpful tip to correct this misconception",
  "score": 0.7
}}

Return ONLY the JSON:"""

        response = await self.llm.generate(prompt, temperature=0.3)
        
        # Parse JSON response
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            # Ensure required fields exist
            if "pattern_type" in result and "description" in result:
                result.setdefault("score", 0.7)
                result.setdefault("intervention", "Review this concept carefully.")
                return result
        
        return None
    
    def _generate_meaningful_pattern(
        self,
        question: str,
        concept_name: str,
        user_answer: str,
        correct_answer: str
    ) -> Dict:
        """Generate a meaningful pattern when LLM fails."""
        
        # Try to extract topic from question or concept
        topic = concept_name or "this concept"
        
        # Determine the type of error based on answer similarity
        user_lower = user_answer.strip().lower()
        correct_lower = correct_answer.strip().lower()
        
        # Check for common error types
        if len(user_lower) < 10 and len(correct_lower) < 10:
            # Short answers - likely confusion between similar terms
            pattern_type = f"term_confusion_{topic.lower().replace(' ', '_')[:20]}"
            description = f"Mixed up terminology related to {topic}"
            intervention = f"Review the definitions and differences in {topic}"
        elif any(word in user_lower for word in correct_lower.split()[:3]):
            # Partial match - incomplete understanding
            pattern_type = "incomplete_understanding"
            description = f"Incomplete understanding of {topic}"
            intervention = f"Study {topic} more thoroughly - you have partial knowledge but missed key details"
        else:
            # Very different answer
            pattern_type = f"misconception_{topic.lower().replace(' ', '_')[:20]}"
            description = f"Misconception about {topic}"
            intervention = f"Review {topic} from the beginning - your understanding may need correction"
        
        return {
            "pattern_type": pattern_type,
            "description": description,
            "score": 0.5,
            "intervention": intervention,
            "concept_area": topic
        }
    
    async def summarize_patterns(
        self,
        patterns: List[Dict],
        course_name: str = None
    ) -> Dict:
        """
        Summarize multiple confusion patterns into actionable insights.
        
        Args:
            patterns: List of confusion patterns
            course_name: Name of the course
            
        Returns:
            Summary with recommendations
        """
        if not patterns:
            return {
                "total_errors": 0,
                "main_issues": [],
                "recommendations": ["Keep up the good work!"]
            }
        
        # Group patterns by type
        pattern_counts = {}
        for p in patterns:
            ptype = p.get("pattern_type", "unknown")
            pattern_counts[ptype] = pattern_counts.get(ptype, 0) + 1
        
        # Sort by frequency
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: -x[1])
        
        main_issues = []
        recommendations = []
        
        for ptype, count in sorted_patterns[:3]:
            main_issues.append({
                "pattern": ptype.replace("_", " ").title(),
                "occurrences": count
            })
            # Find an intervention for this pattern
            for p in patterns:
                if p.get("pattern_type") == ptype:
                    recommendations.append(p.get("intervention", "Review this area"))
                    break
        
        return {
            "total_errors": len(patterns),
            "course": course_name,
            "main_issues": main_issues,
            "recommendations": list(set(recommendations))[:5],
            "improvement_areas": [p["pattern"].replace("_", " ") for p, _ in sorted_patterns[:3]]
        }
