import sqlite3
import os
import shutil

DB_PATH = "studybuddy.db"
UPLOAD_DIR = "uploads"

def reset_content():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("⚠ DELETING ALL COURSES AND CONTENT...")
        
        # Delete data tables
        tables = ["questions", "concept_relations", "concepts", "materials", "courses", "confusion_patterns"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Cleared table: {table}")
            
        conn.commit()
        conn.close()
        print("✅ Database cleared.")
        
        # Delete upload files
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
            print("✅ Uploaded files deleted.")
            os.makedirs(UPLOAD_DIR, exist_ok=True) # Recreate empty dir
            
        print("\n✨ SYSTEM RESET COMPLETE ✨")
        
    except Exception as e:
        print(f"❌ Error resetting content: {e}")

if __name__ == "__main__":
    reset_content()
