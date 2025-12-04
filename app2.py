from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="attendance_system"
    )

# ------------------------
# Teacher Dashboard
# ------------------------

@app.route("/teacher/dashboard")
def teacher_dashboard():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM student_auth WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and user['password'] == password:

            session['id'] = user['id']
            session.permanent = True
            return redirect("/teacher/dashboard")

        return render_template("teacher_login.html", error="Invalid Credentials")

    return render_template("teacher_login.html")

# --------------------------------
# Add Student
# --------------------------------
@app.route("/teacher/add-student", methods=["GET", "POST"])
def add_student():
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    if request.method == "POST":
        name = request.form.get("name")
        roll = request.form.get("roll")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO students (name, roll_no, email, password)
            VALUES (%s, %s, %s, %s)
        """, (name, roll, email, password))

        db.commit()
        db.close()

        return redirect("/teacher/dashboard")

    return render_template("add_student.html")


# --------------------------------
# Mark Attendance
# --------------------------------
@teacher_dashboard.route("/mark-attendance", methods=["GET", "POST"])
def mark_attendance():
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    if request.method == "POST":
        date = request.form.get("date")

        for student in students:
            status = request.form.get(f"status_{student['id']}")

            cur.execute("""
                INSERT INTO attendance (student_id, date, status)
                VALUES (%s, %s, %s)
            """, (student['id'], date, status))

        db.commit()
        db.close()

        return redirect("/teacher/dashboard")

    db.close()
    return render_template("mark_attendance.html", students=students)


# --------------------------------
# View Attendance
# --------------------------------
@teacher_dashboard.route("/view-attendance")
def view_attendance():
    if "id" not in session:
        return redirect("/teacher/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT students.name, students.roll_no, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    """)
    records = cur.fetchall()

    db.close()
    return render_template("view_attendance.html", records=records)


if __name__ == "__main__":
    app.run(debug=True)
