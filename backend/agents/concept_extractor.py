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
        
        import asyncio
        for chunk in chunks:
            text = chunk.get("text", "")
            if not text or len(text) < 100:
                continue
            
            # THROTTLE: 4s delay avoids hitting Gemini Free Tier Rate Limits (15 RPM)
            await asyncio.sleep(4)
            
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
        IMPROVED fallback: Extract using more intelligent heuristics.
        
        Filters out:
        - Person names (detected via common name patterns)
        - Course metadata and headers
        - Non-educational content
        """
        import re
        from collections import Counter
        
        concepts = []
        
        # Common person name patterns to filter - first/last names
        common_first_names = {
            'muhammad', 'mohammad', 'ahmed', 'ali', 'john', 'james', 'michael', 'david', 
            'robert', 'william', 'dr', 'prof', 'professor', 'mr', 'mrs', 'ms', 'sir'
        }
        common_last_names = {
            'khan', 'ahmed', 'ali', 'smith', 'johnson', 'williams', 'brown', 'jones',
            'idrees', 'owais', 'shah', 'malik', 'hussain', 'kumar', 'singh'
        }
        
        # Stop phrases - metadata and non-concept content
        stop_phrases = {
            "Table Of Contents", "Figure Shows", "Chapter Summary", "Cross Reference",
            "Section Introduction", "Page Number", "End Of Chapter", "Learning Objectives",
            "Course Instructor", "Course Name", "Semester Fall", "Semester Spring",
            "Department Of", "University Of", "Assignment Due", "Quiz Date",
            "Lecture Notes", "Slide Number", "Copyright Reserved", "All Rights",
            "Contact Information", "Email Address", "Office Hours", "Course Outline"
        }
        
        def is_garbage_or_name(phrase):
            """Check if phrase is a name, garbage, or metadata."""
            phrase_clean = phrase.lower().replace(" ", "")
            phrase_lower = phrase.lower().strip()
            
            # 1. Specific garbage names the user reported
            blocked_patterns = [
                "muhammadowaisidrees", "owaisidrees", "muhammad", "idrees", 
                "instructor", "student", "teacher", "professor"
            ]
            if any(bp in phrase_clean for bp in blocked_patterns):
                return True
            
            # 2. SLIDE titles and presentation artifacts (e.g., "SLIDE 7: HOW IT WORKS")
            slide_patterns = [
                r'^slide\s*\d+',  # SLIDE 7, Slide 12
                r'^page\s*\d+',   # Page 1, PAGE 5
                r'^section\s*\d+', # Section 1
                r'^chapter\s*\d+', # Chapter 3
                r'^\d+\s*[-:]\s*', # 7: TITLE, 12 - SOMETHING
                r'^\d+%',          # 35% Complete
                r'\d+%\s*(complete|done|finished)', # XX% Complete
                r'^appendix',      # Appendix A
                r'^exhibit',       # Exhibit 1
            ]
            for pattern in slide_patterns:
                if re.match(pattern, phrase_lower):
                    return True
            
            # 3. Contains specific garbage keywords
            garbage_keywords = [
                'slide', 'title slide', 'business model', 'how it works', 
                'what we', 'we built', 'our team', 'our mission', 'our vision',
                'agenda', 'outline', 'overview', 'introduction', 'conclusion',
                'thank you', 'questions', 'q&a', 'contact us', 'next steps',
                'table of contents', 'copyright', 'all rights reserved',
                'proprietary', 'confidential', 'draft', 'version'
            ]
            if any(keyword in phrase_lower for keyword in garbage_keywords):
                return True
                
            # 4. Check for long concatenated strings without spaces (parsing errors)
            # e.g., "UnderstandingLogisticRegressionOctober1,2025"
            if len(phrase) > 20 and ' ' not in phrase:
                return True
                
            # 5. Check for Numbered Concepts (e.g. "1 Feature...") or Figures/Tables
            if phrase and phrase[0].isdigit():
                return True
            if phrase_lower.startswith("figure") or phrase_lower.startswith("table"):
                return True
            
            # 6. Presentation section patterns
            if re.match(r'^(the\s+)?(perfect|financial|market|problem|solution|team|product)', phrase_lower):
                # These are often slide section names, not concepts
                if len(phrase.split()) <= 3:
                    return True
                
            # 7. Standard name checks
            words = phrase.lower().split()
            if len(words) > 5:
                # Filter very long phrases (likely sentences, not concepts)
                return True
                
            # Check for common names
            if any(w in common_first_names or w in common_last_names for w in words):
                return True
                
            return False
        
        # Extract section headers (lines that are short and capitalized)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            words = line.split()
            if 3 <= len(words) <= 7:
                caps_ratio = sum(1 for w in words if w and w[0].isupper()) / len(words)
                if caps_ratio > 0.6 and len(line) < 100:
                    # Skip if looks like a name or stop phrase
                    if is_garbage_or_name(line):
                        continue
                    if any(sp.lower() in line.lower() for sp in stop_phrases):
                        continue
                    concepts.append({
                        "name": line,
                        "definition": f"Key topic or section: {line}",
                        "importance": 8,
                        "difficulty": "medium",
                        "category": "Topic"
                    })
        
        # Extract multi-word capitalized phrases (likely concepts)
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
        matches = re.findall(pattern, text)
        
        # Count frequencies and filter
        freq = Counter(matches)
        
        for phrase, count in freq.most_common(max_concepts * 2):
            # Skip names and stop phrases
            if is_garbage_or_name(phrase):
                continue
            if phrase in stop_phrases or any(sp.lower() in phrase.lower() for sp in stop_phrases):
                continue
            # Filter noise and only keep if appears 2+ times
            if count >= 2 and len(phrase) > 5:
                concepts.append({
                    "name": phrase,
                    "definition": f"Important concept mentioned {count} times in the material.",
                    "importance": min(10, 5 + count),
                    "difficulty": "medium",
                    "category": "Concept"
                })
        
        # De-duplicate by name
        seen = set()
        unique_concepts = []
        for c in concepts:
            name_lower = c["name"].lower()
            if name_lower not in seen:
                seen.add(name_lower)
                unique_concepts.append(c)
        
        return unique_concepts[:max_concepts]
    
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
