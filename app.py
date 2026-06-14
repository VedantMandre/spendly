import sqlite3

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import (
    create_user,
    get_db,
    get_user_by_email,
    init_db,
    seed_db,
)

app = Flask(__name__)


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def fail(message):
        return render_template(
            "register.html", error=message, name=name, email=email
        )

    if not name or not email or not password:
        return fail("All fields are required.")
    if "@" not in email or "." not in email:
        return fail("Please enter a valid email address.")
    if len(password) < 8:
        return fail("Password must be at least 8 characters.")
    if get_user_by_email(email) is not None:
        return fail("Email already registered.")

    try:
        create_user(name, email, generate_password_hash(password))
    except sqlite3.IntegrityError:
        return fail("Email already registered.")

    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
