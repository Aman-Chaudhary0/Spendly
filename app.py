from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import create_user, get_user_by_email

app = Flask(__name__)
app.secret_key = 'spendly-dev-secret-key-123'


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not all([name, email, password, confirm_password]):
            flash("All fields are required", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        try:
            create_user(name, email, hashed_password)
            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("login.html")

        user = get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("landing"))

        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please sign in to view your profile", "error")
        return redirect(url_for("login"))

    # Hardcoded data for UI design phase (Step 4)
    user = {
        "name": "Aman Chaudhary",
        "email": "aman@example.com",
        "member_since": "October 2023",
        "initials": "AC"
    }
    stats = {
        "total_spent": "₹12,450.00",
        "transaction_count": 42,
        "top_category": "Food & Dining"
    }
    transactions = [
        {"date": "2023-10-15", "desc": "Grocery Store", "category": "Food", "amount": "₹1,200.00"},
        {"date": "2023-10-14", "desc": "Uber Ride", "category": "Transport", "amount": "₹450.00"},
        {"date": "2023-10-12", "desc": "Internet Bill", "category": "Bills", "amount": "₹999.00"},
    ]
    categories = [
        {"name": "Food", "amount": "₹4,500.00", "percentage": 36},
        {"name": "Transport", "amount": "₹2,100.00", "percentage": 17},
        {"name": "Bills", "amount": "₹5,850.00", "percentage": 47},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories
    )


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
    app.run(debug=True, port=5001)
