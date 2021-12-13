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

sys.stderr = sys.stdout

# Specify the location of the program files path. Note: separate directories with a double backslash in order to overide any accidental string escape characters.
# End string with "\\"
# C:\\Users\\Zeyn Schweyk\\Documents\\MyProjects\\ZTimeClock\\
program_files_path = r"C:\Users\Zeyn Schweyk\Documents\MyProjects\ZTimeClock\\"
database_file = program_files_path + "employee_time_clock.db"

c = ZSqlite(database_file)


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


# Sets up the TKinter GUI main window.
root = Tk()
root.iconbitmap(program_files_path + "ChemtrolImage.ico")
width = root.winfo_width()
height = root.winfo_height()
# 1200, 773
root.geometry("%dx%d" % (1200, 1000))
root.resizable(width=False, height=False)
root.title("SBCS (Chemtrol)")


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


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def toggle_button(button, text_array, frame_to_clear):
    index = text_array.index(button["text"])
    new_index = 1 - index
    if new_index == 0:
        clear_frame(frame_to_clear)
    button["text"] = text_array[1 - index]
    button["command"] = enter
    # entry_widget_to_clear.delete(0, END)


def fill_frame(frame, button_names_and_funcs, frame_header, return_to_array):
    clear_frame(frame)
    frame.config(text=frame_header)
    global num_of_menu_items
    num_of_menu_items = len(button_names_and_funcs)
    for i in range(1, num_of_menu_items + 1):
        # menu_item_number = Label(frame, text=str(i) + ") ", font=("Arial", 15))
        # menu_item_number.grid(row=i-1, column=0, pady=15)
        menu_item = Button(frame, text=button_names_and_funcs[i - 1][0], command=button_names_and_funcs[i - 1][1])
        menu_item.grid(row=i - 1, column=1, pady=15)
    # ["text", function]
    if return_to_array != None:
        return_to_menu = Button(frame, text="Return to " + return_to_array[0], command=return_to_array[1])
        return_to_menu.grid(row=num_of_menu_items, column=0, columnspan=2, pady=10)


mouse_position = [root.winfo_pointerx(), root.winfo_pointery()]


def automatically_clear_frame(frame, num_of_sec):
    mouse_x = root.winfo_pointerx()
    mouse_y = root.winfo_pointery()
    # root.after(num_of_sec * 1000)


def enter():
    # global employee_menu

    # Thread(target=lambda: automatically_clear_frame(employee_menu, .5)).start()

    enter_clear_button.config(text="Clear",
                              command=lambda: toggle_button(enter_clear_button, enter_clear_button_text, employee_menu))
    root.bind("<Return>", lambda event=None: enter_clear_button.invoke())
    if id_field.get() != AdminInformation.select("AdminPassword"):
        if len(id_field.get()) != 0:
            if id_field.get()[0] == "e":
                entered_id = "E" + id_field.get()[1:]
            elif id_field.get()[0] != "E":
                entered_id = "E" + id_field.get()
            else:
                entered_id = id_field.get()
        else:
            entered_id = ""

        id_field.delete(0, END)

        clear_frame(employee_menu)

        try:
            emp = Employee(entered_id)
        except:
            Label(employee_menu, text="Incorrect Password", fg="red", font=("Arial", 20)).grid(row=0, column=0)
            return

        Label(employee_menu, text=f"Hello \n{emp.first} {emp.last}", fg="green", font=("Arial", 25)).grid(row=0,
                                                                                                           column=0)
        Label(employee_menu).grid(row=1, column=0)


        Label(employee_menu, text="Your Task/Msg for Today", font=("Arial", 16)).grid(row=2, column=0)
        Label(employee_menu, text="Fix This", font=("Arial", 16)).grid(row=3, column=0)

        Label(employee_menu).grid(row=4, column=0)

        font_tuple = ("Arial", 18)

        if emp.get_status():
            Button(employee_menu, text="Clock Out", font=font_tuple).grid(row=5, column=0)
        else:
            Button(employee_menu, text="Clock In", font=font_tuple).grid(row=5, column=0)

        Label(employee_menu).grid(row=6, column=0)

        Button(employee_menu, text="View Hours", font=font_tuple).grid(row=7, column=0)
        Label(employee_menu).grid(row=8, column=0)
        Button(employee_menu, text="View Time Off", font=font_tuple).grid(row=9, column=0)
        Label(employee_menu).grid(row=10, column=0)
        Button(employee_menu, text="Request Vacation", font=font_tuple).grid(row=11, column=0)





# The static main screen.
day_of_week = Label(root, text="", font=("Arial", 25), fg="blue", pady=45)
day_of_week.place(relx=.175, rely=0.0, anchor=N)

program_clock = Label(root, text="", font=("Arial", 25), fg="blue", pady=45)
program_clock.place(relx=.825, rely=0.0, anchor=N)

day_time_greeting = Label(root, text="", font=("Arial", 25), fg="blue")
day_time_greeting.place(relx=0.5, rely=0.13, anchor=N)

Label(root,
      text="Employee ID",
      font=("Arial", 12), fg="black").place(relx=0.5, rely=0.2, anchor=N)
# Label(root, text="2. Press \"Finish\" to complete.", font=("Arial", 12), fg="black").place(relx=0.5, rely=0.23, anchor=N)

clock()
# send_report_if_pay_day()

header = Label(root, text="SBCS\nEmployee Time Clock", font=("Times New Roman", 25, "bold"), pady=22.5)
header.place(relx=0.5, rely=0.0, anchor=N)

emp_id_entry_frame = Frame(root)
emp_id_entry_frame.place(relx=.365, rely=.255)

# Employee Widgets:
id_field_label = Label(emp_id_entry_frame, text="ID: ", font=("Arial", 20))
# id_field_label.place(relx=0.39, rely=.2725, anchor=N)
id_field_label.grid(row=0, column=1, padx=1)

id_field = Entry(emp_id_entry_frame, font=("Arial", 20), show="\u2022")
# id_field.place(relx=.50, rely=.279, width=200, height=27, anchor=N)
id_field.config(width=13)
id_field.grid(row=0, column=2, padx=10)
id_field.focus_set()

enter_clear_button_text = ["Enter", "Clear"]
enter_clear_button = Button(emp_id_entry_frame, text=enter_clear_button_text[0], command=enter, font=("Arial", 15))
# enter_clear_button.place(relx=.6, rely=.2725)
enter_clear_button.grid(row=0, column=3, padx=10)
root.bind("<Return>", lambda event=None: enter_clear_button.invoke())

employee_menu = Frame(root, padx=50, pady=25)
employee_menu.place(relx=.5, rely=.3, anchor=N)

# greeting = Label(employee_menu, text="", font=("Arial", 18))
# greeting.place(relx=.5, rely=.36, anchor=N)

# rely = .35
# rely = .375
# rely = .4


# enter_actual_clock_out_time_label = Label(employee_menu, text="", font=("Arial", 18))
# enter_actual_clock_out_time_label.place(relx=.5, rely=.425, anchor=N)
#
# enter_actual_clock_out_time_entry = Entry(employee_menu, font=("Arial", 18), width=13)
#
# actual_clock_out_time_submit_button = Button(employee_menu, text="Submit", font=("Arial", 18))
#
# time_in = Label(employee_menu, text="", font=("Arial", 10))
# time_in.place(relx=.075, rely=.4, anchor=N)
#
# time_out = Label(employee_menu, text="", font=("Arial", 10))
# time_out.place(relx=.175, rely=.4, anchor=N)
#
# forward = Button(employee_menu, text=">", font=("Arial", 15), command=lambda: print("Clicked"))
#
# backward = Button(employee_menu, text="<", font=("Arial", 15), command=lambda: print("Clicked"))
#
# current_date_mm_dd_yy = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date()
#
# day_total = Label(employee_menu, text="", font=("Arial", 20, "underline"))
# day_total.place(relx=.175, rely=.3, anchor=N)
#
# period_total = Label(employee_menu, text="", font=("Arial", 20, "underline"))
# period_total.place(relx=.825, rely=.3, anchor=N)
#
# period_days = Label(employee_menu, text="", font=("Arial", 10))
# period_days.place(relx=.775, rely=.42, anchor=N)
#
# period_daily_hours = Label(employee_menu, text="", font=("Arial", 10))
# period_daily_hours.place(relx=.875, rely=.42, anchor=N)
#
# time_duration = Label(employee_menu, text="", font=("Arial", 10))
# time_duration.place(relx=.275, rely=.4, anchor=N)
#
# employee_task_header_label = Label(employee_menu, text="", font=("Arial", 20, "underline"))
# employee_task_header_label.place(relx=.5, rely=.7, anchor=N)
#
# employee_task_label = Label(employee_menu, text="", font=("Arial", 13), wraplength=300, justify="center")
# employee_task_label.place(relx=.5, rely=.77, anchor=N)

z_time_clock_label = Label(root, text="ZTimeClock Ver 1.01", font=("Arial", 10))
z_time_clock_label.place(relx=.945, rely=.97, anchor=N)

# Creates the mainloop of the application to constantly check for input events like clicking a button or entering text in a entry widget.
root.mainloop()
