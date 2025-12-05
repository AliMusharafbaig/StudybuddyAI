"""
StudyBuddy AI - Concept Extractor Agent
=========================================
Extracts and organizes key concepts from course materials.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import re

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ConceptExtractorAgent(BaseAgent):
    """
    Agent for extracting key concepts from course materials.
    
    Features:
    - Identifies key concepts using LLM
    - Assigns importance scores
    - Detects concept relationships
    - Builds concept hierarchies
    """
    
    def __init__(self):
        super().__init__("ConceptExtractorAgent")
    
    async def run(
        self,
        text: str,
        course_name: str = None,
        max_concepts: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Extract concepts from text.
        
        Args:
            text: Source text to analyze
            course_name: Name of the course for context
            max_concepts: Maximum number of concepts to extract
        
        Returns:
            List of concept dictionaries
        """
        self._log_action("Extracting concepts", {
            "text_length": len(text),
            "max_concepts": max_concepts
        })
        
        concepts = await self.llm.extract_concepts(text, max_concepts)
        
        if not concepts:
            # Fallback: basic extraction
            concepts = self._basic_extraction(text, max_concepts)
        
        # Identify relationships between concepts
        if len(concepts) > 1:
            concepts = await self._identify_relationships(concepts)
        
        self._log_action("Concepts extracted", {"count": len(concepts)})
        
        return concepts
    
    async def extract_from_chunks(
        self,
        chunks: List[Dict[str, Any]],
        course_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Extract concepts from multiple text chunks.
        
        Args:
            chunks: List of text chunks
            course_name: Name of the course
        
        Returns:
            Deduplicated list of concepts
        """
        all_concepts = []
        seen_names = set()
        
        for chunk in chunks:
            text = chunk.get("text", "")
            if not text or len(text) < 100:
                continue
            
            concepts = await self.run(text, course_name, max_concepts=20)
            
            for concept in concepts:
                name = concept.get("name", "").lower().strip()
                if name and name not in seen_names:
                    seen_names.add(name)
                    concept["source_chunk_id"] = chunk.get("chunk_id")
                    all_concepts.append(concept)
        
        return all_concepts
    
    async def _identify_relationships(
        self,
        concepts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify relationships between concepts.
        
        Args:
            concepts: List of concepts
        
        Returns:
            Concepts with relationship info added
        """
        if len(concepts) < 2:
            return concepts
        
        # Create concept list for LLM
        concept_names = [c.get("name", "") for c in concepts[:30]]
        
        prompt = f"""Analyze these concepts and identify relationships between them.

CONCEPTS:
{json.dumps(concept_names, indent=2)}

For each pair of related concepts, output the relationship type:
- "prerequisite": concept A must be learned before concept B
- "related": concepts are related but neither is prerequisite
- "part_of": concept A is a subtopic of concept B

Return as JSON array:
[
  {{"from": "Concept A", "to": "Concept B", "type": "prerequisite"}},
  ...
]

Return ONLY the JSON array of relationships:"""

        try:
            response = await self.llm.generate(prompt, temperature=0.3)
            json_match = re.search(r'\[[\s\S]*\]', response)
            
            if json_match:
                relationships = json.loads(json_match.group())
                
                # Add relationships to concepts
                relation_map = {}
                for rel in relationships:
                    from_name = rel.get("from", "").lower()
                    to_name = rel.get("to", "").lower()
                    rel_type = rel.get("type", "related")
                    
                    if from_name not in relation_map:
                        relation_map[from_name] = {"prerequisites": [], "related": []}
                    
                    if rel_type == "prerequisite":
                        relation_map[from_name]["prerequisites"].append(to_name)
                    else:
                        relation_map[from_name]["related"].append(to_name)
                
                # Update concepts
                for concept in concepts:
                    name = concept.get("name", "").lower()
                    if name in relation_map:
                        concept["prerequisites"] = ",".join(relation_map[name].get("prerequisites", []))
                        concept["related_concepts"] = ",".join(relation_map[name].get("related", []))
                
        except Exception as e:
            logger.warning(f"Relationship extraction failed: {e}")
        
        return concepts
    
    def _basic_extraction(
        self,
        text: str,
        max_concepts: int
    ) -> List[Dict[str, Any]]:
        """
        Basic concept extraction without LLM.
        
        Uses keyword frequency and capitalization patterns.
        """
        import re
        from collections import Counter
        
        # Find capitalized phrases (likely concepts)
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        matches = re.findall(pattern, text)
        
        # Count frequencies
        freq = Counter(matches)
        
        # Filter and sort
        concepts = []
        for name, count in freq.most_common(max_concepts * 2):
            if len(name) > 3 and count > 1:
                # Rough importance based on frequency
                importance = min(10, 3 + count)
                
                concepts.append({
                    "name": name,
                    "definition": f"A key concept mentioned {count} times in the material.",
                    "importance": importance,
                    "difficulty": "medium",
                    "category": "General"
                })
        
        return concepts[:max_concepts]
    
    async def generate_knowledge_graph(
        self,
        concepts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a knowledge graph from concepts.
        
        Args:
            concepts: List of concepts with relationships
        
        Returns:
            Graph data structure for visualization
        """
        nodes = []
        edges = []
        
        for concept in concepts:
            nodes.append({
                "id": concept.get("name", ""),
                "label": concept.get("name", ""),
                "importance": concept.get("importance", 5),
                "difficulty": concept.get("difficulty", "medium"),
                "category": concept.get("category", "General")
            })
            
            # Add prerequisite edges
            prereqs = concept.get("prerequisites", "").split(",")
            for prereq in prereqs:
                prereq = prereq.strip()
                if prereq:
                    edges.append({
                        "source": prereq,
                        "target": concept.get("name", ""),
                        "type": "prerequisite"
                    })
            
            # Add related edges
            related = concept.get("related_concepts", "").split(",")
            for rel in related:
                rel = rel.strip()
                if rel:
                    edges.append({
                        "source": concept.get("name", ""),
                        "target": rel,
                        "type": "related"
                    })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
