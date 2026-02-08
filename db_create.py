import sqlite3

# Create database file
conn = sqlite3.connect('leave.db')

# Create cursor
cur = conn.cursor()

# Create students table
cur.execute("""
CREATE TABLE students(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT,
 email TEXT,
 password TEXT
)
""")

conn = sqlite3.connect('leave.db')
cur = conn.cursor()

cur.execute("""
CREATE TABLE leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    reason TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()
# Save changes
conn.commit()
conn.close()

print("Database created successfully")