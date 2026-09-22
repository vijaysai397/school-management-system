# Indus Valley International School

Simple Flask login and signup module backed by SQLite.

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

The app supports account creation, duplicate email/username checks, password hashing, username or email login, sessions, flash messages, and logout.
