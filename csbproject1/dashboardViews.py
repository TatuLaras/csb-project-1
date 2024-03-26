import os
import sqlite3
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.utils.cache import md5

db_path = os.path.dirname(__file__) + "/db.sqlite"


def dashboard(request):
    # Require login
    user_id = request.COOKIES.get("user_id", "")
    if len(user_id) == 0:
        request.session["error"] = "You need to be logged in for that"
        return redirect("/")

    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get username
    cursor.execute(f"SELECT username FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        response = redirect("/")
        response.delete_cookie("user_id")
        request.session["error"] = "You need to be logged in for that"
        return response

    user = {"username": row[0], "id": user_id}

    # Get posts
    cursor.execute(
        f"SELECT u.username, p.content FROM posts p LEFT JOIN users u ON u.user_id = p.user_id ORDER BY p.post_id DESC"
    )
    post_rows = cursor.fetchall()

    posts = []
    for row in post_rows:
        posts.append({"username": row[0], "content": row[1]})

    return render(request, "csbproject1/dashboard.html", {"user": user, "posts": posts})


def post(request):
    # Require login
    user_id = request.COOKIES.get("user_id", "")
    if len(user_id) == 0:
        request.session["error"] = "You need to be logged in for that"
        return redirect("/")

    # Validate input
    content = request.POST.get("content", "")
    if len(content) == 0:
        return redirect("/dashboard")

    # Connect to db and insert post
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (user_id, content) VALUES (?, ?)",
        (
            user_id,
            content,
        ),
    )

    conn.commit()

    return redirect("/dashboard")
