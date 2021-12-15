from ast import Index
from sqlite3.dbapi2 import Error, PARSE_DECLTYPES
from tkinter import *
from tkinter import ttk
import tkinter.ttk
from tkinter import messagebox
import sqlite3
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import random
from calendar import month, monthrange, week
from typing import AsyncContextManager
import smtplib
import mimetypes
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
# from openpyxl import load_workbook
import xlsxwriter as xl
import json
from tkinter.filedialog import askdirectory, asksaveasfile, asksaveasfilename
import os
from threading import Thread
import sys
from employee_class import ZSqlite, Employee
from UsefulFunctions import *

sys.stderr = sys.stdout

# Specify the location of the program files path. Note: separate directories with a double backslash in order to overide any accidental string escape characters.
# End string with "\\"
# C:\\Users\\Zeyn Schweyk\\Documents\\MyProjects\\ZTimeClock\\
program_files_path = r"C:\Users\ZSchw\Documents\MyProjects\ZTimeClock\\"
database_file = program_files_path + "employee_time_clock.db"

# Sets up the TKinter GUI main window.
root = Tk()
root.iconbitmap(program_files_path + "ChemtrolImage.ico")
width = root.winfo_width()
height = root.winfo_height()
# 1200, 773
root.geometry("%dx%d" % (1200, 1000))
root.resizable(width=False, height=False)
root.title("SBCS (Chemtrol)")

# The static main screen.
day_of_week = Label(root, text="", font=("Arial", 25), fg="blue", pady=45)
day_of_week.place(relx=.175, rely=0.0, anchor=N)

program_clock = Label(root, text="", font=("Arial", 25), fg="blue", pady=45)
program_clock.place(relx=.825, rely=0.0, anchor=N)

day_time_greeting = Label(root, text="", font=("Arial", 25), fg="blue")
day_time_greeting.place(relx=0.5, rely=0.13, anchor=N)

# Label(root, text="2. Press \"Finish\" to complete.", font=("Arial", 12), fg="black").place(relx=0.5, rely=0.23, anchor=N)
def clock():
    hour = time.strftime("%I")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    am_pm = time.strftime("%p")
    day = time.strftime("%A")
    current_date = time.strftime("%x")
    program_clock.config(text=hour + ":" + minute + ":" + second + " " + am_pm)
    day_of_week.config(text=day[:3] + " " + current_date)

    global day_time_greeting
    hour = int(time.strftime("%H"))
    if hour < 12:
        string = "Good Morning"
    elif hour < 18:
        string = "Good Afternoon"
    else:
        string = "Good Evening"

    day_time_greeting.config(text=string)

    root.after(1000, clock)

clock()

header = Label(root, text="SBCS\nEmployee Time Clock", font=("Times New Roman", 25, "bold"), pady=22.5)
header.place(relx=0.5, rely=0.0, anchor=N)

# A class that handles selecting admin information such as email, password, admin usernmane ... etc.
class AdminInformation:
    # Method that selects a certain field value from a field name (property).
    @staticmethod
    def select(field_property):
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        field_value = \
            c.execute("SELECT FieldValue FROM admin_information WHERE FieldProperty = @0",
                      (field_property,)).fetchone()[0]
        conn.commit()
        conn.close()
        if field_value is None:
            return ""
        else:
            return field_value

class ZTimeClockApp:
    def __init__(self):
        self.make_emp_id_entry_frame()
        self.fill_emp_id_entry_frame()

    def make_employee_menu_frame(self):
        self.employee_menu = Frame(root)
        self.employee_menu.place(relx=.5, rely=.3, anchor=N)

    def fill_employee_menu_frame(self, emp: Employee):
        Label(self.employee_menu, text=f"Hello \n{emp.first} {emp.last}", fg="green", font=("Arial", 25)).grid(row=0,
                                                                                                          column=0)
        Label(self.employee_menu).grid(row=1, column=0)

        Label(self.employee_menu, text="Your Task/Msg for Today", font=("Arial", 16)).grid(row=2, column=0)
        Label(self.employee_menu, text="Fix This", font=("Arial", 16)).grid(row=3, column=0)

        Label(self.employee_menu).grid(row=4, column=0)

        font_tuple = ("Arial", 18)

        if emp.get_status():
            Button(self.employee_menu, text="Clock Out", font=font_tuple).grid(row=5, column=0)
        else:
            Button(self.employee_menu, text="Clock In", font=font_tuple).grid(row=5, column=0)

        Label(self.employee_menu).grid(row=6, column=0)

        Button(self.employee_menu, text="View Hours", font=font_tuple,
               command=lambda: self.view_hours(emp, day=datetime.today(), clock_in_out=False)).grid(row=7, column=0)
        Label(self.employee_menu).grid(row=8, column=0)
        Button(self.employee_menu, text="View Time Off", font=font_tuple).grid(row=9, column=0)
        Label(self.employee_menu).grid(row=10, column=0)
        Button(self.employee_menu, text="Request Vacation", font=font_tuple).grid(row=11, column=0)

    def create_frames_for_view_hours(self):
        self.day_hours_frame = Frame(root)
        self.middle_greeting_frame = Frame(root)
        self.period_hours_frame = Frame(root)

        daily_and_period_frame_rely = .25

        self.day_hours_frame.place(relx=.053, rely=daily_and_period_frame_rely)

        self.middle_greeting_frame.place(relx=.5, rely=.3, anchor=N)

        self.period_hours_frame.place(relx=.687, rely=daily_and_period_frame_rely)
        return

    def view_hours(self, emp_obj: Employee, day=datetime.today(), clock_in_out=False):
        self.create_frames_for_view_hours()
        self.clear_frames([self.employee_menu, self.emp_id_entry_frame, self.day_hours_frame, self.period_hours_frame])
        self.create_frames_for_view_hours()


        if clock_in_out:
            emp_obj.clock_in_or_out()

        if day == datetime.today():
            Label(self.day_hours_frame, text="Today's", font=("Arial", 20, "underline")).grid(row=0, column=0, columnspan=5)
        else:
            Label(self.day_hours_frame, text=day.strftime("%m/%d/%y"), font=("Arial", 20, "underline")).grid(row=0, column=0,
                                                                                                        columnspan=5)

        records_and_total_hours = emp_obj.get_records_and_hours_for_day(day.strftime("%m/%d/%y"), "%m/%d/%y")
        total_day_hours = records_and_total_hours[1]
        records = records_and_total_hours[0]

        time_in = "Time In\n------------------\n"
        time_out = "Time Out\n------------------\n"
        duration = "Duration\n------------------\n"

        for time_in_str, time_out_str, duration_str in records:
            time_in += (time_in_str if time_in_str != "" else " " * 11) + "\n"
            time_out += (time_out_str if time_out_str != "" else " " * 11) + "\n"
            duration += (duration_str if duration_str != "" else " " * 8) + "\n"

        Label(self.day_hours_frame, text=f"Total Hours: {round(total_day_hours, 2)}", font=("Arial", 20, "underline")).\
            grid(row=1, column=0, columnspan=5)

        Label(self.day_hours_frame).grid(row=2, column=1)
        Label(self.day_hours_frame).grid(row=3, column=1)

        Label(self.day_hours_frame, text=time_in, font=("Arial", 10)).grid(row=4, column=0)
        Label(self.day_hours_frame, text="           ").grid(row=4, column=1)
        Label(self.day_hours_frame, text=time_out, font=("Arial", 10)).grid(row=4, column=2)
        Label(self.day_hours_frame, text="           ").grid(row=4, column=3)
        Label(self.day_hours_frame, text=duration, font=("Arial", 10)).grid(row=4, column=4)

        Label(self.middle_greeting_frame, text=f"Here are your hours\n{emp_obj.first} {emp_obj.last}", fg="green",
              font=("Arial", 25)).grid(row=0, column=0, columnspan=2)
        Label(self.middle_greeting_frame, text=" ").grid(row=1, column=0)
        Label(self.middle_greeting_frame, text=" ").grid(row=2, column=0)
        Label(self.middle_greeting_frame, text=" ").grid(row=3, column=0)
        backward = Button(self.middle_greeting_frame, text="<", width=5, font=("Arial", 20, "bold"),
                          command=lambda: self.view_hours(emp_obj, day=day - timedelta(days=1), clock_in_out=False))
        backward.grid(row=4, column=0)
        forward = Button(self.middle_greeting_frame, text=">", width=5, font=("Arial", 20, "bold"),
                         command=lambda: self.view_hours(emp_obj, day=day + timedelta(days=1), clock_in_out=False))
        forward.grid(row=4, column=1)

        if day == datetime.today():
            print("Disabled")
            forward.config(state=DISABLED)
        else:
            print("Normal")
            forward.config(state=NORMAL)

        Label(self.middle_greeting_frame).grid(row=5, column=0, columnspan=2)

        Button(self.middle_greeting_frame,
               text="Back to Menu",
               font=("Arial", 20, "bold"),
               command=lambda: show_employee_menu(emp_obj)
               ).grid(row=6, column=0, columnspan=2)

        if day.strftime("%m/%d/%y") in getPeriodFromDateString(datetime.today().strftime("%m/%d/%Y"), "%m/%d/%Y"):
            Label(self.period_hours_frame, text="Current", font=("Arial", 20, "underline")).grid(row=0, column=0,
                                                                                            columnspan=7)
        else:
            Label(self.period_hours_frame,
                  text=day.strftime("%m/%d/%y"),
                  font=("Arial", 20, "underline")
                  ).grid(row=0, column=0, columnspan=7)

        period_records, period_total_hours = emp_obj.get_records_and_daily_hours_for_period(day.strftime("%m/%d/%Y"),
                                                                                            "%m/%d/%Y")
        Label(self.period_hours_frame,
              text=f"Period's Total Hours: {round(period_total_hours, 2)}",
              font=("Arial", 20, "underline")
              ).grid(row=1, column=0, columnspan=7)

        date_label = "Date\n------------------\n"
        total_period_hours_label = "Total Hours\n------------------\n"

        for date_str, hours in period_records:
            date_label += date_str + "\n"
            total_period_hours_label += str(round(hours, 3)) + "\n"

        Label(self.period_hours_frame, text=" ").grid(row=2, column=0)

        Label(self.period_hours_frame, text="           ").grid(row=3, column=0)
        Label(self.period_hours_frame, text=date_label, font=("Arial", 10)).grid(row=3, column=1)
        Label(self.period_hours_frame, text="           ").grid(row=3, column=2)
        Label(self.period_hours_frame, text=total_period_hours_label, font=("Arial", 10)).grid(row=3, column=3)

    def enter_clear(self, emp_id):
        if self.enter_clear_button["text"] == "Enter":
            # self.make_employee_menu_frame()
            # self.fill_employee_menu_frame(Employee(emp_id))
            root.bind("<Return>", lambda event=None: self.enter_clear_button.invoke())
            if emp_id != AdminInformation.select("AdminPassword"):
                if len(emp_id) != 0:
                    if emp_id[0] == "e":
                        entered_id = "E" + emp_id[1:]
                    elif emp_id[0] != "E":
                        entered_id = "E" + emp_id
                    else:
                        entered_id = emp_id
                else:
                    entered_id = ""

                self.id_field.delete(0, END)
                self.make_employee_menu_frame()
                self.clear_frames([self.employee_menu])

                try:
                    emp = Employee(entered_id)
                except:
                    Label(self.employee_menu, text="Incorrect Password", fg="red", font=("Arial", 20)).grid(row=0, column=0)
                    return
                self.fill_employee_menu_frame(emp)
            self.enter_clear_button.config(text="Clear",
                                  command=lambda: self.clear_frames([self.employee_menu]))




















    def make_emp_id_entry_frame(self):
        self.emp_id_entry_frame = Frame(root)
        self.emp_id_entry_frame.place(relx=.363, rely=.22)

    def fill_emp_id_entry_frame(self):
        Label(self.emp_id_entry_frame,
              text="Enter Employee ID",
              font=("Arial", 12), fg="black").grid(row=0, column=0, columnspan=3)

        # Employee Widgets:
        id_field_label = Label(self.emp_id_entry_frame, text="ID: ", font=("Arial", 20))
        # id_field_label.place(relx=0.39, rely=.2725, anchor=N)
        id_field_label.grid(row=1, column=0, padx=1)

        self.id_field = Entry(self.emp_id_entry_frame, font=("Arial", 20), show="\u2022")
        # id_field.place(relx=.50, rely=.279, width=200, height=27, anchor=N)
        self.id_field.config(width=12)
        self.id_field.grid(row=1, column=1, padx=10)
        self.id_field.focus_set()

        self.enter_clear_button_text = ["Enter", "Clear"]
        self.enter_clear_button = Button(self.emp_id_entry_frame,
                                    text=self.enter_clear_button_text[0],
                                    command=lambda: self.enter_clear(self.id_field.get()),
                                    font=("Arial", 15))
        # enter_clear_button.place(relx=.6, rely=.2725)
        self.enter_clear_button.grid(row=1, column=2, padx=10)
        root.bind("<Return>", lambda event=None: self.enter_clear_button.invoke())

    def delete_emp_id_entry_frame(self):
        self.clear_frames([self.emp_id_entry_frame])

    @staticmethod
    def clear_frames(frames):
        for frame in frames:
            for widget in frame.winfo_children():
                widget.destroy()
            # frame.destroy()




if __name__ == "__main__":
    ZTimeClockApp()
    root.mainloop()

