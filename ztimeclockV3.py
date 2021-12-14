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
program_files_path = r"C:\Users\Zeyn Schweyk\Documents\MyProjects\ZTimeClock\\"
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
               command=lambda: view_hours(emp, day=datetime.today(), clock_in_out=False)).grid(row=7, column=0)
        Label(self.employee_menu).grid(row=8, column=0)
        Button(self.employee_menu, text="View Time Off", font=font_tuple).grid(row=9, column=0)
        Label(self.employee_menu).grid(row=10, column=0)
        Button(self.employee_menu, text="Request Vacation", font=font_tuple).grid(row=11, column=0)

    def enter_clear(self, emp_id):
        if self.enter_clear_button["text"] == "Enter":
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


    @staticmethod
    def clear_frames(frames):
        for frame in frames:
            frame.destroy()
            # for widget in frame.winfo_children():
            #     widget.destroy()

















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




if __name__ == "__main__":
    ZTimeClockApp()
    root.mainloop()

