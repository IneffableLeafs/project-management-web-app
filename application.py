# most of lines 3-32 is CS50x distribution code

import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from sqlite3 import Error
from helpers import login_required, create_connection
from datetime import date, datetime

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
    # Set up database for queries
    conn = create_connection("global.db")
    db = conn.cursor()
    user_id = str(session['user_id'])

    # Query database for username
    db.execute("SELECT username FROM users WHERE id=?", user_id)
    user = db.fetchall()

    # query database for project names
    db.execute("SELECT name FROM projects WHERE owner=?", user_id)
    project_names = db.fetchall()
    refined_project_names = []
    for project in project_names:
        refined_project_names.append(project[0])
    print(refined_project_names)

    # query database for project ids that user owns
    db.execute("SELECT id FROM projects WHERE owner=?", user_id)
    project_ids = db.fetchall()
    refined_project_ids = []
    for identification in project_ids:
        refined_project_ids.append(identification[0])
    ids = str(refined_project_ids)

    # query database for deadlines (detailed tasks)
    db.execute("SELECT task, deadline, project_id FROM tasks WHERE project_id IN (%s)" % ','.join('?'*len(ids)), ids)
    task_deadline_tuple = db.fetchall()
    print(task_deadline_tuple)

    # turn the list of tuples into a list of lists
    task_deadlines = [list(item) for item in task_deadline_tuple]
    print(task_deadlines)

    # add the project name to this list
    for task in task_deadlines:
        db.execute("SELECT name FROM projects WHERE id=?", str(task[2]))
        project_name = db.fetchall()
        task[2] = project_name[0][0]
    print(task_deadlines)

    user = user[0][0]
    conn.commit()
    today = date.today()
    print(today) # 2020-09-07
    day = today.strftime("%B %d, %Y")
    print(day) # September 07, 2020

    return render_template("index.html", username=user, current_date=day, refined_project_names=refined_project_names, info=task_deadlines)
    

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
            return render_template("error.html", error_message="must provide username")


        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", error_message="must provide password")


        db = conn.cursor()
        username = request.form.get("username")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = db.fetchall()
        conn.commit()

        # Ensure username exists and password is correct
        if rows == [] or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("error.html", error_message="invalid username and/or password")


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
            return render_template("error.html", error_message="must provide password")


        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", error_message="must provide password")


        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("error.html", error_message="must confirm password")


        # Ensure the confirmation is the same as the password
        elif request.form.get("password") != request.form.get("confirmation"):
        	return render_template("error.html", error_message="passwords don't match")


        # Get username and password
        username = request.form.get("username")
        print(username)
        password = generate_password_hash(request.form.get("password"))
        print(password)

        db = conn.cursor()
        db2 = conn2.cursor()
		# Query database for username
        db.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = db.fetchall()
        print(rows)
        conn.commit()

        # Ensure username exists and password is correct
        if len(rows) == 1:
            return render_template("error.html", error_message="username already taken")


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

        user_id = str(session['user_id'])

        # Ensure project name was submitted
        if not request.form.get("project_name"):
            return render_template("error.html", error_message="must provide project name")

        # store project name and description as variables
        project_name = request.form.get("project_name")
        project_description = request.form.get("project_description")


        # check if project name is already taken
        conn = create_connection("global.db")
        db = conn.cursor()
        db.execute("SELECT name FROM projects WHERE owner=? AND name=?", (user_id, project_name))
        # check if the project name already exists for someone with the same username
        exists = db.fetchall()

        if len(exists) == 1:
            return render_template("error.html", error_message="project name already exists, try another name")
        
        # connect to sqlite3 and put name and description into database
        db = conn.cursor()
        db.execute("INSERT INTO projects ('owner', 'name', 'description') VALUES (?, ?, ?)", (session['user_id'], project_name, project_description))
        rows = db.fetchall()
        conn.commit()
        conn.close()

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("create.html")

@app.route("/projects", methods=["GET", "POST"])
@login_required
def project():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # get user id:
        user_id = str(session['user_id'])

        conn = create_connection("global.db")
        db = conn.cursor()

        # store project name 
        project_name = request.form.get('name')

        # get project description
        db.execute("SELECT description FROM projects WHERE name=?", (project_name,))
        project_description = db.fetchall()
        project_description = project_description[0][0]
        
        # get project id:
        # query database for project in question:
        db.execute("SELECT id FROM projects WHERE owner=? AND name=?", (user_id, project_name))
        project_id = db.fetchall()
        refined_project_id = []
        for identification in project_id:
            refined_project_id.append(identification[0])
        print(refined_project_id)
        
        # use the name to get project details (tasks, deadlines):
        db.execute("SELECT task, deadline FROM tasks WHERE project_id=?", str(refined_project_id[0]))
        task_deadline_tuple = db.fetchall()
        conn.commit()
        conn.close()

        # turn the list of tuples into a list of lists
        task_deadlines = [list(item) for item in task_deadline_tuple]

        # we want to change the date format from yyyy-mm-dd to Month dd, yyyy:
        for task in task_deadlines:
            task_due_date = datetime.strptime(task[1], "%Y-%m-%d")
            task[1] = task_due_date.strftime("%B %d, %Y")
            print(task[1])
        
        today = date.today()
        day = today.strftime("%B %d, %Y")


        return render_template("projects.html", name=project_name, info=task_deadlines, current_day=day, desc=project_description)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("projects.html")

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():

    # User reached route via POST (clicked to add a task)
    if request.method == "POST":

        project_name = request.form.get('add_task')
        print(project_name)

        return render_template("tasks.html", project=project_name)

    # User reached route via GET (by submitting the form detailing the task)
    else:
        return redirect("/")

@app.route("/add-task", methods=["POST"])
@login_required
def add_task():

    # check if the user entered a day that already happened
    deadline = request.form.get('deadline')
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
    print(deadline)
    print(deadline_date)
    current_date = datetime.now()
    print(current_date)
    if deadline_date.date() < current_date.date():
        return render_template("error.html", error_message="please enter a due date today or after today's date")

    # get project name to help add to database
    project_name = request.form.get('confirm_add_task')

    # get user id to help add to database
    user_id = str(session['user_id'])

    # store task details 
    task_name = request.form.get('task')
    deadline = request.form.get('deadline')

    # get the project id for the selected task
    conn = create_connection("global.db")
    db = conn.cursor()
    db.execute("SELECT id FROM projects WHERE name=?", (project_name,))
    project_id = db.fetchall()
    project_id = project_id[0][0]

    # add the task to the database:
    db.execute("INSERT INTO tasks ('task', 'deadline', 'project_id') VALUES (?, ?, ?)", (task_name, deadline, project_id))

    conn.commit()
    conn.close()

    return redirect("/")





