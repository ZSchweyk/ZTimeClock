from server import db
from useful_functions import *
from datetime import datetime


# Create the Users table
class Employees(db.Model):
    id = db.Column(db.String(64), primary_key=True, nullable=False, unique=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    department = db.Column(db.String(64), nullable=False)
    hourly_pay = db.Column(db.Float(), nullable=False)
    ot_allowed = db.Column(db.String(64), nullable=False)
    max_daily_hours = db.Column(db.Float(), nullable=False)
    shift_end_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, emp_id, first_name, last_name, department, hourly_pay, ot_allowed, max_daily_hours, shift_end_time):
        self.id = emp_id
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.hourly_pay = hourly_pay
        self.ot_allowed = ot_allowed
        self.max_daily_hours = max_daily_hours
        self.shift_end_time = shift_end_time

    def __repr__(self):
        return f"Employees({self.first_name} {self.last_name})"


# Create the Equations table
class EmployeeTasks(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    employee_id = db.Column(db.String(64), nullable=False)
    task_date = db.Column(db.DateTime, nullable=False)
    task = db.Column(db.String(64), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)  # 2022-03-21 13:46:34.242217 %Y-%m-%d %H:%M:%S.%f

    def __init__(self, user_id, equation):
        self.id = user_id
        self.equation = equation

    # def __repr__(self):
    #     return f"EmployeeTasks({})"



