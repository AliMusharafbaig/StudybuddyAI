"""
StudyBuddy AI - Embeddings Service
====================================
Text embedding generation for RAG system.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging
from functools import lru_cache
import asyncio

from core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Text embedding service using sentence-transformers.
    
    Supports local models for fast, free embeddings.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Model name from HuggingFace or local path
        """
        self.model_name = model_name or settings.embedding_model
        self.dimension = settings.embedding_dimension
        
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text or list of texts
        
        Returns:
            Numpy array of embeddings (shape: [n_texts, dimension])
        """
        if self.model is None:
            logger.warning("Embedding model not available, returning random embeddings")
            if isinstance(texts, str):
                return np.random.randn(self.dimension).astype(np.float32)
            return np.random.randn(len(texts), self.dimension).astype(np.float32)
        
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return np.random.randn(len(texts), self.dimension).astype(np.float32)
    
    async def embed_async(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Async version of embed.
        
        Args:
            texts: Single text or list of texts
        
        Returns:
            Numpy array of embeddings
        """
        return await asyncio.to_thread(self.embed, texts)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a search query.
        
        Args:
            query: Query text
        
        Returns:
            Query embedding vector
        """
        return self.embed(query)[0] if len(self.embed(query).shape) > 1 else self.embed(query)
    
    def similarity(self, query_embedding: np.ndarray, document_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and documents.
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: Document embedding matrix
        
        Returns:
            Similarity scores
        """
        # Normalize if not already
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        doc_norms = document_embeddings / (np.linalg.norm(document_embeddings, axis=1, keepdims=True) + 1e-9)
        
        # Cosine similarity
        similarities = np.dot(doc_norms, query_norm)
        return similarities


# Singleton instance
@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Get the embedding service singleton."""
    return EmbeddingService()


# Convenience functions
def embed_texts(texts: Union[str, List[str]]) -> np.ndarray:
    """Embed texts using the default service."""
    return get_embedding_service().embed(texts)


async def embed_texts_async(texts: Union[str, List[str]]) -> np.ndarray:
    """Async embed texts using the default service."""
    return await get_embedding_service().embed_async(texts)
