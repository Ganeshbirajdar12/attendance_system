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
        database="attendance_system"
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
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:
        return render_template("student_auth.html", register_error="Passwords do not match")

    hashed_password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO student_auth (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        db.commit()
    except mysql.connector.IntegrityError:
        cursor.close()
        db.close()
        return render_template("student_auth.html", register_error="Username or email already taken")

    cursor.close()
    db.close()
    return render_template("student_auth.html", register_success="Registration successful! Please log in.")

@app.route("/student/login", methods=["POST"])
def student_login():
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student_auth WHERE username=%s", (username,))
    student = cursor.fetchone()
    cursor.close()
    db.close()

    if student and check_password_hash(student["password"], password):
        session["admin_id"] = student["id"]
        return redirect("/student/dashboard")

    return render_template("student_auth.html", login_error="Invalid username or password")





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

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect("/admin/auth")   # Redirect if not logged in

    return render_template("admin_dashboard.html")

# ================== LONGOUTS ==================
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)   # remove admin session
    return redirect("/")  # go back to login page


# ===================add teachers =================================
@app.route("/admin/add_teacher")
def admin_add_teacher_page():
    if "admin_id" not in session:
        return redirect("/admin/auth")
    return render_template("add_teacher.html")

@app.route("/admin/add_program")
def admin_add_program_page():
    if "admin_id" not in session:
        return redirect("/admin/auth")
    return render_template("add_program.html")

@app.route("/admin/add_class")
def admin_add_class_page():
    if "admin_id" not in session:
        return redirect("/admin/auth")
    return render_template("add_class.html")

@app.route("/admin/assign_class")
def admin_assign_class_page():
    if "admin_id" not in session:
        return redirect("/admin/auth")
    return render_template("assign_class.html")

if __name__ == "__main__":
    app.run(debug=True)

