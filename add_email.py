import sqlite3

# Connect to your DB
conn = sqlite3.connect('leave.db')
cur = conn.cursor()

# Add email column
try:
    cur.execute("ALTER TABLE leave_requests ADD COLUMN email TEXT;")
    print("Email column added successfully!")
except sqlite3.OperationalError:
    print("Column already exists or table does not exist.")

conn.commit()
conn.close()