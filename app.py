from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import DevelopmentConfig
from datetime import date, datetime
from flask import send_file
from io import BytesIO
import os

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

app.config.from_object(DevelopmentConfig)

# ================= SECRET KEY =================
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")


# =========================================================
#                    DATABASE CONNECTION
# =========================================================
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        connection_timeout=10,
        autocommit=True
    )


# =========================================================
#                         INDEX
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
#                  STUDENT AUTHENTICATION
# =========================================================
@app.route('/student/auth', methods=['GET', 'POST'])
def student_login():

    if request.method == 'POST':

        roll_no = request.form.get('roll_no')
        password = request.form.get('password')

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT student_id, roll_number, hash_password, status
                FROM students
                WHERE roll_number = %s
                AND status = 'Active'
            """

            cursor.execute(query, (roll_no,))
            student = cursor.fetchone()

            # ================= PASSWORD CHECK =================
            if student and check_password_hash(student['hash_password'], password):

                session['student_id'] = student['student_id']
                session['roll_number'] = student['roll_number']
                session['role'] = 'student'

                return redirect("/student/dashboard")

            else:
                return render_template(
                    'student_auth.html',
                    login_error="Invalid Roll Number or Password"
                )

        except Exception as e:
            return render_template(
                'student_auth.html',
                login_error=f"Error: {e}"
            )

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('student_auth.html')


# =========================================================
#                  TEACHER AUTHENTICATION
# =========================================================
@app.route("/teacher/auth")
def teacher_auth_page():
    return render_template("teacher_auth.html")


@app.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = None
        cursor = None

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM teachers WHERE username = %s",
                (username,)
            )

            teacher = cursor.fetchone()

            if teacher and check_password_hash(
                teacher["password"],
                password
            ):

                session["teacher_id"] = teacher["id"]
                session["teacher_name"] = teacher["name"]

                return redirect("/teacher/dashboard")

            return render_template(
                "teacher_auth.html",
                login_error="Invalid username or password"
            )

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    return render_template("teacher_auth.html")


# =========================================================
#                    ADMIN AUTHENTICATION
# =========================================================
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
        return render_template(
            "admin_auth.html",
            register_error="Passwords do not match"
        )

    hashed_password = generate_password_hash(password)

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO admin_auth
            (username, email, password)
            VALUES (%s, %s, %s)
            """,
            (username, email, hashed_password)
        )

        db.commit()

        return redirect(
            url_for(
                'admin_auth_page',
                register_success='Registration successful!'
            )
        )

    except mysql.connector.IntegrityError:
        return render_template(
            "admin_auth.html",
            register_error="Username or email already taken"
        )

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@app.route("/admin/login", methods=["POST"])
def admin_login():

    username = request.form.get("username")
    password = request.form.get("password")

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM admin_auth WHERE username=%s",
            (username,)
        )

        admin = cursor.fetchone()

        if admin and check_password_hash(
            admin["password"],
            password
        ):

            session["admin_id"] = admin["id"]

            return redirect("/admin/dashboard")

        return redirect(
            url_for(
                'admin_auth_page',
                login_error='Invalid username or password'
            )
        )

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
#                       DASHBOARDS
# =========================================================
@app.route("/student/dashboard")
def student_dashboard():

    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                s.student_id,
                s.roll_number AS roll_no,
                s.first_name,
                s.last_name,
                s.email,
                s.address,
                c.class_name AS class_name,
                p.program_name AS program
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            LEFT JOIN programs p ON s.program_id = p.id
            WHERE s.student_id = %s
        """

        cursor.execute(query, (session['student_id'],))
        student = cursor.fetchone()

        if not student:
            flash("Student not found!", "error")
            return redirect(url_for('student_login'))

        student['name'] = (
            f"{student['first_name']} "
            f"{student['last_name'] or ''}"
        ).strip()

        return render_template(
            "student_dashboard.html",
            student=student
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/teacher/dashboard")
def teacher_dashboard():

    if "teacher_id" not in session:
        return redirect("/teacher/auth")

    return render_template(
        "teacher_dashboard.html",
        name=session.get("teacher_name")
    )


@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect("/admin/auth")

    return render_template("admin_dashboard.html")


# =========================================================
#                          LOGOUTS
# =========================================================
@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_id", None)

    return redirect("/")


@app.route("/student/logout")
def student_logout():

    session.pop("student_id", None)
    session.pop("roll_number", None)

    return redirect("/")


@app.route("/teacher/logout")
def teacher_logout():

    session.pop("id", None)
    session.pop("teacher_name", None)

    return redirect("/")


# =========================================================
#                       ADD TEACHER
# =========================================================
@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        db = None
        cursor = None

        try:
            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO teachers
                (name, email, phone, username, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                name,
                email,
                phone,
                username,
                hashed_password
            ))

            db.commit()

            flash("Teacher added successfully!", "success")

            return redirect(url_for('add_teacher'))

        except Exception as e:
            flash(f"Error: {e}", "error")

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    return render_template('add_teacher.html')


# =========================================================
#                       ADD STUDENT
# =========================================================
@app.route("/teacher/add_student", methods=["GET", "POST"])
def add_student():

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT id, program_name FROM programs")
        programs = cursor.fetchall()

        cursor.execute("SELECT id, class_name FROM classes")
        classes = cursor.fetchall()

        if request.method == "POST":

            roll_number = request.form.get("roll_number", "").strip()
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name")
            gender = request.form.get("gender")
            dob = request.form.get("dob")
            email = request.form.get("email")
            password = request.form.get("password")
            phone = request.form.get("phone")
            address = request.form.get("address")
            program_id = request.form.get("program_id")
            class_id = request.form.get("class_id")
            admission_date = request.form.get("admission_date")
            status = request.form.get("status", "Active")

            hashed_password = generate_password_hash(password)

            sql = """
                INSERT INTO students (
                    roll_number,
                    first_name,
                    last_name,
                    gender,
                    dob,
                    email,
                    phone,
                    address,
                    class_id,
                    program_id,
                    admission_date,
                    status,
                    hash_password
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                roll_number,
                first_name,
                last_name,
                gender,
                dob,
                email,
                phone,
                address,
                class_id,
                program_id,
                admission_date,
                status,
                hashed_password
            ))

            db.commit()

            flash("Student added successfully!", "success")

            return redirect(url_for("add_student"))

        return render_template(
            "add_student.html",
            programs=programs,
            classes=classes
        )

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
#                   MARK ATTENDANCE
# =========================================================
@app.route("/teacher/mark_attendance", methods=["GET", "POST"])
def mark_attendance():

    if "teacher_id" not in session:
        return redirect("/teacher/auth")

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        today_date = date.today()

        cursor.execute("SELECT id, program_name FROM programs")
        programs = cursor.fetchall()

        cursor.execute("SELECT id, class_name FROM classes")
        classes = cursor.fetchall()

        students = []

        program_id = request.args.get("program_id")
        class_id = request.args.get("class_id")

        if program_id and class_id:

            cursor.execute("""
                SELECT
                    student_id,
                    roll_number,
                    first_name,
                    last_name
                FROM students
                WHERE program_id = %s
                AND class_id = %s
                AND status = 'Active'
                ORDER BY roll_number
            """, (program_id, class_id))

            students = cursor.fetchall()

        if request.method == "POST":

            attendance_data = []

            for key, value in request.form.items():

                if key.startswith("attendance["):

                    student_id = (
                        key.replace("attendance[", "")
                        .replace("]", "")
                    )

                    attendance_data.append(
                        (student_id, today_date, value)
                    )

            cursor.executemany("""
                INSERT INTO attendance
                (student_id, attendance_date, status)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                status = VALUES(status)
            """, attendance_data)

            db.commit()
            flash("Attendance saved successfully!", "success")

            return redirect(
                url_for(
                    "mark_attendance",
                    program_id=program_id,
                    class_id=class_id
                )
            )

        return render_template(
            "mark_attendance.html",
            programs=programs,
            classes=classes,
            students=students,
            today_date=today_date.strftime("%d %b %Y")
        )

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
#                        RUN APP
# =========================================================
if __name__ == "__main__":
    app.run(debug=False)