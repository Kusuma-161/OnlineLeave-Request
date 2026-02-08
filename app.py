from flask import Flask, render_template, request, redirect
import sqlite3
import smtplib
from flask import redirect

app = Flask(__name__)

# -----------------------------
# DB table create function
# -----------------------------
def init_db():
    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()
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

# Call this function app start avvagane
init_db()
# -----------------------------
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

        if user:
            return redirect('/dashboard')
        else:
            return "Invalid Login ❌"

    return render_template('login.html')


# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
# ---------------- APPLY LEAVE ---------------- #

@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if request.method == 'POST':
        
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        reason = request.form['reason']
        email = request.form['email']  # <-- student email

        conn = sqlite3.connect('leave.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO leave_requests ( from_date, to_date, reason, email, status) VALUES ( ?, ?, ?, ?, ?)",
            ( from_date, to_date, reason, email, "Pending")
        )

        conn.commit()
        conn.close()

        return "Leave Applied Successfully!"  # Or redirect to leave history

    return render_template('apply_leave.html')
       # ---------------- LEAVE HISTORY ---------------- #

@app.route('/history')
def history():

    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM leave_requests")
    data = cur.fetchall()

    conn.close()

    return render_template('history.html', data=data)
# ---------------- HOD DASHBOARD ---------------- #

@app.route('/hod')
def hod():

    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM leave_requests")
    data = cur.fetchall()

    conn.close()

    return render_template('hod_dashboard.html', data=data)
# ---------------- APPROVE LEAVE ---------------- #

@app.route('/approve/<int:id>')
def approve(id):

    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    # Email fetch
    cur.execute(
        "SELECT email FROM leave_requests WHERE id=?",
        (id,)
    )
    data = cur.fetchone()
    receiver_mail = data[0]

    # Status update
    cur.execute(
        "UPDATE leave_requests SET status='Approved' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    send_email(receiver_mail, "Approved")

    return redirect('/hod')
# ---------------- REJECT LEAVE ---------------- #

@app.route('/reject/<int:id>')
def reject(id):

    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    # Email fetch
    cur.execute(
        "SELECT email FROM leave_requests WHERE id=?",
        (id,)
    )
    data = cur.fetchone()
    receiver_mail = data[0]

    # Status update
    cur.execute(
        "UPDATE leave_requests SET status='Rejected' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    send_email(receiver_mail, "Rejected")

    return redirect('/hod')


@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):
    conn = sqlite3.connect('leave.db')
    cur = conn.cursor()

    # Fetch student email from DB
    cur.execute("SELECT email FROM leave_requests WHERE id=?", (id,))
    data = cur.fetchone()
    receiver_mail = data[0] if data and data[0] else None

    # Update leave status
    cur.execute("UPDATE leave_requests SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()

    # Send mail only if email exists
    if receiver_mail:
        send_email(receiver_mail, status)

    return redirect('/hod')
def send_email(receiver_mail, status):

    sender = "leaveproject2026@gmail.com"
    password = "utgyfblshelryflg"

    message = f"Your Leave Request is {status}"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)

    server.sendmail(sender, receiver_mail, message)
    server.quit()
# ---------------- RUN APP ---------------- #

app.run(debug=True)