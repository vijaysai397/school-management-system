from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from src.database import get_database_connection


def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([name, email, username, password, confirm_password]):
            flash("Please fill in every field.", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        connection = get_database_connection()
        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ? OR username = ?",
            (email, username),
        ).fetchone()

        if existing_user:
            connection.close()
            flash("That email or username is already registered.", "error")
            return render_template("signup.html")

        connection.execute(
            """
            INSERT INTO users (name, email, username, password, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                username,
                generate_password_hash(password),
                datetime.utcnow().isoformat(),
            ),
        )
        connection.commit()
        connection.close()

        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")
