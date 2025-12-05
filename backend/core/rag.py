"""
StudyBuddy AI - RAG System
===========================
Retrieval-Augmented Generation pipeline.
"""

from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass

from core.vector_store import get_vector_store, VectorStore
from core.llm import get_llm, GeminiLLM
from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """Result from a RAG query."""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float


class RAGSystem:
    """
    Retrieval-Augmented Generation system.
    
    Pipeline:
    1. Query → Embedding
    2. Vector Search → Relevant Chunks
    3. Reranking → Top Chunks
    4. Context Assembly → LLM Prompt
    5. Generation → Answer
    """
    
    def __init__(self):
        """Initialize RAG system components."""
        self.vector_store = get_vector_store()
        self.llm = get_llm()
        
        logger.info("RAG System initialized")
    
    async def query(
        self,
        query: str,
        course_id: str,
        top_k: int = None,
        rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query
            course_id: Course to search in
            top_k: Number of results (default from settings)
            rerank: Whether to rerank results
        
        Returns:
            List of relevant chunks
        """
        if top_k is None:
            top_k = settings.max_chunks_per_query
        
        # Search vector store
        results = await self.vector_store.search_async(
            course_id=course_id,
            query=query,
            top_k=top_k * 2 if rerank else top_k  # Get more for reranking
        )
        
        if not results:
            return []
        
        if rerank:
            results = self._rerank(query, results, top_k)
        
        return results[:top_k]
    
    def _rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Rerank chunks based on multiple factors.
        
        Factors:
        - Semantic similarity (from vector search)
        - Importance score
        - Source recency
        """
        for chunk in chunks:
            # Base score from vector search
            score = chunk.get("score", 0.5)
            
            # Boost by importance
            importance = chunk.get("importance_score", 0.5)
            score *= (0.5 + importance * 0.5)
            
            # Update score
            chunk["rerank_score"] = score
        
        # Sort by rerank score
        chunks.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        
        return chunks[:top_k]
    
    async def generate_answer(
        self,
        query: str,
        course_id: str,
        top_k: int = None,
        include_sources: bool = True
    ) -> RAGResult:
        """
        Generate an answer using RAG.
        
        Args:
            query: User query
            course_id: Course context
            top_k: Number of chunks to use
            include_sources: Whether to include source citations
        
        Returns:
            RAGResult with answer and sources
        """
        # Retrieve relevant chunks
        chunks = await self.query(query, course_id, top_k)
        
        if not chunks:
            return RAGResult(
                answer="I couldn't find relevant information in your course materials. Try rephrasing your question or make sure you've uploaded relevant materials.",
                sources=[],
                confidence=0.0
            )
        
        # Build context
        context = self._build_context(chunks)
        
        # Generate answer
        prompt = f"""Use the following context from course materials to answer the question.
If the answer is not in the context, say so and provide what you know.

CONTEXT:
{context}

QUESTION: {query}

Provide a clear, helpful answer. Cite sources when relevant."""

        answer = await self.llm.generate(prompt, temperature=0.3)
        
        # Calculate confidence based on top scores
        avg_score = sum(c.get("score", 0) for c in chunks[:3]) / min(len(chunks), 3)
        confidence = min(avg_score * 1.2, 1.0)  # Scale up but cap at 1
        
        sources = []
        if include_sources:
            sources = [
                {
                    "source": c.get("source", "Unknown"),
                    "page": c.get("page"),
                    "score": round(c.get("score", 0), 3)
                }
                for c in chunks[:5]
            ]
        
        return RAGResult(
            answer=answer,
            sources=sources,
            confidence=confidence
        )
    
    def _build_context(self, chunks: List[Dict[str, Any]], max_tokens: int = 4000) -> str:
        """
        Build context string from chunks.
        
        Args:
            chunks: Retrieved chunks
            max_tokens: Approximate max tokens (4 chars per token)
        
        Returns:
            Context string
        """
        context_parts = []
        current_length = 0
        max_chars = max_tokens * 4
        
        for chunk in chunks:
            text = chunk.get("text", "")
            source = chunk.get("source", "Unknown")
            page = chunk.get("page", "")
            
            # Format chunk
            formatted = f"[Source: {source}"
            if page:
                formatted += f", Page {page}"
            formatted += f"]\n{text}\n---"
            
            if current_length + len(formatted) > max_chars:
                break
            
            context_parts.append(formatted)
            current_length += len(formatted)
        
        return "\n".join(context_parts)
    
    async def add_documents(
        self,
        course_id: str,
        documents: List[Dict[str, Any]]
    ) -> int:
        """
        Add documents to the RAG system.
        
        Args:
            course_id: Course ID
            documents: List of document dicts with text and metadata
        
        Returns:
            Number of chunks added
        """
        return self.vector_store.add_chunks(course_id, documents)
    
    def delete_course_data(self, course_id: str) -> bool:
        """Delete all RAG data for a course."""
        return self.vector_store.delete_course_index(course_id)


# Singleton
_rag_system: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """Get the RAG system singleton."""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system
