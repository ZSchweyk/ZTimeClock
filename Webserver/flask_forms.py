# Create a Form Class
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, FloatField
from wtforms.validators import InputRequired, EqualTo, ValidationError, NumberRange


class EquationForm(FlaskForm):
    equation = StringField("Enter Equation", validators=[InputRequired()])
    submit = SubmitField("Add")

    @staticmethod
    def validate_equation(form, field):
        if not ConferenceSandTable.is_equation_valid(field.data):  # ensures that the syntax is correct
            flash("Syntax Error")
            raise ValidationError("Invalid Equation")


class DrawEquationForm(FlaskForm):
    theta_max = FloatField("&theta; range (num of &pi;s)", validators=[InputRequired(), NumberRange(min=0)])
    theta_speed = FloatField("&theta; speed ratio (from 0 to 1)", validators=[InputRequired(), NumberRange(min=0, max=1)])
    scale_factor = FloatField("Scale Factor (from 0 to 1)", validators=[InputRequired(), NumberRange(min=0, max=1)])
    submit = SubmitField("Draw Equation")


class LoginForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    password1 = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Confirm Password",
                              validators=[InputRequired(), EqualTo('password1', message='Passwords must match')])
    agree = BooleanField("I agree to the ", validators=[InputRequired()])
    create = SubmitField("Create")


class ProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    save = SubmitField("Save")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Password", validators=[InputRequired()])
    new_password1 = PasswordField("New Password", validators=[InputRequired()])
    new_password2 = PasswordField("Confirm New Password", validators=[InputRequired()])