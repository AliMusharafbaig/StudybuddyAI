import sqlite3
import os

DB_PATH = "studybuddy.db"

def wipe_concepts():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("⚠ Wiping ALL concepts, questions, and relations...")
        
        # Delete from dependent tables first
        cursor.execute("DELETE FROM concept_relations")
        cursor.execute("DELETE FROM questions")
        cursor.execute("DELETE FROM confusion_patterns")
        
        # Delete concepts
        cursor.execute("DELETE FROM concepts")
        
        print(f"Deleted {cursor.rowcount} concepts.")
        conn.commit()
        conn.close()
        print("✅ Database successfully scrubbed.")
        
    except Exception as e:
        print(f"❌ Error wiping database: {e}")

if __name__ == "__main__":
    wipe_concepts()
