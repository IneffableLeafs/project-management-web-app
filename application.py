import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from sqlite3 import Error
from helpers import login_required, create_connection

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
@login_required
def index():
	return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Set up database for queries
    conn = create_connection("global.db")


    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        db = conn.cursor()
        username = request.form.get("username")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        rows = db.fetchall()
        conn.commit()

        # Ensure username exists and password is correct
        if rows == [] or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        conn.close()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Set up database for queries
    conn = create_connection("global.db")
    conn2 = create_connection("global.db")

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 403)

        # Ensure the confirmation is the same as the password
        elif request.form.get("password") != request.form.get("confirmation"):
        	return apology("passwords don't match", 403)

        # Get username and password
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        db = conn.cursor()
        db2 = conn2.cursor()
		# Query database for username
        db.execute("SELECT * FROM users WHERE username=?", username)
        rows = db.fetchall()
        conn.commit()

        # Ensure username exists and password is correct
        if len(rows) == 1:
            return apology("username already taken", 403)

        # Add the new user to the database

        db2.execute("INSERT INTO users ('username', 'hash') VALUES (?, ?)", (username, password))
        rows2 = db2.fetchall()
        conn2.commit()

        conn.close()
        conn2.close()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

  
@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure project name was submitted
        if not request.form.get("project_name"):
            return apology("must provide project name", 403)

        # store project name and description as variables
        project_name = request.form.get("project_name")
        project_description = request.form.get("project_description")
        
        # connect to sqlite3 and put name and description into database
        conn = create_connection("global.db")
        db = conn.cursor()
        db.execute("INSERT INTO users ('username', 'hash') VALUES (?, ?)", (username, password))
        rows = db.fetchall()
        conn.commit()
        conn.close()


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("create.html")
