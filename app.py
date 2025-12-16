from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import DevelopmentConfig
from datetime import date

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
app.config.from_object(DevelopmentConfig)
app.secret_key = "your_secret_key"


# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="attendance_system1"
    )

# ------------------------------------------
#                 INDEX
# ------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------
#          STUDENT AUTHENTICATION
# ------------------------------------------
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
        session["student_id"] = student["id"]
        return redirect("/student/dashboard")

    return render_template("student_auth.html", login_error="Invalid username or password")


# ------------------------------------------
#           TEACHER AUTHENTICATION
# ------------------------------------------
@app.route("/teacher/auth")
def teacher_auth_page():
    return render_template("teacher_auth.html")

@app.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Teachers WHERE username = %s", (username,))
        teacher = cursor.fetchone()
        cursor.close()
        db.close()

        if teacher and check_password_hash(teacher["password"], password):
           
            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["name"]
            return redirect("/teacher/dashboard")
        else:
           
            return render_template("teacher_auth.html", login_error="Invalid username or password")

   
    return render_template("teacher_auth.html")


# ------------------------------------------
#              ADMIN AUTHENTICATION
# ------------------------------------------
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
    return redirect(url_for('admin_auth_page', register_success='Registration successful! Please login.'))


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

    return redirect(url_for('admin_auth_page', login_error='Invalid username or password'))


# ------------------------------------------
#                DASHBOARDS
# ------------------------------------------
@app.route("/student/dashboard")
def student_dashboard():
    if 'student_id' not in session:
        return redirect("/student/auth")
    return render_template("student_dashboard.html")

@app.route("/teacher/dashboard")
def teacher_dashboard():
    if "teacher_id" not in session:
        return redirect("/teacher/auth")

    return render_template("teacher_dashboard.html", name=session.get("teacher_name"))



@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect("/admin/auth")
    return render_template("admin_dashboard.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect("/")


# ------------------------------------------
#      ADMIN STATIC FORM PAGES
# ------------------------------------------
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


@app.route("/admin/assign_class")
def admin_assign_class_page():
    if "admin_id" not in session:
        return redirect("/admin/auth")
    return render_template("assign_class.html")




# ------------------------------------------
#              ADD PROGRAM
# ------------------------------------------
@app.route('/admin/add_program', methods=['POST'])
def add_program():
    program_name = request.form['program_name']
    program_code = request.form['program_code']
    duration = request.form['duration']
    department = request.form['department']
    description = request.form['description']

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO Programs (program_name, program_code, duration, department, description)
        VALUES (%s, %s, %s, %s, %s)
    """, (program_name, program_code, duration, department, description))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_add_program_page', success='true'))


# ------------------------------------------
#              ADD CLASS 
# ------------------------------------------
@app.route('/admin/add_class', methods=['GET'])
def show_add_class_form():
    if "admin_id" not in session:
        return redirect("/admin/auth")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT program_name FROM Programs")
    programs = cursor.fetchall()

    cursor.execute("SELECT name FROM Teachers")
    teachers = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('add_class.html', programs=programs, teachers=teachers)


@app.route('/admin/add_class', methods=['POST'])
def add_class():
    class_name = request.form['class_name']
    program = request.form['program']
    year = request.form.get('year')
    teacher = request.form.get('teacher')
    division = request.form.get('division')
    description = request.form.get('description')

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO Classes (class_name, program, year, teacher, division, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (class_name, program, year, teacher, division, description))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('show_add_class_form', success='true'))


# ------------------------------------------
#          ADD TEACHER
# ------------------------------------------
@app.route('/admin/add_teacher', methods=['POST'])
def add_teacher():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO Teachers (name, email, phone, username, password)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, phone, username, hashed_password))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('show_add_teacher_form', success='true'))


@app.route('/admin/add_teacher', methods=['GET'])
def show_add_teacher_form():
    return render_template('add_teacher.html')


# -------------- ADD STUDENT (GET + POST) ----------------
@app.route("/teacher/add_student", methods=["GET", "POST"])
def add_student():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # --------- GET Programs + Classes ---------
    cursor.execute("SELECT id, program_name FROM programs")
    programs = cursor.fetchall()

    cursor.execute("SELECT id, class_name FROM classes")
    classes = cursor.fetchall()

    # ======================== POST ========================
    if request.method == "POST":
        roll_number = request.form.get("roll_number", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name")
        gender = request.form.get("gender")
        dob = request.form.get("dob")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        program_id = request.form.get("program_id", "").strip()
        class_id = request.form.get("class_id", "").strip()
        admission_date = request.form.get("admission_date")
        status = request.form.get("status", "Active")

        # ------------------ VALIDATION ------------------
        if not roll_number or not first_name or not program_id or not class_id:
            flash("Roll Number, First Name, Program and Class are required!", "error")
            return redirect(url_for("add_student"))

        try:
            # --------- INSERT INTO DATABASE ---------
            sql = """
                INSERT INTO students 
                (roll_number, first_name, last_name, gender, dob, email, phone, 
                 address, class_id, program_id, admission_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                roll_number, first_name, last_name, gender, dob, email, phone,
                address, class_id, program_id, admission_date, status
            ))

            db.commit()
            flash("Student added successfully!", "success")

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")

        return redirect(url_for("add_student"))

    # ======================== GET ========================
    return render_template(
        "add_student.html",
        programs=programs,
        classes=classes
    )

# @app.route("/teacher/mark_attendance")
# def teacher_mark_attendance_page():
#     if "admin_id" not in session:
#         return redirect("/teacher/auth")
#     return render_template("mark_attendance.html")


# ========================== MARK TODAY ATTENDANCE =======================================================================
@app.route("/teacher/mark_attendance", methods=["GET", "POST"])
def mark_attendance():
    if "teacher_id" not in session:
        return redirect("/teacher/auth")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    today_date = date.today()

    # Load Programs & Classes
    cursor.execute("SELECT id, program_name FROM programs")
    programs = cursor.fetchall()

    cursor.execute("SELECT id, class_name FROM classes")
    classes = cursor.fetchall()

    students = []

    # GET selected program/class
    program_id = request.args.get("program_id")
    class_id = request.args.get("class_id")

    if program_id and class_id:
        cursor.execute("""
            SELECT student_id, roll_number, first_name, last_name
            FROM students
            WHERE program_id = %s AND class_id = %s AND status = 'Active'
            ORDER BY roll_number
        """, (program_id, class_id))
        students = cursor.fetchall()

    # POST attendance
    if request.method == "POST":
        try:
            for key, value in request.form.items():
                if key.startswith("attendance["):
                    student_id = key.replace("attendance[", "").replace("]", "")
                    status = value

                    cursor.execute("""
                        INSERT INTO attendance (student_id, attendance_date, status)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE status = VALUES(status)
                    """, (student_id, today_date, status))

            db.commit()
            flash("Attendance saved successfully!", "success")

        except Exception as e:
            db.rollback()
            flash(f"Error saving attendance: {e}", "error")

        return redirect(url_for("mark_attendance",
                                program_id=program_id,
                                class_id=class_id))

    cursor.close()
    db.close()

    return render_template(
        "mark_attendance.html",
        programs=programs,
        classes=classes,
        students=students,
        today_date=today_date.strftime("%d %b %Y")
    )




# ------------------------------------------
#                RUN APP
# ------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
