import sqlite3
import os

DB_PATH = "studybuddy.db"

BAD_CONCEPTS = [
    "Step", "Cross", "Table", "Figure", "Chapter", "Section", 
    "Page", "Reference", "Summary", "Index", "Appendix", 
    "Introduction", "Solution", "Problem", "Example", "Exercise",
    "Week", "Module", "Unit", "Topic", "Question", "Answer"
]

def clean_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"Checking for {len(BAD_CONCEPTS)} bad concept names...")
        
        # Build query
        placeholders = ','.join(['?'] * len(BAD_CONCEPTS))
        
        # Check count first
        cursor.execute(f"SELECT COUNT(*) FROM concepts WHERE name IN ({placeholders})", BAD_CONCEPTS)
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Found {count} bad concepts. Deleting...")
            cursor.execute(f"DELETE FROM concepts WHERE name IN ({placeholders})", BAD_CONCEPTS)
            conn.commit()
            print("✅ Successfully deleted bad concepts.")
            
            # Also clean up related questions?
            # Cascading delete usually handles this, or they become orphaned.
            # But let's check questions too just in case.
            # (Assuming questions link to concept_id)
        else:
            print("✨ No bad concepts found in database.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")

if __name__ == "__main__":
    clean_database()
