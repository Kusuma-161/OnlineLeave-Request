import sqlite3

# Connect to database
conn = sqlite3.connect('leave.db')
cur = conn.cursor()

# Insert student record
cur.execute("""
INSERT INTO students (name, email, password)
VALUES ('Kusuma', 'kusuma@gmail.com', '1234')
""")

conn.commit()
conn.close()

print("Student added successfully")