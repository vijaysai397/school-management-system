import os

from flask import Flask, redirect, render_template, session, url_for

from src.database import initialize_database
from src.login import login, logout
from src.signup import signup
from src.modules import (
    dashboard, student_list, student_form, student_view, student_delete,
    marks_list, marks_form, report_card, fee_list, fee_form,
    books, book_form, library_card_form, transactions, transaction_form, return_transaction,
    faculty_list, faculty_form, salary_list, salary_form, notes, note_form,
)


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
initialize_database()


def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
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
app.add_url_rule("/dashboard", endpoint="dashboard", view_func=dashboard)
app.add_url_rule("/students", endpoint="student_list", view_func=student_list)
app.add_url_rule("/students/add", endpoint="student_form", view_func=student_form, methods=["GET", "POST"])
app.add_url_rule("/students/<int:student_id>", endpoint="student_view", view_func=student_view)
app.add_url_rule("/students/<int:student_id>/edit", endpoint="student_edit", view_func=student_form, methods=["GET", "POST"])
app.add_url_rule("/students/<int:student_id>/delete", endpoint="student_delete", view_func=student_delete, methods=["POST"])
app.add_url_rule("/marks", endpoint="marks_list", view_func=marks_list)
app.add_url_rule("/marks/add", endpoint="marks_form", view_func=marks_form, methods=["GET", "POST"])
app.add_url_rule("/students/<int:student_id>/report-card", endpoint="report_card", view_func=report_card)
app.add_url_rule("/fees", endpoint="fee_list", view_func=fee_list)
app.add_url_rule("/fees/add", endpoint="fee_form", view_func=fee_form, methods=["GET", "POST"])
app.add_url_rule("/library/books", endpoint="books", view_func=books)
app.add_url_rule("/library/books/add", endpoint="book_form", view_func=book_form, methods=["GET", "POST"])
app.add_url_rule("/library/cards/add", endpoint="library_card_form", view_func=library_card_form, methods=["GET", "POST"])
app.add_url_rule("/library/transactions", endpoint="transactions", view_func=transactions)
app.add_url_rule("/library/transactions/add", endpoint="transaction_form", view_func=transaction_form, methods=["GET", "POST"])
app.add_url_rule("/library/transactions/<int:transaction_id>/return", endpoint="return_transaction", view_func=return_transaction, methods=["POST"])
app.add_url_rule("/faculty", endpoint="faculty_list", view_func=faculty_list)
app.add_url_rule("/faculty/add", endpoint="faculty_form", view_func=faculty_form, methods=["GET", "POST"])
app.add_url_rule("/salary", endpoint="salary_list", view_func=salary_list)
app.add_url_rule("/salary/add", endpoint="salary_form", view_func=salary_form, methods=["GET", "POST"])
app.add_url_rule("/notes", endpoint="notes", view_func=notes)
app.add_url_rule("/notes/add", endpoint="note_form", view_func=note_form, methods=["GET", "POST"])


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
