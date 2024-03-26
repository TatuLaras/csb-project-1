import os
import sqlite3
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.utils.cache import md5

db_path = os.path.dirname(__file__) + "/db.sqlite"


def hash_password(password):
    # FLAW: The app uses the dated and now insecure md5 hash algorithm, in addition to not salting it.
    # A3:2017-Sensitive Data Exposure
    return md5(password.encode()).hexdigest()

    # The fix is to not use md5 and opt in for a more secure hashing algorithm, such as bcrypt.
    # To do this, you first need to install bcrypt by running 'pip install bcrypt'.
    # After which you can import the bcrypt module at the top of this file.
    # Finally, you can replace the contents of this function with the following:

    # salt = bcrypt.gensalt()
    # return bcrypt.hashpw(password.encode(), salt)


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

    # FLAW: The app uses a cookie for storing authentication data, which is just an integer of the user's id,
    # allowing an attacker to gain access to other users' accounts by editing the cookie on client side.
    # A5:2017-Broken Access Control

    # This is analoguous to a weak session id, but because Django makes it a bit difficult to shoot yourself
    # in the foot in this way, this is what I went with.

    response = redirect("/dashboard")
    response.set_cookie("user_id", user[0])

    return response

    # The fix is to use request.session to store this in session storage rather than as a client-side cookie.

    # Here we would replace the previous three lines with:

    # request.session["user_id"] = user[0]
    # return redirect("/dashboard")

    # And everywhere in this application where we check the user_id -cookie, we would check the session entry instead.

    # For example, at the start of the index route instead of:

    # user_id = request.COOKIES.get("user_id", "")

    # We would write:

    # user_id = request.session.get("user_id", "")


def register(request):
    # Input validation
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    if len(username) == 0 or len(password) == 0:
        return redirect("/")

    # FLAW: The app permits any password no matter how weak it may be.
    # (A2:2017-Broken Authentication)

    # The solution might for example look like setting constraints on password length:

    # if len(password) < 8:
    #     request.session["error"] = "Password must be more than 8 characters"
    #     return redirect("/")

    # One could also ensure that the password has numbers, special characters etc.

    # if not any(char.isdigit() for char in password) or not any(
    #     not c.isalnum() for c in password
    # ):
    #     request.session["error"] = (
    #         "Password must contain at least one number and one special character"
    #     )
    #     return redirect("/")

    # Other solutions, such as checking the password against
    # a list of the most common passwords
    # (as OWASP recommends: https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication.html)
    # may be applicable here.

    # Hash password
    password_hash = hash_password(password)

    # Connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if username exists

    # FLAW: The app doesn't sanitize inputs properly, making SQL injections possible.
    # A1:2017-Injection

    cursor.execute(f"SELECT count(*) FROM users WHERE username = '{username}'")

    # The fix is to replace the previous line with the following:

    # cursor.execute(f"SELECT count(*) FROM users WHERE username = ?", (username,))

    # Which will sanitize the input properly. One could also use Django's ORM
    # tools to implement their database, which handles inputs safely as well.
    # In fact, I went out of my way to use the bare sqlite3 Python library
    # instead of Django's database tools so I could have this security flaw.

    user_count = cursor.fetchone()[0]

    if user_count > 0:
        request.session["error"] = "Username already exists"
        return redirect("/")

    # Create user
    cursor.execute(
        f"INSERT INTO users (username, password) VALUES ('{username}', '{password_hash}')"
    )
    conn.commit()

    request.session["info"] = "A new user has been created. You can log in now."
    return redirect("/")
