# Indus Valley International School

Flask and SQLite school management system for students, academics, fees, library, faculty, salary, and teaching notes.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "replace-with-a-random-secret"
python app.py
```

Open `http://127.0.0.1:5000` in a browser. The `queries/database.db` file and `users` table are created automatically on the first run.

The root `app.py` starts the application. Login code lives in `src/login.py`, signup code lives in `src/signup.py`, and shared database setup lives in `src/database.py`. Database files and SQL schema files live in `queries/`.

The app supports account creation, duplicate email/username checks, password hashing, username or email login, sessions, role checks, flash messages, and logout. The dashboard links to the student, marks/report card, fees, library, faculty, salary, and PDF notes modules. Uploaded photos and notes are stored under `static/uploads/`.

Accounts can use the `admin`, `faculty`, or `student` role. Admin users manage records; faculty users can view students and enter marks; students can view the portal and report cards. For a production deployment, restrict who can create an admin account.

An empty database is populated automatically with demo records on first startup. Demo logins are `admin` / `admin123`, `faculty` / `faculty123`, and `student` / `student123`.
