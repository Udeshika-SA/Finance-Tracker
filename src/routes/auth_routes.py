from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from src.database.db import get_db
from src.models.user import User
import hashlib

auth_bp = Blueprint("auth", __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# Login 
# =========================
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        # ---------- Validate empty fields ----------
        if not username or not password:
            flash("Please enter username and password", "danger")
            return redirect(url_for("auth.login"))
        
        # ---------- Check whether user is already registered ----------
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        # ---------- If user already registered then navigate to the Dasboard, if not send error message ----------
        if user:
            login_user(User(user["id"], user["username"], user["email"]))
            return redirect(url_for("finance.dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html", show_nav=False)


# =========================
# Register 
# =========================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # ---------- Prevent empty insert ----------
        if not username or not email or not password:
            flash("All fields are required", "danger")
            return redirect(url_for("auth.register"))

        db = get_db()
        cursor = db.cursor()

        # ---------- Insert new user data to the database ----------
        cursor.execute(
            "INSERT INTO users (username,email,password) VALUES (%s,%s,%s)",
            (request.form["username"],
             request.form["email"],
             hash_password(request.form["password"]))
        )
        db.commit()

        # ---------- If account created successfully then navigate to the Login page ----------
        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", show_nav=False)


# =========================
# Logout 
# =========================
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))