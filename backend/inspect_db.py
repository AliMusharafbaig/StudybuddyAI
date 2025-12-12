import sqlite3

def check_concepts():
    try:
        conn = sqlite3.connect("studybuddy.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT email FROM users")
        users = cursor.fetchall()
        print(f"Users in DB: {users}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_concepts()
