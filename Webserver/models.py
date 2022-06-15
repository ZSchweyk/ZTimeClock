from server import db
from useful_functions import *
from datetime import datetime


# Create the Users table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    salt = db.Column(db.String(64), unique=True, nullable=False)
    salted_password_hash = db.Column(db.String(64), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now)  # %Y-%m-%d %H:%M:%S.%f

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email.lower()
        self.salt = sha256(self.email)
        self.salted_password_hash = sha256(self.salt + password)

    def __repr__(self):
        return "<Name %r>" % (self.first_name + " " + self.last_name)


# Create the Equations table
class Equations(db.Model):
    row = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    id = db.Column(db.Integer, nullable=False)
    equation = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)  # 2022-03-21 13:46:34.242217 %Y-%m-%d %H:%M:%S.%f

    def __init__(self, user_id, equation):
        self.id = user_id
        self.equation = equation

    def __repr__(self):
        return "<Equation %r>" % self.equation




