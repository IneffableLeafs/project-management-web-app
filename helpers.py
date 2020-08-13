import os
from functools import wraps
from flask import redirect, render_template, request, session
import sqlite3
from sqlite3 import Error


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def create_connection(file):
    connection = None

    try:
        conn = sqlite3.connect(file)
    except Error as e:
        print(e)

    return conn