import sys

import time
from math import pi
import sqlalchemy.exc
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_encode
import pickle
from threading import Thread

from flask_forms import *
from useful_functions import *

from ServerPi.conference_sand_table_class import ConferenceSandTable
from ServerPi.main import draw_equation

app = Flask(__name__)
app.secret_key = "my super secret key that no one is supposed to know"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # removes an annoying warning message
app.permanent_session_lifetime = timedelta(minutes=10)

# Initialize the Database
db = SQLAlchemy(app)
from models import *  # models imports db above, explaining why I have this import here. It avoids circular import

# errors.

print("CREATING A TABLE OBJECT!!!")
table = ConferenceSandTable("172.17.21.2")


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


@app.route("/<user_flast>/home", methods=["POST", "GET"])
def home(user_flast):
    # if the user already exists in the session dictionary...the user manually types in ipaddr:5000/FLast/home
    if "user_id" in session:
        form = EquationForm()  # render the equations form
        # retrieve the user object who's id matches what's in the session
        user = Users.query.filter_by(id=session["user_id"]).first()
        # find all row objects in the Equations table belonging to that user
        rows = Equations.query.filter_by(id=session["user_id"]).all()
        equations = [row.equation for row in rows]  # obtain a list of the pure equations
        if form.validate_on_submit():  # if the form is submitted and the data is valid...
            print("Validated")
            # create a new equation for that user
            new_equation = Equations(
                user_id=session["user_id"],
                equation=remove_spaces(form.equation.data)
            )
            # test if that new equation already exists. if not...
            if new_equation.equation not in equations:
                db.session.add(new_equation)  # add that new equation to the db session
                db.session.commit()  # commit it (permanently modify the db)
                form.equation.data = ""  # clear the equation field
                # redirect the user to the same page; home
                return redirect(url_for("home", user_flast=session["flast"], form=None))
            else:  # if the new equation DOES exist...
                flash("Equation already exists.")  # flash an error warning that the equation already exists
        # if the form is NOT submitted, render the home.html template for the logged in user.
        return render_template(
            'home.html',
            user=user,
            form=form,
            equations=equations
        )
    else:  # if the user is not in the session
        return redirect(url_for("login"))  # redirect the user to the login page


@app.route("/<user_flast>/restart")
def restart(user_flast):
    # Reboot client pi, then server pi
    global table
    table.server.send_to_radius_client("Reboot Sequence")
    assert table.server.receive_from_radius_client() == "close server and reboot server pi", "Received packet incorrectly"
    table.server.close_server()
    table.server.send_to_radius_client("Reboot")
    os.system("sudo reboot")


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))


@app.route("/<user_flast>/equations", methods=["POST", "GET"])
def equations(user_flast, eq_num=1):

    if "user_id" in session:
        form = DrawEquationForm()
        user_id = session["user_id"]
        user = Users.query.filter_by(id=user_id).first()
        args = request.args
        # the default parameter ensures that if the argument can't be converted into an int, it defaults to 1.
        eq_num = args.get("eq_num", default=eq_num, type=int)

        # if delete_equation:
        #     rows = Equations.query.filter_by(id=user.id).all()
        #     equation = rows[eq_num - 1].equation
        #     Equations.query.filter_by(id=user.id, equation=equation).delete()
        #     db.session.commit()
        #     return redirect(url_for("home", user_flast=session["flast"]))

        if form.validate_on_submit():
            rows = Equations.query.filter_by(id=user.id).all()
            equation = rows[eq_num - 1].equation

            # def run_client():
            #     os.system('sshpass -p dpea7266! ssh pi@conference-sand-table-v2-radius-pi.local "python3 ~/projects/ConferenceSandTable/ClientPi/main.py"')
            #
            # Thread(target=run_client).start()

            global table
            draw_equation(
                table=table,
                equation=equation,
                theta_range=form.theta_max.data * pi,
                theta_speed=form.theta_speed.data,
                scale_factor=form.scale_factor.data
            )

            print("About to redirect back to this page...")
            return redirect(url_for("equations", user_flast=session["flast"], eq_num=eq_num))

        rows = Equations.query.filter_by(id=user.id).all()
        if 0 < eq_num <= len(rows):
            equation = rows[eq_num - 1].equation
            return render_template("equations.html", user=user, equation=equation, eq_num=eq_num, form=form)
        return "Please add at least 1 equation"
    return redirect(url_for("login"))


@app.route("/<user_flast>/edit-equation")
def edit_equation(user_flast):
    pass


# @app.route("/<user_flast>/home/draw-equation")
# def draw_equation(user_flast):
#     pass

@app.route("/<user_flast>/home/delete-equation", methods=["POST", "GET"])
def stop_drawing(user_flast):
    global table
    table.ENABLED = False
    time.sleep(.2)
    table.ENABLED = True
    return redirect(url_for("home", user_flast=session["flast"]))


@app.route("/<user_flast>/home/delete-equation", methods=["POST", "GET"])
def delete_equation(user_flast, eq_num=1):
    if "user_id" in session:
        user_id = session["user_id"]
        user = Users.query.filter_by(id=user_id).first()
        args = request.args
        # the default parameter ensures that if the argument can't be converted into an int, it defaults to 1.
        eq_num = args.get("eq_num", default=eq_num, type=int)
        rows = Equations.query.filter_by(id=user.id).all()
        equation = rows[eq_num - 1].equation
        Equations.query.filter_by(id=user.id, equation=equation).delete()
        db.session.commit()
        return redirect(url_for("home", user_flast=session["flast"]))


@app.route("/<user_flast>/logout")
def logout(user_flast):
    # clear the users cookies, specifically their id and flast.
    session.pop("user_id", None)
    session.pop("flast", None)
    # redirect the user to the login page
    return redirect(url_for("login"))


@app.route("/<user_flast>/profile")
def profile(user_flast):
    form = ProfileForm()
    if form.validate_on_submit():
        # Update the user's fields
        pass

    if "user_id" in session:
        user_id = session["user_id"]
        user = Users.query.filter_by(id=user_id).first()
        return render_template("profile.html", user=user)
    return redirect(url_for("login"))


@app.route("/terms_and_conditions")
def terms_page():
    return render_template("terms.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# def loop(start_string):
#     previous = start_string
#     while True:
#         new = sha256(previous)
#         print(new)
#         previous = new


if __name__ == '__main__':
    # db.create_all()
    app.run(host="0.0.0.0", debug=True)
