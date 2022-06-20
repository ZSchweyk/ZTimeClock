import sqlite3
import sys
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
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

trusted_ips = ["127.0.0.1"]




@app.before_request
def limit_remote_addr():
    if request.remote_addr not in trusted_ips:
        abort(404)  # Not Found



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




@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignupForm()  # render the signup form
    if form.validate_on_submit():  # if the form is submitted and all the data is valid
        # create a new Users object, representing the user who just created an account
        new_user = Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password1.data
        )
        db.session.add(new_user)  # Add that user to the db
        try:  # try committing that change
            db.session.commit()
        # if there's an IntegrityError, that means that a user with the same email address exists. since the email
        # field is the primary key, which I defined when making the model, sqlalchemy will throw an error.

        except sqlalchemy.exc.IntegrityError:
            # technically speaking, an account with that email address already exists, so print that to the console
            # just to remind myself mostly
            print("Account already exists")
            # flash an error message that warns "Incorrect Credentials".
            # don't want to explicitly inform the user that an account with the same email address already exists.
            flash("Incorrect Credentials")
            # render the signup page again for the user to try again
            return render_template("signup.html", form=form)

        # A new user has been succesfully created.

        # clear the first name, last name, and email address fields.
        form.first_name.data = ""
        form.last_name.data = ""
        form.email.data = ""

        # Log the user in
        session.permanent = True  # create a permanent session with a lifetime of app.permanent_session_lifetime
        session["user_id"] = new_user.id  # create a cookie that stores the user's id
        # create a cookie that stores the user's flast, mainly to just display in the url
        session["flast"] = new_user.first_name[0].upper() + new_user.last_name[0].upper() + new_user.last_name[
                                                                                            1:].lower()
        # log the newly created user in, so that they don't have to retype in all their credentials to log in, after
        # creating an account.
        return redirect(url_for("home", user_flast=session["flast"]))

    # if the form isn't submitted, render the html signup page with the signup form
    return render_template("signup.html", form=form)



@app.route("/terms_and_conditions")
def terms_page():
    return render_template("terms.html")






if __name__ == '__main__':
    # db.create_all()
    app.run(host="0.0.0.0", debug=True)
