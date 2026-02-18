from flask import Flask, render_template, request, redirect
import sqlite3
import smtplib
import re

app = Flask(__name__)

# -------------------------
# DB table create function
# -------------------------

def init_db():
    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    # Students table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    ''')

    # Leave table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_date TEXT,
        to_date TEXT,
        reason TEXT,
        email TEXT,
        status TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Only college email allowed
        pattern = r'^\d{12}\.[a-zA-Z]+@gvpcew\.ac\.in$'
        if not re.match(pattern, email):
            return "Invalid College Email Format ❌"

        conn = sqlite3.connect('leave.db')
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO students (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
        except:
            return "User already exists ❌"

        conn.close()
        return redirect('/')

    return render_template('register.html')


# ---------------- LOGIN ---------------- #

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('leave.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM students WHERE email=? AND password=?",
            (email, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            return redirect('/dashboard')
        else:
            return "Invalid Login ❌"

    return render_template('login.html')


# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ---------------- HISTORY ---------------- #

@app.route('/history')
def history():
    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    cur.execute("SELECT id, from_date, to_date, reason, status FROM leave_requests")
    data = cur.fetchall()

    conn.close()

    return render_template('history.html', leaves=data)


# ---------------- APPLY LEAVE ---------------- #

@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():

    if request.method == 'POST':

        from_date = request.form['from_date']
        to_date = request.form['to_date']
        reason = request.form['reason']
        email = request.form['email']

        conn = sqlite3.connect('leave.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO leave_requests (from_date, to_date, reason, email, status) VALUES (?, ?, ?, ?, ?)",
            (from_date, to_date, reason, email, "Pending")
        )

        conn.commit()
        conn.close()

        return "Leave Applied Successfully ✅"

    return render_template('apply_leave.html')


# ---------------- HOD DASHBOARD ---------------- #

@app.route('/hod')
def hod():

    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM leave_requests")
    data = cur.fetchall()

    conn.close()

    return render_template('hod_dashboard.html', data=data)


# ---------------- UPDATE STATUS ---------------- #

@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):

    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    cur.execute("SELECT email FROM leave_requests WHERE id=?", (id,))
    data = cur.fetchone()
    receiver_mail = data[0] if data else None

    cur.execute("UPDATE leave_requests SET status=? WHERE id=?", (status, id))

    conn.commit()
    conn.close()

    if receiver_mail:
        send_email(receiver_mail, status)

    return redirect('/hod')


# ---------------- SEND EMAIL ---------------- #

def send_email(receiver_mail, status):

    sender = "leaveproject2026@gmail.com"
    password = "utgyfblshelryflg"

    message = f"Subject: Leave Status Update\n\nYour Leave Request is {status}"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver_mail, message)
    server.quit()


# ---------------- RUN APP ---------------- #

if __name__ == '__main__':
    app.run(debug=True)