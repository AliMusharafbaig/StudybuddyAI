"""
Cleanup Garbage Concepts Script
================================
This script removes garbage concepts from the database.
Uses minimal imports to avoid loading heavy ML dependencies (TensorFlow, sentence_transformers).
"""

import asyncio
import aiosqlite
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path - using same path as the main app
DB_PATH = os.path.join(os.path.dirname(__file__), "studybuddy.db")


def is_garbage_concept(name: str) -> bool:
    """Check if a concept name is garbage and should be deleted."""
    import re
    
    if not name:
        return False
    
    name_lower = name.lower().strip()
    name_clean = name_lower.replace(" ", "")
    
    # Check 1: User reported names
    blocked_patterns = [
        "muhammadowaisidrees", "owaisidrees", "muhammad", "idrees", 
        "instructor", "student", "teacher", "professor"
    ]
    if any(bp in name_clean for bp in blocked_patterns):
        return True
    
    # Check 2: SLIDE titles and presentation artifacts
    slide_patterns = [
        r'^slide\s*\d*',  # SLIDE 7, Slide, SLIDE 12
        r'^page\s*\d+',   # Page 1
        r'^section\s*\d+', # Section 1
        r'^chapter\s*\d+', # Chapter 3
        r'^\d+\s*[-:]\s*', # 7: TITLE
        r'^\d+%',          # 35%
        r'\d+%\s*(complete|done|finished)', # XX% Complete
    ]
    for pattern in slide_patterns:
        if re.match(pattern, name_lower):
            return True
    
    # Check 3: Garbage keywords commonly found in pitch decks and presentations
    garbage_keywords = [
        'slide', 'title slide', 'business model', 'how it works', 
        'what we', 'we built', 'our team', 'our mission', 'our vision',
        'agenda', 'outline', 'overview', 'introduction', 'conclusion',
        'thank you', 'questions', 'q&a', 'contact us', 'next steps',
        'table of contents', 'copyright', 'all rights reserved',
        'proprietary', 'confidential', 'draft', 'version',
        'perfect storm', 'financial impact', 'market opportunity',
        'traction', 'neuro-trading', 'pitch deck', 'shark tank',
        'the problem', 'the solution', 'the team', 'the product',
        'ask', 'funding', 'investment', 'valuation'
    ]
    if any(keyword in name_lower for keyword in garbage_keywords):
        return True
    
    # Check 4: Numbered headers (e.g. "1 Feature...", "6 Logistic...")
    if name and name[0].isdigit():
        return True
    
    # Check 5: "Figure" or "Table" captions 
    if name_lower.startswith("figure") or name_lower.startswith("table"):
        return True
    
    # Check 6: Very long names without spaces (parsing errors)
    if len(name) > 25 and ' ' not in name:
        return True
    
    # Check 7: Very short or very long phrases
    if len(name) < 3 or len(name.split()) > 6:
        return True
    
    return False


async def cleanup_garbage():
    """Delete garbage concepts from the database using raw SQL."""
    
    if not os.path.exists(DB_PATH):
        logger.error(f"Database not found at: {DB_PATH}")
        return
    
    logger.info(f"Connecting to database: {DB_PATH}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            # 1. Fetch all concepts
            logger.info("Scanning for garbage concepts...")
            
            cursor = await db.execute("SELECT id, name FROM concepts")
            all_concepts = await cursor.fetchall()
            
            garbage_ids = []
            
            for concept_id, name in all_concepts:
                if is_garbage_concept(name):
                    logger.info(f"Found garbage concept: {name}")
                    garbage_ids.append(concept_id)
            
            logger.info(f"Found {len(garbage_ids)} garbage concept(s).")
            
            if garbage_ids:
                # 2. Delete related questions first
                for concept_id in garbage_ids:
                    await db.execute(
                        "DELETE FROM questions WHERE concept_id = ?",
                        (concept_id,)
                    )
                
                # 3. Delete the concepts
                for concept_id in garbage_ids:
                    await db.execute(
                        "DELETE FROM concepts WHERE id = ?",
                        (concept_id,)
                    )
                
                await db.commit()
                logger.info(f"Deleted {len(garbage_ids)} garbage concept(s) and their related questions.")
            else:
                logger.info("No garbage concepts found.")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(cleanup_garbage())
