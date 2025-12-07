from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import DevelopmentConfig

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
app.config.from_object(DevelopmentConfig)
app.secret_key = "your_secret_key"


app.secret_key = "your_secret_key"

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="SAMS"
    )

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


# ================== STUDENT AUTH ==================

@app.route("/student/auth")
def student_auth_page():
    return render_template("student_auth.html")


@app.route("/student/register", methods=["POST"])
def student_register():
    roll_no = request.form["roll_no"]
    name = request.form["name"]
    username = request.form["username"]
    password = request.form["password"]
    program_id = request.form["program_id"]
    class_id = request.form["class_id"]

    db = get_db_connection()
    cursor = db.cursor()

    # 1. Insert student into students table
    cursor.execute("""
        INSERT INTO students (roll_no, name, program_id, class_id)
        VALUES (%s, %s, %s, %s)
    """, (roll_no, name, program_id, class_id))

    student_id = cursor.lastrowid

    # 2. Insert login into student_auth table
    cursor.execute("""
        INSERT INTO student_auth (student_id, username, password_hash)
        VALUES (%s, %s, %s)
    """, (student_id, username, generate_password_hash(password)))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/student/login")

@app.route("/student/login", methods=["POST"])
def student_login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT sa.*, s.name, s.roll_no
        FROM student_auth sa
        JOIN students s ON sa.student_id = s.id
        WHERE sa.username = %s
    """, (username,))

    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and check_password_hash(user["password_hash"], password):
        session["student_id"] = user["student_id"]
        session["student_name"] = user["name"]
        return "Student Login Successful!"
    else:
        return "Invalid username or password"




# ================== TEACHER AUTH ==================
@app.route("/teacher/auth")
def teacher_auth_page():
    return render_template("teacher_auth.html")


@app.route("/teacher/register", methods=["POST"])
def teacher_register():
    name = request.form["name"]
    email = request.form["email"]
    username = request.form["username"]
    password = request.form["password"]

    db = get_db_connection()
    cursor = db.cursor()

    # Insert teacher
    cursor.execute("""
        INSERT INTO teachers (name, email)
        VALUES (%s, %s)
    """, (name, email))

    teacher_id = cursor.lastrowid

    # Insert login
    cursor.execute("""
        INSERT INTO teacher_auth (teacher_id, username, password_hash)
        VALUES (%s, %s, %s)
    """, (teacher_id, username, generate_password_hash(password)))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/teacher/login_page")

@app.route("/teacher/login", methods=["POST"])
def teacher_login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT ta.*, t.name, t.email
        FROM teacher_auth ta
        JOIN teachers t ON ta.teacher_id = t.id
        WHERE ta.username = %s
    """, (username,))

    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and check_password_hash(user["password_hash"], password):
        session["teacher_id"] = user["teacher_id"]
        session["teacher_name"] = user["name"]
        return "Teacher Login Successful!"
    else:
        return "Invalid username or password"
    



#====================================== admin auth ======================================
@app.route("/admin/auth")
def admin_auth_page():
    return render_template("admin_auth.html")

@app.route("/admin/register", methods=["POST"])
def admin_register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:
        return render_template("admin_auth.html", register_error="Passwords do not match")

    hashed_password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO admin_auth (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        db.commit()
    except mysql.connector.IntegrityError:
        cursor.close()
        db.close()
        return render_template("admin_auth.html", register_error="Username or email already taken")

    cursor.close()
    db.close()
    return render_template("admin_auth.html", register_success="Registration successful! Please log in.")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin_auth WHERE username=%s", (username,))
    admin = cursor.fetchone()
    cursor.close()
    db.close()

    if admin and check_password_hash(admin["password"], password):
        session["admin_id"] = admin["id"]
        return redirect("/admin/dashboard")

    return render_template("admin_auth.html", login_error="Invalid username or password")


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
@app.route("/view_attendance/<roll_no>")
def view_attendance(roll_no):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get student info
    cursor.execute("SELECT * FROM students WHERE roll_no=%s", (roll_no,))
    student = cursor.fetchone()

    if not student:
        return "Student not found"

    # Get attendance of this student
    cursor.execute("""
        SELECT date, status 
        FROM attendance
        WHERE student_id = %s
        ORDER BY date DESC
    """, (student['id'],))
    attendance = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("view_attendance.html",student=student,attendance=attendance)







# ================== LOGOUT ==================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

# ================== ADMIN LOGIN ==================
@app.route("/admin/auth", methods=["GET", "POST"])
def admin_auth():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Example static admin login
        if username == "admin" and password == "admin123":
            session["admin_id"] = 1
            return redirect("/admin/dashboard")

        return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")
