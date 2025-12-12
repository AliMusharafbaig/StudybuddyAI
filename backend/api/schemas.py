"""
StudyBuddy AI - Pydantic Schemas
=================================
Request/Response models for API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ============================================
# Enums
# ============================================

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADAPTIVE = "adaptive"


class QuestionType(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    PROBLEM_SOLVING = "problem_solving"


class QuizStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================
# Auth Schemas
# ============================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    preferred_difficulty: str = "medium"
    daily_study_goal_minutes: int = 30
    total_study_time_minutes: int = 0
    total_quizzes_completed: int = 0
    current_streak_days: int = 0
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================
# Course Schemas
# ============================================

class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    code: Optional[str] = Field(None, max_length=50)
    instructor: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field("#6366F1", pattern=r"^#[0-9A-Fa-f]{6}$")


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    code: Optional[str] = Field(None, max_length=50)
    instructor: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: Optional[str] = None
    code: Optional[str] = None
    instructor: Optional[str] = None
    color: str = "#6366F1"
    is_processed: bool = False
    processing_progress: int = 0
    total_concepts: int = 0
    total_materials: int = 0
    mastery_percentage: int = 0
    created_at: datetime


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    is_processed: bool = False
    processing_status: str = "pending"
    num_pages: Optional[int] = None
    duration_seconds: Optional[int] = None
    created_at: datetime


# ============================================
# Concept Schemas
# ============================================

class ConceptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    definition: Optional[str] = None
    category: Optional[str] = None
    importance_score: int = 5
    difficulty: str = "medium"
    exam_probability: float = 0.5
    mastery_level: int = 0
    times_reviewed: int = 0
    times_correct: int = 0
    times_incorrect: int = 0
    created_at: datetime


class ConceptRelationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    source_concept_id: str
    target_concept_id: str
    relation_type: str
    strength: float = 1.0


class KnowledgeGraphResponse(BaseModel):
    concepts: List[ConceptResponse]
    relations: List[ConceptRelationResponse]


# ============================================
# Quiz Schemas
# ============================================

class QuizCreate(BaseModel):
    course_id: str
    title: Optional[str] = None
    quiz_type: str = "practice"
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    num_questions: int = Field(10, ge=1, le=50)
    topics: Optional[List[str]] = None  # Specific concepts to focus on
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=180)


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    question_text: str
    question_type: str
    difficulty: str = "medium"
    options: Optional[List[str]] = None
    question_order: int = 0
    # Note: correct_answer and explanation hidden until answered
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None


class QuestionAnswerRequest(BaseModel):
    answer: str
    time_taken_seconds: Optional[int] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=5)


class QuestionAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    confusion_detected: bool = False
    confusion_pattern: Optional[str] = None
    intervention_message: Optional[str] = None


class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: Optional[str] = None
    quiz_type: str = "practice"
    difficulty: str = "medium"
    total_questions: int = 0
    answered_questions: int = 0
    correct_answers: int = 0
    score: Optional[float] = None
    status: str = "in_progress"
    time_limit_seconds: Optional[int] = None
    time_spent_seconds: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None


class QuizWithQuestionsResponse(QuizResponse):
    questions: List[QuestionResponse] = []


class QuizResultsResponse(BaseModel):
    quiz: QuizResponse
    questions: List[QuestionResponse]
    confusion_patterns: List[str] = []
    recommendations: List[str] = []
    concepts_to_review: List[str] = []


# ============================================
# Analytics Schemas
# ============================================

class StudyProgressResponse(BaseModel):
    total_study_time_minutes: int = 0
    total_quizzes_completed: int = 0
    current_streak_days: int = 0
    average_score: float = 0.0
    concepts_mastered: int = 0
    concepts_learning: int = 0
    concepts_weak: int = 0
    recent_activity: List[dict] = []
    score_history: List[dict] = []


class ConceptMasteryResponse(BaseModel):
    concept_id: str
    concept_name: str
    mastery_level: int
    times_reviewed: int
    accuracy_rate: float
    last_reviewed: Optional[datetime] = None


class ConfusionAnalysisResponse(BaseModel):
    pattern_type: str
    description: str
    confusion_score: float
    trigger_count: int
    affected_concepts: List[str] = []
    recommended_action: str
    # Simple display fields (what the user wants)
    user_answer: Optional[str] = None  # What user answered
    correct_answer: Optional[str] = None  # What was correct
    course_name: Optional[str] = None  # Course name
    topic_name: Optional[str] = None  # Topic/concept name


# ============================================
# Exam Prediction Schemas
# ============================================

class ExamPredictionRequest(BaseModel):
    course_id: str
    num_predictions: int = Field(10, ge=1, le=30)
    include_solutions: bool = False


class ExamQuestionResponse(BaseModel):
    question_text: str
    question_type: str = "problem_solving"
    exam_probability: int = Field(..., ge=0, le=100)
    difficulty: str = "medium"
    concept_name: str
    solution: Optional[str] = None


class ExamPredictionDetailResponse(BaseModel):
    id: str
    course_id: str
    predicted_questions: List[ExamQuestionResponse]
    created_at: datetime


# Legacy schemas (kept for compatibility)
class ExamPredictionResponseLegacy(BaseModel):
    topic: str
    probability: float  # 0-1
    importance: int  # 1-10
    recommended_study_time_minutes: int
    sample_questions: List[str] = []


class ExamPredictionsResponseLegacy(BaseModel):
    course_id: str
    predictions: List[ExamPredictionResponseLegacy]
    overall_readiness: float  # 0-100
    recommended_focus_areas: List[str] = []


# Aliases for backward compatibility with analytics.py imports
ExamPredictionsResponse = ExamPredictionsResponseLegacy
ExamPredictionResponse = ExamPredictionResponseLegacy


# ============================================
# Cram Mode Schemas
# ============================================

class CramPlanRequest(BaseModel):
    course_id: str
    hours_available: float = Field(..., ge=0.5, le=24)
    focus_topics: Optional[List[str]] = None


class CramTopicPlan(BaseModel):
    topic: str
    allocated_minutes: int
    priority: int  # 1-10
    key_points: List[str] = []
    quick_review_notes: str = ""


class CramPlanResponse(BaseModel):
    id: str
    course_id: str
    total_minutes: int
    topics: List[CramTopicPlan]
    cheat_sheet: str = ""
    high_priority_concepts: List[str] = []
    skip_topics: List[str] = []
    created_at: datetime


# ============================================
# Mnemonic Schemas
# ============================================

class MnemonicRequest(BaseModel):
    concept_id: str
    mnemonic_type: Optional[str] = None  # acronym, rhyme, story, visual


class MnemonicResponse(BaseModel):
    concept_id: str
    concept_name: str
    mnemonic_type: str
    mnemonic_text: str
    explanation: str
    visual_cue: Optional[str] = None


# ============================================
# Chat Schemas
# ============================================

class ChatMessageRequest(BaseModel):
    message: str
    course_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: str
    role: str  # user or assistant
    content: str
    sources: List[dict] = []  # Citations from course materials
    timestamp: datetime
    conversation_id: Optional[str] = None


# ============================================
# Upload & Processing Schemas
# ============================================

class UploadResponse(BaseModel):
    material_id: str
    filename: str
    file_type: str
    file_size: int
    status: str = "pending"
    message: str = "File uploaded successfully. Processing will begin shortly."


class ProcessingStatusResponse(BaseModel):
    material_id: str
    status: ProcessingStatus
    progress: int = 0  # 0-100
    message: Optional[str] = None
    error: Optional[str] = None
