import bcrypt
import sqlite3

# Generate new password hash
password = b'test123'
hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

print(f"New hash: {hashed}")

# Update database
conn = sqlite3.connect('studybuddy.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed, 'alimusharaf.baig@gmail.com'))
conn.commit()
print(f"Rows updated: {cursor.rowcount}")
conn.close()
print("Password reset to: test123")
