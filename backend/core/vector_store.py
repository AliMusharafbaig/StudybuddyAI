"""
StudyBuddy AI - Vector Store
==============================
FAISS-based vector storage for RAG retrieval.
"""

import faiss
import numpy as np
import os
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

from core.config import settings
from core.embeddings import get_embedding_service

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a stored chunk."""
    chunk_id: str
    course_id: str
    material_id: str
    text: str
    source: str  # filename
    page: Optional[int] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    importance_score: float = 0.5
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


class VectorStore:
    """
    FAISS-based vector store for semantic search.
    
    Features:
    - Per-course indices for isolation
    - Metadata storage alongside vectors
    - Persistent storage to disk
    - Fast similarity search
    """
    
    def __init__(self, index_dir: str = None):
        """
        Initialize vector store.
        
        Args:
            index_dir: Directory for storing indices
        """
        self.index_dir = index_dir or settings.faiss_index_dir
        os.makedirs(self.index_dir, exist_ok=True)
        
        self.embedding_service = get_embedding_service()
        self.dimension = self.embedding_service.dimension
        
        # Cache for loaded indices
        self._indices: Dict[str, faiss.Index] = {}
        self._metadata: Dict[str, List[ChunkMetadata]] = {}
        
        logger.info(f"VectorStore initialized. Dimension: {self.dimension}")
    
    def _get_index_path(self, course_id: str) -> Tuple[str, str]:
        """Get paths for index and metadata files."""
        index_path = os.path.join(self.index_dir, f"{course_id}.faiss")
        metadata_path = os.path.join(self.index_dir, f"{course_id}.meta.json")
        return index_path, metadata_path
    
    def _load_index(self, course_id: str) -> Tuple[Optional[faiss.Index], List[ChunkMetadata]]:
        """Load index and metadata from disk."""
        index_path, metadata_path = self._get_index_path(course_id)
        
        index = None
        metadata = []
        
        if os.path.exists(index_path):
            try:
                index = faiss.read_index(index_path)
                logger.debug(f"Loaded FAISS index for course {course_id}")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    data = json.load(f)
                    metadata = [ChunkMetadata(**m) for m in data]
                logger.debug(f"Loaded {len(metadata)} metadata entries for course {course_id}")
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
        
        return index, metadata
    
    def _save_index(self, course_id: str) -> None:
        """Save index and metadata to disk."""
        if course_id not in self._indices:
            return
        
        index_path, metadata_path = self._get_index_path(course_id)
        
        try:
            faiss.write_index(self._indices[course_id], index_path)
            
            with open(metadata_path, 'w') as f:
                json.dump([asdict(m) for m in self._metadata.get(course_id, [])], f)
            
            logger.debug(f"Saved index for course {course_id}")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def _get_or_create_index(self, course_id: str) -> faiss.Index:
        """Get existing index or create new one."""
        if course_id in self._indices:
            return self._indices[course_id]
        
        # Try to load from disk
        index, metadata = self._load_index(course_id)
        
        if index is None:
            # Create new index
            index = faiss.IndexFlatL2(self.dimension)
            metadata = []
            logger.info(f"Created new FAISS index for course {course_id}")
        
        self._indices[course_id] = index
        self._metadata[course_id] = metadata
        
        return index
    
    def add_chunks(
        self,
        course_id: str,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """
        Add chunks to the vector store.
        
        Args:
            course_id: Course ID for the index
            chunks: List of chunks with text and metadata
        
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        index = self._get_or_create_index(course_id)
        
        # Extract texts and generate embeddings
        texts = [c.get("text", "") for c in chunks]
        embeddings = self.embedding_service.embed(texts)
        
        # Add to index
        index.add(embeddings)
        
        # Store metadata
        for i, chunk in enumerate(chunks):
            metadata = ChunkMetadata(
                chunk_id=chunk.get("chunk_id", f"{course_id}_{index.ntotal - len(chunks) + i}"),
                course_id=course_id,
                material_id=chunk.get("material_id", ""),
                text=chunk.get("text", ""),
                source=chunk.get("source", "Unknown"),
                page=chunk.get("page"),
                start_char=chunk.get("start_char"),
                end_char=chunk.get("end_char"),
                importance_score=chunk.get("importance_score", 0.5)
            )
            self._metadata[course_id].append(metadata)
        
        # Save to disk
        self._save_index(course_id)
        
        logger.info(f"Added {len(chunks)} chunks to course {course_id}")
        return len(chunks)
    
    def search(
        self,
        course_id: str,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            course_id: Course ID to search in
            query: Query text
            top_k: Number of results to return
        
        Returns:
            List of matching chunks with scores
        """
        index = self._get_or_create_index(course_id)
        
        if index.ntotal == 0:
            logger.warning(f"Empty index for course {course_id}")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed(query)
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Search
        k = min(top_k, index.ntotal)
        distances, indices = index.search(query_embedding, k)
        
        # Build results with metadata
        results = []
        metadata_list = self._metadata.get(course_id, [])
        
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0 or idx >= len(metadata_list):
                continue
            
            meta = metadata_list[idx]
            
            # Convert L2 distance to similarity score (0-1)
            score = 1.0 / (1.0 + dist)
            
            results.append({
                "chunk_id": meta.chunk_id,
                "text": meta.text,
                "source": meta.source,
                "page": meta.page,
                "score": float(score),
                "material_id": meta.material_id,
                "importance_score": meta.importance_score
            })
        
        logger.debug(f"Found {len(results)} results for query in course {course_id}")
        return results
    
    async def search_async(
        self,
        course_id: str,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Async version of search."""
        return await asyncio.to_thread(self.search, course_id, query, top_k)
    
    def delete_course_index(self, course_id: str) -> bool:
        """
        Delete all data for a course.
        
        Args:
            course_id: Course ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        # Remove from cache
        if course_id in self._indices:
            del self._indices[course_id]
        if course_id in self._metadata:
            del self._metadata[course_id]
        
        # Remove files
        index_path, metadata_path = self._get_index_path(course_id)
        
        deleted = False
        for path in [index_path, metadata_path]:
            if os.path.exists(path):
                os.remove(path)
                deleted = True
        
        if deleted:
            logger.info(f"Deleted index for course {course_id}")
        
        return deleted
    
    def get_stats(self, course_id: str) -> Dict[str, Any]:
        """
        Get statistics for a course index.
        
        Args:
            course_id: Course ID
        
        Returns:
            Dictionary with stats
        """
        index = self._get_or_create_index(course_id)
        metadata = self._metadata.get(course_id, [])
        
        return {
            "course_id": course_id,
            "total_chunks": index.ntotal,
            "dimension": self.dimension,
            "unique_materials": len(set(m.material_id for m in metadata)),
            "avg_importance": sum(m.importance_score for m in metadata) / max(len(metadata), 1)
        }


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
