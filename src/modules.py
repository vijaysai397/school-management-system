import os
import uuid
from datetime import date, datetime
from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from src.database import get_database_connection, PROJECT_ROOT


def logged_in(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in first.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def allowed(*roles):
    def decorator(view):
        @wraps(view)
        @logged_in
        def wrapped(*args, **kwargs):
            if session.get("role") not in roles:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def form_value(name, default=""):
    return request.form.get(name, default).strip()


def save_upload(field, folder, extensions):
    upload = request.files.get(field)
    if not upload or not upload.filename:
        return None
    extension = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
    if extension not in extensions:
        flash("That file type is not allowed.", "error")
        return None
    folder_path = os.path.join(PROJECT_ROOT, "static", "uploads", folder)
    os.makedirs(folder_path, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{secure_filename(upload.filename)}"
    upload.save(os.path.join(folder_path, stored_name))
    return f"uploads/{folder}/{stored_name}"


@logged_in
def dashboard():
    connection = get_database_connection()
    role = session.get("role")
    current_student = connection.execute(
        "SELECT id, full_name FROM students WHERE email = ?",
        (session.get("user_email", ""),),
    ).fetchone()
    if role == "admin":
        counts = {
            "Students": connection.execute("SELECT COUNT(*) AS total FROM students").fetchone()["total"],
            "Faculty": connection.execute("SELECT COUNT(*) AS total FROM faculty").fetchone()["total"],
            "Books": connection.execute("SELECT COUNT(*) AS total FROM books").fetchone()["total"],
            "Notes": connection.execute("SELECT COUNT(*) AS total FROM notes").fetchone()["total"],
        }
        actions = [
            ("Students", "Add and manage student records", "student_form"),
            ("Faculty", "Manage faculty details and salary", "faculty_form"),
            ("Fees", "Record payments and view dues", "fee_form"),
            ("Library", "Manage books, cards, and issues", "books"),
            ("Academics", "Enter marks and create report cards", "marks_form"),
            ("Notes", "Upload teaching PDFs", "note_form"),
        ]
    elif role == "faculty":
        counts = {
            "Students": connection.execute("SELECT COUNT(*) AS total FROM students").fetchone()["total"],
            "Exam marks": connection.execute("SELECT COUNT(*) AS total FROM marks").fetchone()["total"],
            "Books": connection.execute("SELECT COUNT(*) AS total FROM books").fetchone()["total"],
            "Notes": connection.execute("SELECT COUNT(*) AS total FROM notes").fetchone()["total"],
        }
        actions = [
            ("Student directory", "View student profiles", "student_list"),
            ("Enter marks", "Record subject-wise exam marks", "marks_form"),
            ("Exam results", "Review marks already entered", "marks_list"),
            ("Library", "Browse the book catalog", "books"),
            ("Teaching notes", "Upload or read class PDFs", "notes"),
        ]
    else:
        counts = {
            "My report card": 1 if current_student else 0,
            "Library books": connection.execute("SELECT COUNT(*) AS total FROM books").fetchone()["total"],
            "Study notes": connection.execute("SELECT COUNT(*) AS total FROM notes").fetchone()["total"],
        }
        actions = [
            ("Library catalog", "Browse available school books", "books"),
            ("Study notes", "Open notes shared by faculty", "notes"),
        ]
        if current_student:
            actions.insert(0, ("My report card", "View marks and teacher remarks", "report_card", current_student["id"]))
    connection.close()
    return render_template("dashboard.html", counts=counts, actions=actions, role=role, current_student=current_student)


STUDENT_FIELDS = [
    ("admission_number", "Admission number", "text", True), ("full_name", "Full name", "text", True),
    ("dob", "Date of birth", "date", False), ("gender", "Gender", "text", False),
    ("blood_group", "Blood group", "text", False), ("class_name", "Class", "text", False),
    ("section", "Section", "text", False), ("roll_number", "Roll number", "text", False),
    ("admission_date", "Admission date", "date", False), ("aadhar_number", "Aadhar/ID number", "text", False),
    ("nationality", "Nationality", "text", False), ("phone", "Phone", "tel", False),
    ("email", "Email", "email", False), ("guardian_name", "Parent/guardian name", "text", False),
    ("guardian_occupation", "Guardian occupation", "text", False), ("guardian_contact", "Guardian contact", "tel", False),
    ("guardian_email", "Guardian email", "email", False), ("emergency_contact", "Emergency contact", "tel", False),
    ("previous_school", "Previous school", "text", False), ("transport_route", "Transport route", "text", False),
    ("address", "Address", "textarea", False), ("medical_notes", "Medical notes/allergies", "textarea", False),
]


@allowed("admin", "faculty")
def student_list():
    connection = get_database_connection()
    students = connection.execute("SELECT * FROM students ORDER BY full_name").fetchall()
    connection.close()
    return render_template("students.html", students=students)


@allowed("admin")
def student_form(student_id=None):
    connection = get_database_connection()
    student = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone() if student_id else None
    if student_id and not student:
        connection.close()
        flash("Student not found.", "error")
        return redirect(url_for("student_list"))
    if request.method == "POST":
        values = [form_value(field[0]) for field in STUDENT_FIELDS]
        photo = save_upload("photo", "students", {"jpg", "jpeg", "png", "webp"})
        if not values[0] or not values[1]:
            flash("Admission number and full name are required.", "error")
        else:
            columns = ", ".join(field[0] for field in STUDENT_FIELDS)
            if student_id:
                assignments = ", ".join(f"{field[0]} = ?" for field in STUDENT_FIELDS)
                values.append(photo or student["photo"])
                connection.execute(f"UPDATE students SET {assignments}, photo = ? WHERE id = ?", (*values, student_id))
                message = "Student updated."
            else:
                connection.execute(f"INSERT INTO students ({columns}, photo, created_at) VALUES ({', '.join('?' for _ in STUDENT_FIELDS)}, ?, ?)", (*values, photo, datetime.utcnow().isoformat()))
                message = "Student added."
            connection.commit()
            connection.close()
            flash(message, "success")
            return redirect(url_for("student_list"))
    connection.close()
    return render_template("student_form.html", fields=STUDENT_FIELDS, student=student, student_id=student_id)


@allowed("admin", "faculty")
def student_view(student_id):
    connection = get_database_connection()
    student = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    connection.close()
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("student_list"))
    return render_template("student_view.html", student=student)


@allowed("admin")
def student_delete(student_id):
    connection = get_database_connection()
    connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
    connection.commit()
    connection.close()
    flash("Student deleted.", "success")
    return redirect(url_for("student_list"))


@allowed("admin", "faculty")
def marks_list():
    connection = get_database_connection()
    marks = connection.execute("SELECT marks.*, students.full_name, students.admission_number FROM marks JOIN students ON students.id = marks.student_id ORDER BY marks.id DESC").fetchall()
    connection.close()
    return render_template("marks.html", marks=marks)


@allowed("admin", "faculty")
def marks_form():
    connection = get_database_connection()
    students = connection.execute("SELECT id, admission_number, full_name FROM students ORDER BY full_name").fetchall()
    if request.method == "POST":
        obtained = float(form_value("obtained", "0"))
        maximum = float(form_value("max_marks", "0"))
        percentage = round(obtained * 100 / maximum, 2) if maximum else 0
        grade = "A+" if percentage >= 90 else "A" if percentage >= 80 else "B" if percentage >= 70 else "C" if percentage >= 60 else "D" if percentage >= 40 else "F"
        connection.execute("INSERT INTO marks (student_id, subject, obtained, max_marks, grade, percentage, exam_type, term, academic_year, attendance_percent, class_rank, teacher_remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.form.get("student_id"), form_value("subject"), obtained, maximum, grade, percentage, form_value("exam_type"), form_value("term"), form_value("academic_year"), form_value("attendance_percent", "0"), form_value("class_rank", ""), form_value("teacher_remarks")))
        connection.commit()
        connection.close()
        flash("Marks saved.", "success")
        return redirect(url_for("marks_list"))
    connection.close()
    return render_template("mark_form.html", students=students)


@allowed("admin", "faculty", "student")
def report_card(student_id):
    connection = get_database_connection()
    student = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    marks = connection.execute("SELECT * FROM marks WHERE student_id = ? ORDER BY subject", (student_id,)).fetchall()
    connection.close()
    total = sum(row["obtained"] for row in marks)
    maximum = sum(row["max_marks"] for row in marks)
    percentage = round(total * 100 / maximum, 2) if maximum else 0
    return render_template("report_card.html", student=student, marks=marks, total=total, maximum=maximum, percentage=percentage)


@allowed("admin", "faculty")
def fee_list():
    connection = get_database_connection()
    fees = connection.execute("SELECT fees.*, students.full_name, students.admission_number FROM fees JOIN students ON students.id = fees.student_id ORDER BY fees.due_date").fetchall()
    connection.close()
    return render_template("fees.html", fees=fees)


@allowed("admin")
def fee_form():
    connection = get_database_connection()
    students = connection.execute("SELECT id, admission_number, full_name FROM students ORDER BY full_name").fetchall()
    if request.method == "POST":
        total = float(form_value("total_fee", "0"))
        paid = float(form_value("paid_amount", "0"))
        due = max(total - paid - float(form_value("discount", "0")) + float(form_value("late_fee", "0")), 0)
        status = "paid" if due == 0 else "overdue" if form_value("due_date") and form_value("due_date") < date.today().isoformat() else "pending"
        connection.execute("INSERT INTO fees (student_id, fee_head, total_fee, paid_amount, due_amount, due_date, payment_date, payment_mode, receipt_number, installment_plan, late_fee, discount, academic_year, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.form.get("student_id"), form_value("fee_head"), total, paid, due, form_value("due_date"), form_value("payment_date"), form_value("payment_mode"), form_value("receipt_number"), form_value("installment_plan"), form_value("late_fee", "0"), form_value("discount", "0"), form_value("academic_year"), status))
        connection.commit()
        connection.close()
        flash("Fee record saved.", "success")
        return redirect(url_for("fee_list"))
    connection.close()
    return render_template("fee_form.html", students=students)


@allowed("admin", "faculty", "student")
def books():
    connection = get_database_connection()
    rows = connection.execute("SELECT * FROM books ORDER BY title").fetchall()
    connection.close()
    return render_template("books.html", books=rows)


@allowed("admin")
def book_form():
    if request.method == "POST":
        copies = int(form_value("total_copies", "1"))
        connection = get_database_connection()
        connection.execute("INSERT INTO books (book_id, title, author, isbn, category, publisher, edition, total_copies, available_copies, shelf_location, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (form_value("book_id"), form_value("title"), form_value("author"), form_value("isbn"), form_value("category"), form_value("publisher"), form_value("edition"), copies, copies, form_value("shelf_location"), date.today().isoformat()))
        connection.commit()
        connection.close()
        flash("Book added.", "success")
        return redirect(url_for("books"))
    return render_template("book_form.html")


@allowed("admin")
def library_card_form():
    connection = get_database_connection()
    students = connection.execute("SELECT id, admission_number, full_name FROM students ORDER BY full_name").fetchall()
    if request.method == "POST":
        connection.execute("INSERT INTO library_cards (card_number, student_id, issue_date, expiry_date, status) VALUES (?, ?, ?, ?, ?)", (form_value("card_number"), request.form.get("student_id"), form_value("issue_date"), form_value("expiry_date"), form_value("status", "active")))
        connection.commit()
        connection.close()
        flash("Library card created.", "success")
        return redirect(url_for("books"))
    connection.close()
    return render_template("library_card_form.html", students=students)


@allowed("admin", "faculty")
def transactions():
    connection = get_database_connection()
    rows = connection.execute("SELECT book_transactions.*, books.title, students.full_name FROM book_transactions JOIN books ON books.id = book_transactions.book_id JOIN students ON students.id = book_transactions.student_id ORDER BY issue_date DESC").fetchall()
    connection.close()
    return render_template("transactions.html", transactions=rows)


@allowed("admin")
def transaction_form():
    connection = get_database_connection()
    books_rows = connection.execute("SELECT id, title, available_copies FROM books WHERE available_copies > 0").fetchall()
    students = connection.execute("SELECT id, full_name FROM students ORDER BY full_name").fetchall()
    if request.method == "POST":
        connection.execute("INSERT INTO book_transactions (book_id, student_id, issue_date, due_date) VALUES (?, ?, ?, ?)", (request.form.get("book_id"), request.form.get("student_id"), form_value("issue_date"), form_value("due_date")))
        connection.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = ? AND available_copies > 0", (request.form.get("book_id"),))
        connection.commit()
        connection.close()
        flash("Book issued.", "success")
        return redirect(url_for("transactions"))
    connection.close()
    return render_template("transaction_form.html", books=books_rows, students=students)


@allowed("admin")
def return_transaction(transaction_id):
    connection = get_database_connection()
    transaction = connection.execute("SELECT book_id FROM book_transactions WHERE id = ? AND return_date IS NULL", (transaction_id,)).fetchone()
    if transaction:
        connection.execute("UPDATE book_transactions SET return_date = ?, return_condition = ?, fine = ? WHERE id = ?", (date.today().isoformat(), form_value("return_condition", "Good"), form_value("fine", "0"), transaction_id))
        connection.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = ?", (transaction["book_id"],))
        connection.commit()
        flash("Book returned.", "success")
    else:
        flash("Active transaction not found.", "error")
    connection.close()
    return redirect(url_for("transactions"))


FACULTY_FIELDS = [("faculty_id", "Faculty ID"), ("name", "Name"), ("dob", "Date of birth"), ("gender", "Gender"), ("qualification", "Qualification"), ("subject_specialization", "Subject specialization"), ("designation", "Designation"), ("department", "Department"), ("joining_date", "Date of joining"), ("employment_type", "Employment type"), ("contact", "Contact"), ("address", "Address"), ("aadhar_pan", "Aadhar/PAN"), ("bank_account", "Bank account"), ("assigned_classes", "Classes/subjects assigned"), ("experience", "Experience")]


@allowed("admin")
def faculty_list():
    connection = get_database_connection()
    rows = connection.execute("SELECT * FROM faculty ORDER BY name").fetchall()
    connection.close()
    return render_template("faculty.html", faculty=rows)


@allowed("admin")
def faculty_form():
    if request.method == "POST":
        values = [form_value(field[0]) for field in FACULTY_FIELDS]
        photo = save_upload("photo", "faculty", {"jpg", "jpeg", "png", "webp"})
        connection = get_database_connection()
        connection.execute(f"INSERT INTO faculty ({', '.join(field[0] for field in FACULTY_FIELDS)}, photo) VALUES ({', '.join('?' for _ in FACULTY_FIELDS)}, ?)", (*values, photo))
        connection.commit()
        connection.close()
        flash("Faculty member added.", "success")
        return redirect(url_for("faculty_list"))
    return render_template("faculty_form.html", fields=FACULTY_FIELDS)


@allowed("admin")
def salary_list():
    connection = get_database_connection()
    rows = connection.execute("SELECT salary.*, faculty.name, faculty.faculty_id AS faculty_code FROM salary JOIN faculty ON faculty.id = salary.faculty_id ORDER BY month DESC").fetchall()
    connection.close()
    return render_template("salary.html", salary=rows)


@allowed("admin")
def salary_form():
    connection = get_database_connection()
    faculty = connection.execute("SELECT id, faculty_id, name FROM faculty ORDER BY name").fetchall()
    if request.method == "POST":
        values = {name: float(form_value(name, "0")) for name in ["basic_pay", "hra", "da", "allowances", "pf", "tax", "leave_deduction", "deductions"]}
        gross = values["basic_pay"] + values["hra"] + values["da"] + values["allowances"]
        net = gross - values["pf"] - values["tax"] - values["leave_deduction"] - values["deductions"]
        connection.execute("INSERT INTO salary (faculty_id, month, basic_pay, hra, da, allowances, pf, tax, leave_deduction, deductions, gross_salary, net_salary, payment_date, payment_mode, bank_reference, increment_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.form.get("faculty_id"), form_value("month"), *values.values(), gross, net, form_value("payment_date"), form_value("payment_mode"), form_value("bank_reference"), form_value("increment_history")))
        connection.commit()
        connection.close()
        flash("Salary record saved.", "success")
        return redirect(url_for("salary_list"))
    connection.close()
    return render_template("salary_form.html", faculty=faculty)


@allowed("admin", "faculty", "student")
def notes():
    connection = get_database_connection()
    rows = connection.execute("SELECT notes.*, faculty.name AS uploader FROM notes JOIN faculty ON faculty.id = notes.uploaded_by ORDER BY upload_date DESC").fetchall()
    connection.close()
    return render_template("notes.html", notes=rows)


@allowed("admin", "faculty")
def note_form():
    connection = get_database_connection()
    faculty = connection.execute("SELECT id, faculty_id, name FROM faculty ORDER BY name").fetchall()
    if request.method == "POST":
        stored_file = save_upload("file", "notes", {"pdf"})
        if not stored_file:
            connection.close()
            return render_template("note_form.html", faculty=faculty)
        upload = request.files.get("file")
        connection.execute("INSERT INTO notes (file_name, stored_file, subject, class_name, section, upload_date, file_type, file_size, topic, description, uploaded_by, visibility, previous_file) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (secure_filename(upload.filename), stored_file, form_value("subject"), form_value("class_name"), form_value("section"), datetime.utcnow().isoformat(), upload.mimetype, os.path.getsize(os.path.join(PROJECT_ROOT, "static", stored_file)), form_value("topic"), form_value("description"), request.form.get("uploaded_by"), form_value("visibility"), form_value("previous_file")))
        connection.commit()
        connection.close()
        flash("Note uploaded.", "success")
        return redirect(url_for("notes"))
    connection.close()
    return render_template("note_form.html", faculty=faculty)