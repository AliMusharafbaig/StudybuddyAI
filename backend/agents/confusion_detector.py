"""
StudyBuddy AI - Confusion Detector Agent
==========================================
Detects learning confusion patterns from student responses.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import re

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Common confusion patterns
CONFUSION_PATTERNS = {
    "overfitting_underfitting": {
        "id": "P001",
        "description": "Confuses overfitting with underfitting",
        "triggers": ["high variance", "low variance", "high bias"],
        "intervention": "Overfitting = too complex. Underfitting = too simple."
    },
    "supervised_unsupervised": {
        "id": "P002", 
        "description": "Confuses supervised and unsupervised learning",
        "triggers": ["labeled", "unlabeled", "classification"],
        "intervention": "Supervised = labeled data. Unsupervised = no labels."
    },
    "precision_recall": {
        "id": "P003",
        "description": "Confuses precision and recall",
        "triggers": ["true positive", "false positive"],
        "intervention": "Precision = TP/(TP+FP). Recall = TP/(TP+FN)."
    }
}


class ConfusionDetectorAgent(BaseAgent):
    """Agent for detecting student confusion patterns."""
    
    def __init__(self):
        super().__init__("ConfusionDetectorAgent")
        self.patterns = CONFUSION_PATTERNS
    
    async def run(self, question: str, user_answer: str, correct_answer: str, concept_id: str = None) -> Optional[Dict]:
        return await self.detect_confusion(question, user_answer, correct_answer, concept_id)
    
    async def detect_confusion(self, question: str, user_answer: str, correct_answer: str, concept_id: str = None) -> Optional[Dict]:
        if user_answer.strip().lower() == correct_answer.strip().lower():
            return None
        
        # Pattern matching
        combined = f"{question} {user_answer} {correct_answer}".lower()
        
        for key, pattern in self.patterns.items():
            if any(t in combined for t in pattern["triggers"]):
                return {
                    "pattern_type": key,
                    "description": pattern["description"],
                    "score": 0.7,
                    "intervention": pattern["intervention"]
                }
        
        return {"pattern_type": "generic_error", "description": "Incorrect answer", "score": 0.3, "intervention": "Review this concept."}
