"""
StudyBuddy AI - Quiz Generator Agent
======================================
Generates personalized quiz questions using RAG.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import re
import random

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class QuizGeneratorAgent(BaseAgent):
    """
    Agent for generating personalized quiz questions.
    
    Features:
    - RAG-based question generation
    - Multiple question types (MCQ, T/F, short answer, problem-solving)
    - Adaptive difficulty
    - Distractor generation for MCQs
    - Professor style matching
    """
    
    def __init__(self):
        super().__init__("QuizGeneratorAgent")
    
    async def run(
        self,
        course_id: str,
        concepts: List[Dict[str, Any]] = None,
        num_questions: int = 10,
        difficulty: str = "medium",
        question_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a quiz for a course.
        
        Args:
            course_id: Course to generate quiz for
            concepts: Optional list of concepts to focus on
            num_questions: Number of questions
            difficulty: Question difficulty level
            question_types: Types of questions to include
        
        Returns:
            List of generated questions
        """
        return await self.generate_questions(
            concepts=concepts or [],
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=question_types
        )
    
    async def generate_questions(
        self,
        concepts: List[Dict[str, Any]],
        num_questions: int = 10,
        difficulty: str = "medium",
        question_types: List[str] = None,
        course_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from concepts.
        
        Args:
            concepts: List of concept dictionaries
            num_questions: Number of questions to generate
            difficulty: Difficulty level
            question_types: Types of questions
            course_id: Optional course ID for RAG context
        
        Returns:
            List of question dictionaries
        """
        self._log_action("Generating questions", {
            "num_questions": num_questions,
            "difficulty": difficulty,
            "num_concepts": len(concepts)
        })
        
        if not question_types:
            question_types = ["mcq", "true_false", "short_answer"]
        
        questions = []
        
        # Try LLM generation first
        try:
            llm_questions = await self.llm.generate_quiz_questions(
                concepts=concepts,
                num_questions=num_questions,
                difficulty=difficulty,
                question_types=question_types
            )
            
            if llm_questions:
                # Add concept IDs to questions
                for q in llm_questions:
                    concept_name = q.get("concept_name", "").lower()
                    for c in concepts:
                        if c.get("name", "").lower() == concept_name:
                            q["concept_id"] = c.get("id")
                            break
                
                questions = llm_questions
        except Exception as e:
            logger.warning(f"LLM question generation failed: {e}")
        
        # Fallback or supplement with template-based questions
        if len(questions) < num_questions:
            template_questions = self._generate_template_questions(
                concepts,
                num_questions - len(questions),
                difficulty,
                question_types
            )
            questions.extend(template_questions)
        
        self._log_action("Questions generated", {"count": len(questions)})
        
        return questions[:num_questions]
    
    def _generate_template_questions(
        self,
        concepts: List[Dict[str, Any]],
        num_questions: int,
        difficulty: str,
        question_types: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate questions using templates.
        
        Fallback when LLM is unavailable.
        """
        questions = []
        templates = self._get_question_templates()
        
        for i in range(min(num_questions, len(concepts))):
            concept = concepts[i % len(concepts)]
            q_type = random.choice(question_types)
            
            if q_type == "mcq":
                question = self._generate_mcq(concept, templates, difficulty)
            elif q_type == "true_false":
                question = self._generate_true_false(concept, templates, difficulty)
            else:
                question = self._generate_short_answer(concept, templates, difficulty)
            
            questions.append(question)
        
        return questions
    
    def _get_question_templates(self) -> Dict[str, List[str]]:
        """Get question templates by type."""
        return {
            "mcq": [
                "What is {concept}?",
                "Which of the following best describes {concept}?",
                "What is the primary function of {concept}?",
                "Which statement about {concept} is correct?",
            ],
            "true_false": [
                "{concept} is used for {definition}.",
                "{concept} is a type of {category}.",
                "{concept} requires {related} as a prerequisite.",
            ],
            "short_answer": [
                "Explain {concept} in your own words.",
                "What are the key characteristics of {concept}?",
                "Give an example of {concept} in practice.",
                "How does {concept} relate to {related}?",
            ],
            "problem_solving": [
                "Given a scenario involving {concept}, how would you apply it?",
                "Design a solution using {concept}.",
                "Analyze the following situation using {concept}.",
            ]
        }
    
    def _generate_mcq(
        self,
        concept: Dict[str, Any],
        templates: Dict[str, List[str]],
        difficulty: str
    ) -> Dict[str, Any]:
        """Generate a multiple choice question."""
        name = concept.get("name", "Unknown")
        definition = concept.get("definition", "A key concept")
        
        template = random.choice(templates["mcq"])
        question_text = template.format(
            concept=name,
            definition=definition,
            category=concept.get("category", "this field")
        )
        
        # Generate options
        correct = definition[:100] if len(definition) > 100 else definition
        distractors = self._generate_distractors(name, correct, 3)
        
        options = [correct] + distractors
        random.shuffle(options)
        
        return {
            "question_text": question_text,
            "question_type": "mcq",
            "difficulty": difficulty,
            "options": options,
            "correct_answer": correct,
            "explanation": f"{name}: {definition}",
            "concept_id": concept.get("id"),
            "concept_name": name
        }
    
    def _generate_true_false(
        self,
        concept: Dict[str, Any],
        templates: Dict[str, List[str]],
        difficulty: str
    ) -> Dict[str, Any]:
        """Generate a true/false question."""
        name = concept.get("name", "Unknown")
        definition = concept.get("definition", "A key concept")
        
        # Randomly make it true or false
        is_true = random.choice([True, False])
        
        if is_true:
            statement = f"{name} {definition[:50]}..." if len(definition) > 50 else f"{name} is {definition}."
        else:
            # Create a false statement
            statement = f"{name} is not related to {concept.get('category', 'this field')}."
        
        return {
            "question_text": f"True or False: {statement}",
            "question_type": "true_false",
            "difficulty": difficulty,
            "options": ["True", "False"],
            "correct_answer": "True" if is_true else "False",
            "explanation": f"The correct statement is: {name} - {definition}",
            "concept_id": concept.get("id"),
            "concept_name": name
        }
    
    def _generate_short_answer(
        self,
        concept: Dict[str, Any],
        templates: Dict[str, List[str]],
        difficulty: str
    ) -> Dict[str, Any]:
        """Generate a short answer question."""
        name = concept.get("name", "Unknown")
        definition = concept.get("definition", "A key concept")
        
        template = random.choice(templates["short_answer"])
        related = concept.get("related_concepts", "related concepts")
        
        question_text = template.format(
            concept=name,
            related=related
        )
        
        return {
            "question_text": question_text,
            "question_type": "short_answer",
            "difficulty": difficulty,
            "correct_answer": definition,
            "explanation": f"Key points about {name}: {definition}",
            "concept_id": concept.get("id"),
            "concept_name": name
        }
    
    def _generate_distractors(
        self,
        concept_name: str,
        correct_answer: str,
        num_distractors: int = 3
    ) -> List[str]:
        """
        Generate plausible wrong answers.
        
        Args:
            concept_name: The concept being tested
            correct_answer: The correct answer
            num_distractors: Number of distractors to generate
        
        Returns:
            List of distractor strings
        """
        distractors = [
            f"A method unrelated to {concept_name}",
            f"The opposite of {concept_name}",
            f"A common misconception about {concept_name}",
            f"An outdated definition of {concept_name}",
            f"A related but different concept",
        ]
        
        return random.sample(distractors, min(num_distractors, len(distractors)))
    
    async def generate_adaptive_question(
        self,
        concept: Dict[str, Any],
        user_history: List[Dict[str, Any]] = None,
        target_difficulty: str = None
    ) -> Dict[str, Any]:
        """
        Generate an adaptively difficult question.
        
        Args:
            concept: Target concept
            user_history: User's answer history for this concept
            target_difficulty: Override difficulty level
        
        Returns:
            Question dictionary
        """
        # Determine difficulty from history
        if user_history and not target_difficulty:
            correct_rate = sum(1 for h in user_history if h.get("is_correct")) / len(user_history)
            
            if correct_rate > 0.8:
                target_difficulty = "hard"
            elif correct_rate > 0.5:
                target_difficulty = "medium"
            else:
                target_difficulty = "easy"
        else:
            target_difficulty = target_difficulty or "medium"
        
        # Generate question at target difficulty
        questions = await self.generate_questions(
            concepts=[concept],
            num_questions=1,
            difficulty=target_difficulty,
            question_types=["mcq"]
        )
        
        return questions[0] if questions else None
