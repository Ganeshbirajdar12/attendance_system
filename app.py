from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

app.secret_key = "your_secret_key"

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="attendance_system"
    )

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


# ================== STUDENT LOGIN ==================
@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM student_auth WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and user['password'] == password:

            session['student_id'] = user['id']
            session.permanent = True
            return redirect("/student/dashboard")

        return render_template("student_login.html", error="Invalid Credentials")

    return render_template("student_login.html")


# ================== TEACHER LOGIN ==================
@app.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teachers WHERE email=%s", (email,))
        user = cursor.fetchone()
        db.close()

        if user and user['password'] == password:

            session['teacher_id'] = user['id']  # FIXED
            session.permanent = True
            return redirect("/teacher/dashboard")  # FIXED

        return render_template("teacher_login.html", error="Invalid Credentials")

    return render_template("teacher_login.html")





# ================== DASHBOARDS ==================
@app.route("/student/dashboard")
def student_dashboard():
    if 'student_id' not in session:
        return redirect("/student/login")
    return render_template("student_dashboard.html")


@app.route("/teacher/dashboard")
def teacher_dashboard():
    if 'teacher_id' not in session:
        return redirect("/teacher/login")
    return render_template("teacher_dashboard.html")

# --------------------------------
# Mark Attendance
# --------------------------------
@app.route("/teacher/mark_attendance", methods=["POST"])
def mark_attendance():
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    student_id = request.form.get("student_id")
    status = request.form.get("status")  # Present / Absent

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO attendance (student_id, status) VALUES (%s, %s)",
        (student_id, status)
    )
    db.commit()
    cursor.close()
    db.close()

    return redirect("/teacher/dashboard")


# ================== ADD STUDENTS ==================
@app.route("/teacher_dashboard/add_student", methods=["POST"])
def add_student():
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    name = request.form.get("name")
    roll = request.form.get("roll")
    email = request.form.get("email")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO students (name, roll, email) VALUES (%s, %s, %s)",
        (name, roll, email)
    )
    db.commit()
    cursor.close()
    db.close()

    return redirect("/teacher/dashboard")

# ================== VIEW ATTENDANCE  ===============
@app.route("/teacher/view_attendance")
def view_attendance():
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT students.name, students.roll, attendance.date, attendance.status
        FROM attendance 
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    """)
    records = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("teacher_attendance.html", records=records)









# ================== LOGOUT ==================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
