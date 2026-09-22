from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from src.database import get_database_connection


def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_database_connection()
        user = connection.execute(
            "SELECT id, name, email, role, password FROM users "
            "WHERE username = ? OR email = ?",
            (username, username.lower()),
        ).fetchone()
        connection.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["role"] = user["role"]
            return redirect(url_for("home"))

        flash("Invalid username/email or password.", "error")

    return render_template("login.html")


def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))
