CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('admin', 'faculty', 'student')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_number TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    dob TEXT, gender TEXT, blood_group TEXT, photo TEXT,
    class_name TEXT, section TEXT, roll_number TEXT, admission_date TEXT,
    aadhar_number TEXT, nationality TEXT, address TEXT, phone TEXT, email TEXT,
    guardian_name TEXT, guardian_occupation TEXT, guardian_contact TEXT, guardian_email TEXT,
    emergency_contact TEXT, previous_school TEXT, medical_notes TEXT, transport_route TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL, subject TEXT NOT NULL, obtained REAL NOT NULL, max_marks REAL NOT NULL,
    grade TEXT, percentage REAL, exam_type TEXT, term TEXT, academic_year TEXT,
    attendance_percent REAL, class_rank INTEGER, teacher_remarks TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL, fee_head TEXT NOT NULL, total_fee REAL NOT NULL, paid_amount REAL NOT NULL DEFAULT 0,
    due_amount REAL NOT NULL DEFAULT 0, due_date TEXT, payment_date TEXT, payment_mode TEXT, receipt_number TEXT,
    installment_plan TEXT, late_fee REAL NOT NULL DEFAULT 0, discount REAL NOT NULL DEFAULT 0,
    academic_year TEXT, status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT, book_id TEXT NOT NULL UNIQUE, title TEXT NOT NULL, author TEXT,
    isbn TEXT, category TEXT, publisher TEXT, edition TEXT, total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1, shelf_location TEXT, date_added TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS library_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT, card_number TEXT NOT NULL UNIQUE, student_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL, expiry_date TEXT, status TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL, due_date TEXT, return_date TEXT, fine REAL NOT NULL DEFAULT 0,
    return_condition TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id TEXT NOT NULL UNIQUE, name TEXT NOT NULL, dob TEXT,
    gender TEXT, photo TEXT, qualification TEXT, subject_specialization TEXT, designation TEXT,
    department TEXT, joining_date TEXT, employment_type TEXT, contact TEXT, address TEXT,
    aadhar_pan TEXT, bank_account TEXT, assigned_classes TEXT, experience TEXT
);

CREATE TABLE IF NOT EXISTS salary (
    id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id INTEGER NOT NULL, month TEXT NOT NULL,
    basic_pay REAL NOT NULL DEFAULT 0, hra REAL NOT NULL DEFAULT 0, da REAL NOT NULL DEFAULT 0,
    allowances REAL NOT NULL DEFAULT 0, pf REAL NOT NULL DEFAULT 0, tax REAL NOT NULL DEFAULT 0,
    leave_deduction REAL NOT NULL DEFAULT 0, deductions REAL NOT NULL DEFAULT 0,
    gross_salary REAL NOT NULL DEFAULT 0, net_salary REAL NOT NULL DEFAULT 0,
    payment_date TEXT, payment_mode TEXT, bank_reference TEXT, increment_history TEXT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT NOT NULL, stored_file TEXT NOT NULL,
    subject TEXT NOT NULL, class_name TEXT, section TEXT, upload_date TEXT NOT NULL,
    file_type TEXT, file_size INTEGER, topic TEXT, description TEXT, uploaded_by INTEGER NOT NULL,
    visibility TEXT, previous_file TEXT,
    FOREIGN KEY (uploaded_by) REFERENCES faculty(id) ON DELETE CASCADE
);
