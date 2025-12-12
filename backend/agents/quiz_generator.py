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
        Generate quiz questions from concepts using RAG for context.
        
        Args:
            concepts: List of concept dictionaries
            num_questions: Number of questions to generate
            difficulty: Difficulty level
            question_types: Types of questions
            course_id: Course ID for RAG context retrieval
        
        Returns:
            List of question dictionaries
        """
        self._log_action("Generating questions with RAG", {
            "num_questions": num_questions,
            "difficulty": difficulty,
            "num_concepts": len(concepts),
            "course_id": course_id
        })
        
        if not question_types:
            question_types = ["mcq"]  # Force MCQ only for quality quiz experience
        
        questions = []
        
        # Get vector store for RAG context
        from core.vector_store import get_vector_store
        vector_store = get_vector_store()
        
        # Build rich context for each concept using RAG
        enriched_concepts = []
        for concept in concepts[:num_questions * 2]:
            concept_name = concept.get("name", "")
            concept_def = concept.get("definition", "")
            
            # Retrieve relevant content from vector store - get more context for better questions
            rag_context = ""
            if course_id and concept_name:
                try:
                    chunks = vector_store.search(
                        course_id=course_id,
                        query=f"{concept_name} {concept_def}",
                        top_k=5  # Increased from 2 to get more context
                    )
                    if chunks:
                        # Get more text per chunk for richer context
                        rag_context = "\n\n".join([c.get("text", "")[:800] for c in chunks])
                except Exception as e:
                    logger.warning(f"RAG retrieval failed for concept {concept_name}: {e}")
            
            enriched_concepts.append({
                **concept,
                "rag_context": rag_context
            })
        
        # Try LLM generation with enriched context
        try:
            llm_questions = await self._generate_with_rag_context(
                enriched_concepts=enriched_concepts,
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
        
        # Fallback: Use standard LLM generation without RAG (but still better than templates)
        if len(questions) < num_questions:
            try:
                fallback_questions = await self.llm.generate_quiz_questions(
                    concepts=enriched_concepts[:num_questions - len(questions)],  # Use enriched concepts
                    num_questions=num_questions - len(questions),
                    difficulty=difficulty,
                    question_types=question_types
                )
                if fallback_questions:
                    questions.extend(fallback_questions)
            except Exception as e:
                logger.warning(f"Fallback question generation also failed: {e}")
        
        self._log_action("Questions generated", {"count": len(questions)})
        
        return questions[:num_questions]
    
    async def _generate_with_rag_context(
        self,
        enriched_concepts: List[Dict[str, Any]],
        num_questions: int,
        difficulty: str,
        question_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate MCQ questions using RAG-enriched concept context."""
        
        # Build detailed concept context with more source material
        concepts_text = ""
        for i, c in enumerate(enriched_concepts[:20]):
            concepts_text += f"\n\n### Topic {i+1}: {c.get('name', 'Unknown')}\n"
            if c.get('definition'):
                concepts_text += f"Definition: {c.get('definition')}\n"
            if c.get('rag_context'):
                concepts_text += f"Detailed Content from PDF:\n{c.get('rag_context')}\n"
        
        prompt = f"""You are an expert professor creating a multiple-choice quiz for university students.

Based on the following course content extracted from uploaded PDFs, generate {num_questions} HIGH-QUALITY multiple choice questions.

{concepts_text}

═══════════════════════════════════════════════════════════════════════════════
STRICT REQUIREMENTS FOR MCQ QUESTIONS:
═══════════════════════════════════════════════════════════════════════════════

1. QUESTION QUALITY:
   - Each question MUST test understanding of SPECIFIC content from the PDFs above
   - Questions must be CLEAR, UNAMBIGUOUS, and have ONE definitively correct answer
   - Test APPLICATION and COMPREHENSION, not just memorization
   - Reference specific concepts, formulas, processes, or examples from the content

2. OPTIONS (A, B, C, D):
   - Provide EXACTLY 4 options for each question
   - One option must be clearly correct
   - Three distractors must be PLAUSIBLE but incorrect
   - Distractors should be related concepts, common misconceptions, or partial truths
   - Options should be similar in length and format
   - AVOID obviously wrong answers like "None of the above" or joke answers

3. DIFFICULTY LEVEL: {difficulty.upper()}
   - Easy: Direct recall from the source material
   - Medium: Requires understanding and connecting concepts
   - Hard: Requires analysis, application, or comparing multiple concepts

4. FORBIDDEN QUESTION PATTERNS:
   ✗ "What is [term]?" - too generic
   ✗ "Define [concept]" - tests memorization only
   ✗ Questions about things NOT in the source material
   ✗ Vague or ambiguous questions
   ✗ Questions with multiple correct answers

5. EXCELLENT QUESTION EXAMPLES:
   ✓ "Which of the following correctly describes the relationship between X and Y according to the course material?"
   ✓ "In the context of [specific topic], what happens when [specific condition]?"
   ✓ "Based on the lecture content, which statement about [concept] is TRUE?"
   ✓ "What is the PRIMARY advantage of using [method A] over [method B] for [specific task]?"

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT - Return ONLY this JSON array, nothing else:
═══════════════════════════════════════════════════════════════════════════════

[
  {{
    "question_text": "Your clear, specific question here?",
    "question_type": "mcq",
    "difficulty": "{difficulty}",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_answer": "The exact text of the correct option",
    "explanation": "Detailed explanation of why this answer is correct, referencing the source material",
    "concept_name": "Main concept being tested"
  }}
]

Generate exactly {num_questions} questions. Each must be unique and test different aspects of the material.
RETURN ONLY THE JSON ARRAY:"""

        response = await self.llm.generate(prompt, temperature=0.6)
        
        try:
            import re
            # Try to extract JSON array
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                import json
                questions = json.loads(json_match.group())
                
                # Validate and fix questions
                validated_questions = []
                for q in questions[:num_questions]:
                    # Ensure it's MCQ type
                    q['question_type'] = 'mcq'
                    
                    # Ensure exactly 4 options
                    if q.get('options') and len(q['options']) >= 4:
                        q['options'] = q['options'][:4]
                        
                        # Ensure correct_answer matches one of the options
                        if q.get('correct_answer') not in q['options']:
                            # Try to find the closest match
                            q['correct_answer'] = q['options'][0]
                        
                        validated_questions.append(q)
                
                return validated_questions
        except Exception as e:
            logger.warning(f"Failed to parse RAG questions JSON: {e}")
        
        return []
    
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
        # CRITICAL CAUTION: Template questions often produce low-quality output 
        # (e.g. "What is Changing?") if concepts are not perfect.
        # It is better to return fewer questions than bad ones.
        return []

        # DISABLED OLD LOGIC:
        # questions = []
        # templates = self._get_question_templates()
        # ...
    
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

    def generate_fallback_question(
        self,
        concept: Dict[str, Any],
        question_type: str = "mcq"
    ) -> Dict[str, Any]:
        """Generate a fallback question without LLM."""
        templates = self._get_question_templates()
        
        if question_type == "mcq":
            return self._generate_mcq(concept, templates, "medium")
        elif question_type == "true_false":
            return self._generate_true_false(concept, templates, "medium")
        else:
            return self._generate_short_answer(concept, templates, "medium")

