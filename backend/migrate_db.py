"""
Database migration script to add missing columns to confusion_patterns table.
Run this once to fix the schema mismatch.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "studybuddy.db")

def add_missing_columns():
    """Add missing columns to the confusion_patterns table."""
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(confusion_patterns)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing columns: {existing_columns}")
    
    columns_to_add = [
        ("user_answer", "TEXT"),
        ("correct_answer", "TEXT"),
        ("course_name", "VARCHAR(255)"),
        ("topic_name", "VARCHAR(255)"),
    ]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE confusion_patterns ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")


if __name__ == "__main__":
    add_missing_columns()
