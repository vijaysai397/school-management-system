import os

from flask import Flask, redirect, render_template, session, url_for

from src.database import initialize_database
from src.login import login, logout
from src.signup import signup


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


def home():
    if session.get("user_id"):
        return render_template("login.html", logged_in=True)
    return redirect(url_for("login"))


app.add_url_rule("/", endpoint="home", view_func=home)
app.add_url_rule("/login", endpoint="login", view_func=login, methods=["GET", "POST"])
app.add_url_rule("/logout", endpoint="logout", view_func=logout)
app.add_url_rule(
    "/signup",
    endpoint="signup",
    view_func=signup,
    methods=["GET", "POST"],
)


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
