import sys
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime, timedelta
from werkzeug.urls import url_encode
from threading import Thread
from flask_forms import *
from useful_functions import *
from RequiredClasses.sqlite_wrapper import SQLiteWrapper

app = Flask(__name__)
app.secret_key = "my super secret key that no one is supposed to know"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # removes an annoying warning message
app.permanent_session_lifetime = timedelta(minutes=10)

db = SQLiteWrapper("database.db")





@app.route("/", methods=["POST", "GET"])
def login():
    form = LoginForm()  # render the login form
    if form.validate_on_submit():  # if all form data is valid on submit...
        # get the user object/row from the db whose email matches whatever was submitted
        user = Users.query.filter_by(email=form.email.data.lower()).first()

        # if the user exists in the db, and the salt + input password matches what's stored in the db, log them in
        if user is not None and sha256(user.salt + form.password.data) == user.salted_password_hash:
            # Log the user in

            # make the session permanent; erase session/cookies after app.permanent_session_lifetime, defined above
            session.permanent = True
            # create a cookie that stores the user's id so that switching between pages is easy
            session["user_id"] = user.id
            # create a cookie that stores the user's flast, to ultimately display in the url. This really won't have any
            # effect, with the exception of showing in the url so that the user knows who they are. This follows
            # GitHub's convention/style, which I really like.
            session["flast"] = user.first_name[0].upper() + user.last_name[0].upper() + user.last_name[1:].lower()
            # redirect the user to the home page, and pass in their flast into the url
            return redirect(url_for("home", user_flast=session["flast"]))
        else:
            # Wrong password, but I flash incorrect credentials to make them think that it also could be an incorrect
            # email address.
            flash("Incorrect Credentials")
            # reset the form's email field to ""
            form.email.data = ""
            # reset the form's password field to ""
            form.password.data = ""
            # render the login page again, because they entered incorrect credentials
            return render_template("login.html", form=form)
    else:
        # if the user is saved in the session/cookie, automatically redirect them to the home page, instead of manually
        # making them login again
        if "user" in session:
            # as stated above, redirect them to the home page; this essentially "logs them in"
            return redirect(url_for("home", user_flast=session["flast"]))
        # render the login page again
        return render_template("login.html", form=form)



if __name__ == '__main__':
    # db.create_all()
    app.run(host="0.0.0.0", debug=True)
