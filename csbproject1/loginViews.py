import os
import sqlite3
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.utils.cache import md5

db_path = os.path.dirname(__file__) + "/db.sqlite"


def hash_password(password):
    #  NOTE: First vulnerability, insecure hash function for password
    return md5(password.encode()).hexdigest()


def index(request):
    # Check for user id cookie (logged in)
    user_id = request.COOKIES.get("user_id", "")
    if len(user_id) > 0:
        return redirect("/dashboard")

    error = request.session.get("error", "")
    info = request.session.get("info", "")
    request.session["error"] = ""
    request.session["info"] = ""
    return render(request, "csbproject1/index.html", {"error": error, "info": info})


def login(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    if len(username) == 0 or len(password) == 0:
        return redirect("/")

    password_hash = hash_password(password)

    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find user
    cursor.execute(
        f"SELECT user_id, username FROM users WHERE username = ? AND password = ?",
        (
            username,
            password_hash,
        ),
    )
    user = cursor.fetchone()
    if not user:
        request.session["error"] = "Incorrect username or password"
        return redirect("/")

    #  NOTE: Third vulnerability, broken access control (similar to a weak session id in real life)
    response = redirect("/dashboard")
    response.set_cookie("user_id", user[0])
    return response


def register(request):
    # Input validation
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    if len(username) == 0 or len(password) == 0:
        return redirect("/")

    # Hash password
    password_hash = hash_password(password)

    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if username exists

    #  NOTE: Second vulnerability, SQL injection
    cursor.execute(f"SELECT count(*) FROM users WHERE username = '{username}'")
    user_count = cursor.fetchone()[0]

    if user_count > 0:
        request.session["error"] = "Username already exists"
        return redirect("/")

    cursor.execute(
        f"INSERT INTO users (username, password) VALUES ('{username}', '{password_hash}')"
    )
    conn.commit()

    request.session["info"] = "A new user has been created. You can log in now."
    return redirect("/")
