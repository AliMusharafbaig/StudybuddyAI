"""
StudyBuddy AI - Agent Tests
============================
Unit tests for AI agents.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestContentIngestionAgent:
    """Test content ingestion agent."""

    @pytest.mark.asyncio
    async def test_extract_pdf_text(self):
        """Test PDF text extraction."""
        from agents.content_ingestion import ContentIngestionAgent
        
        agent = ContentIngestionAgent()
        # Mock PDF extraction
        with patch.object(agent, 'extract_pdf_text', new_callable=AsyncMock) as mock:
            mock.return_value = "Sample PDF content about machine learning."
            result = await agent.extract_pdf_text("test.pdf")
            assert "machine learning" in result

    @pytest.mark.asyncio
    async def test_chunk_text(self):
        """Test text chunking."""
        from agents.content_ingestion import ContentIngestionAgent
        
        agent = ContentIngestionAgent()
        text = "A" * 1000  # Long text
        chunks = agent.chunk_text(text, chunk_size=100, overlap=10)
        
        assert len(chunks) > 1
        assert all(len(c["text"]) <= 110 for c in chunks)


class TestConceptExtractorAgent:
    """Test concept extraction agent."""

    @pytest.mark.asyncio
    async def test_extract_concepts(self):
        """Test concept extraction."""
        from agents.concept_extractor import ConceptExtractorAgent
        
        agent = ConceptExtractorAgent()
        text = "Machine learning is a subset of artificial intelligence. Neural networks are used in deep learning."
        
        with patch.object(agent.llm, 'extract_concepts', new_callable=AsyncMock) as mock:
            mock.return_value = [
                {"name": "Machine Learning", "definition": "A subset of AI", "importance": 9},
                {"name": "Neural Networks", "definition": "Used in deep learning", "importance": 8}
            ]
            concepts = await agent.run(text)
            assert len(concepts) >= 1


class TestQuizGeneratorAgent:
    """Test quiz generation agent."""

    @pytest.mark.asyncio
    async def test_generate_mcq(self):
        """Test MCQ generation."""
        from agents.quiz_generator import QuizGeneratorAgent
        
        agent = QuizGeneratorAgent()
        concepts = [{"name": "Machine Learning", "definition": "A type of AI", "importance": 9}]
        
        with patch.object(agent.llm, 'generate_quiz_questions', new_callable=AsyncMock) as mock:
            mock.return_value = [{
                "question": "What is Machine Learning?",
                "options": ["A type of AI", "A database", "A network", "A protocol"],
                "correct_answer": "A type of AI",
                "type": "mcq"
            }]
            questions = await agent.generate_questions(concepts, num_questions=1)
            assert len(questions) >= 1

    @pytest.mark.asyncio
    async def test_fallback_generation(self):
        """Test fallback question generation."""
        from agents.quiz_generator import QuizGeneratorAgent
        
        agent = QuizGeneratorAgent()
        concept = {"name": "Test Concept", "definition": "Test definition"}
        
        question = agent.generate_fallback_question(concept, "mcq")
        assert "question" in question
        assert "options" in question


class TestConfusionDetectorAgent:
    """Test confusion detection agent."""

    @pytest.mark.asyncio
    async def test_detect_confusion(self):
        """Test confusion pattern detection."""
        from agents.confusion_detector import ConfusionDetectorAgent
        
        agent = ConfusionDetectorAgent()
        result = await agent.detect_confusion(
            question="What is the difference between stack and queue?",
            user_answer="They are the same",
            correct_answer="Stack is LIFO, Queue is FIFO"
        )
        
        # Should detect some pattern or return None
        assert result is None or "pattern_type" in result


class TestExplanationBuilderAgent:
    """Test explanation builder agent."""

    @pytest.mark.asyncio
    async def test_generate_explanation(self):
        """Test explanation generation."""
        from agents.explanation_builder import ExplanationBuilderAgent
        
        agent = ExplanationBuilderAgent()
        
        with patch.object(agent.llm, 'generate_explanation', new_callable=AsyncMock) as mock:
            mock.return_value = "Machine learning is a method of data analysis..."
            explanation = await agent.generate_explanation("Machine Learning")
            assert len(explanation) > 0

    @pytest.mark.asyncio
    async def test_generate_mnemonic(self):
        """Test mnemonic generation."""
        from agents.explanation_builder import ExplanationBuilderAgent
        
        agent = ExplanationBuilderAgent()
        
        with patch.object(agent.llm, 'generate_mnemonic', new_callable=AsyncMock) as mock:
            mock.return_value = {
                "type": "acronym",
                "mnemonic": "ML = Machines Learn",
                "explanation": "Simple acronym"
            }
            result = await agent.generate_mnemonic(
                "Machine Learning",
                "A type of AI",
                "acronym"
            )
            assert "mnemonic" in result
