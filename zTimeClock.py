
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
#from openpyxl import load_workbook
import xlsxwriter as xl
import json
from tkinter.filedialog import askdirectory, asksaveasfile, asksaveasfilename
import os
import sys
sys.stderr = sys.stdout


# Specify the location of the program files path. Note: separate directories with a double backslash in order to overide any accidental string escape characters.
# End string with "\\"
# C:\\Users\\Zeyn Schweyk\\Documents\\MyProjects\\ZTimeClock\\
program_files_path = "C:\\Programming\\MyProjects\\ZTimeClock\\"
database_file = program_files_path + "employee_time_clock.db"

# A class that handles selecting admin information such as email, password, admin usernmane ... etc.
class AdminInformation:
    # Method that selects a certain field value from a field name (property).
    @staticmethod
    def select(field_property):
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        field_value = c.execute("SELECT FieldValue FROM admin_information WHERE FieldProperty = @0", (field_property,)).fetchone()[0]
        conn.commit()
        conn.close()
        if field_value is None:
            return ""
        else:
            return field_value


# Sets up the TKinter GUI main window.
root = Tk()
root.iconbitmap(program_files_path + "ChemtrolImage.ico")
width= root.winfo_width()
height= root.winfo_height()
# 1200, 773
root.geometry("%dx%d" % (1200, 1000))
root.resizable(width=False, height=False)
root.title("SBCS (Chemtrol)")

# A standalone function that checks if a given timestamp in a given format is valid. Returns a boolean.
def validate_timestamp(time_string, format):
    try:
        datetime.strptime(time_string, format)
    except ValueError:
        return False
    else:
        return True

# This function inserts an employee's clock out request into the "Request" column in the database if they forget to clock out on the same day they clocked in at.
# It also handles validating the entered timestamp as well.
def insert_request(emp_id, time_string, format, clocked_in_time):
    if validate_timestamp(time_string, format) :
        conn = sqlite3.connect(database_file)
        c = conn.cursor()

        clock_out = datetime.strptime(time_string, format)
        clock_in = datetime.strptime(clocked_in_time, "%H:%M:%S")

        if clock_out.time() >= clock_in.time():
            formatted_time = datetime.strptime(time_string, format).strftime("%H:%M:%S")
            max_row = c.execute(f"SELECT row, ClockIn, Request FROM time_clock_entries WHERE empID = '{emp_id}' ORDER BY row DESC LIMIT 1;").fetchone()
            c.execute(f"UPDATE time_clock_entries SET ClockOut = 'FORGOT', Request = '{max_row[1][:10]} {formatted_time}' WHERE row = '{max_row[0]}';")
            conn.commit()
            conn.close()
            # if max_row[2] is None:
            messagebox.showinfo("Thank You", f"Your timestamp request of \"{time_string}\" has been sent to management for approval.")
            clear([greeting, enter_actual_clock_out_time_label], [enter_actual_clock_out_time_entry, actual_clock_out_time_submit_button], True, None)
            id_field.delete(0, "end")
            button.config(command=enter) 

            # else:
            #     replaced = datetime.strptime(max_row[2][11:], "%H:%M:%S").strftime("%I:%M:%S %p")
            #     messagebox.showinfo("Successful", f"Your timestamp request of \"{time_string}\" has been replaced by your previous request of \"{replaced}\", and has been sent to management for approval.")
        else:
            messagebox.showerror("Clock Out < Clock In", "Entry must be greater than or equal to your clock in timestamp.")
    else:
        messagebox.showerror("Wrong Time Format", "Enter timestamp in the format of \"HH:MM:SS am/pm\"")
        
    return

# Sends an email from a gmail account, and provides the option to include a file to attach to the email. If the file_path parameter is an emtpy string, no file will be attached.
def send_email(sender, password, recipient, body, subject, file_path):
    #Make file_path = "" if you don't want to send an attachment.
    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message.set_content(body)

    if file_path != "":
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type, mime_subtype = mime_type.split('/')
        with open(file_path, 'rb') as file:
            message.add_attachment(file.read(),
            maintype=mime_type,
            subtype=mime_subtype,
            filename=file_path.split("\\")[-1])
        

    mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
    mail_server.set_debuglevel(1)
    mail_server.login(sender, password)
    mail_server.send_message(message)
    mail_server.quit()

def send_email_with_db_attachment(sender, password, recipient, body, subject, file_path):
    data = MIMEMultipart()
    data["From"] = sender
    data["To"] = recipient
    data["Subject"] = subject
    data.attach(MIMEText(body, 'plain'))
    attachment = open(file_path, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % file_path.split("\\")[-1])
    data.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender, password)
    text = data.as_string()
    s.sendmail(sender, recipient, text)
    s.quit()
    return
    

    
# Checks if a given date is a payday. Note: 15th or last day of the month = end_of_pay_period. It will return True if the date is a weekday and the end_of_pay_period, a Friday but the end_of_pay_period is on the following weekend (1 or 2 days after it), or a Thursday and the end_of_pay_period is a Saturday.
def is_this_a_pay_day(date_in, format):
    date_in = datetime.strptime(date_in, format)
    last_day_of_month = monthrange(date_in.year, date_in.month)[1]

    # check if the date is the 15th, the end of the month, and it's a weekday
    if (date_in.day == 15 or date_in.day == last_day_of_month) and date_in.weekday() <= 4:
        return True
    else:
        # check if the date is <= the 15th, or the end of the month, by two days or less, and it's a Friday
        if ((date_in.day >= 13 and date_in.day <= 15) or (date_in.day >= last_day_of_month - 2 and date_in.day <= last_day_of_month)) and date_in.weekday() == 4: 
            return True
        else:
            return False

def get_database_copy():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    array_of_dicts = []
    array_of_sheet_names = []

    tables_and_columns = {
        "employees": ["ID", "FirstName", "LastName", "Department", "HourlyPay", "OTAllowed", "MaxDailyHours"],
        "time_clock_entries": ["row", "empID", "ClockIn", "ClockOut", "Request"],
        "employee_tasks": ["task_id", "employee_id", "task_date", "task"],
        "admin_information": ["FieldProperty", "FieldValue"]
    }

    for table_name, table_columns in tables_and_columns.items():
        array_of_sheet_names.append(table_name)
        table_dict = {}
        for column in table_columns:
            column_values = [value[0] for value in c.execute(f"SELECT {column} FROM {table_name}")]
            table_dict[column] = column_values
        array_of_dicts.append(table_dict)
        # array_of_dicts.append(dict())

    conn.commit()
    conn.close()

    
    return array_of_dicts, array_of_sheet_names


# CreateExcelFile.create_excel_file_with_multiple_sheets(program_files_path + "CopyOfDatabase.xlsx", array_of_dicts, array_of_sheet_names)

# send_email(AdminInformation.select("EmailAddress"), AdminInformation.select("EmailAddressPassword"), AdminInformation.select("EmailAddress"), "Hello Zeyn,\n\nThis message should have an excel file attached that is an exact copy of the database.\n\nSincerely,\nZeyn", "testing copy of database", program_files_path + "CopyOfDatabase.xlsx")


def merge_2_dicts(dict1, dict2):
    res = {**dict1, **dict2}
    return res

# This function checks every hour that the program is open if the given date is a pay day using is_this_a_pay_day. If it is, it sends an email with a Excel File Report attached to the admin.
def send_report_if_pay_day():
    today = datetime.today()
    last_day_of_month = monthrange(today.year, today.month)[1]

    if (today.day == 15 or today.day == last_day_of_month) and int(datetime.now().strftime("%H")) >= 18:
        # final_list = []
        report_dict = [{
            "ID": [],
            "FLast": [],
            "Total Pay": [],
            "Total Hours": [],
            "Regular Hours": [],
            "Overtime Hours": [],
            "Double Time Hours": [],
            "Regular Pay": [],
            "Overtime Pay": [],
            "Double Time Pay": []
        }]
        beginning_of_pay_period = ""
        end_of_pay_period = today.strftime("%m/%d/%y")

        if today.day == 15:
            all_emp_ids = get_all_emp_ids()
            beginning_of_pay_period = f"{str(today.month)}/01/{str(today.year)[2:4]}"
        else:
            all_emp_ids = get_all_emp_ids()
            beginning_of_pay_period = f"{str(today.month)}/16/{str(today.year)[2:4]}"

        for emp_id in all_emp_ids:
            emp_dict = calculate_employee_pay(beginning_of_pay_period, end_of_pay_period, "%m/%d/%y", str(emp_id[0]))
            for key, value in emp_dict.items():
                report_dict[0][key].append(value)
            
            # final_list.append({"EmpID": str(emp_id[0]), "FLast": emp_id[1][0] + emp_id[2]} | calculate_employee_pay(beginning_of_pay_period, end_of_pay_period, "%m/%d/%y", str(emp_id[0])))

        period_1 = datetime.strptime(get_period_days(0)[0][1], "%m/%d/%y").strftime("%m%d%y")
        period_2 = datetime.strptime(get_period_days(0)[0][1], "%m/%d/%y").strftime("%m/%d/%y")
        complete_file_path = program_files_path + period_1 + "_Pay_Period_Report_and_DB_Copy.xlsx"

        copy_of_db_as_dict_array, array_of_sheet_names = get_database_copy()
        CreateExcelFile.create_excel_file_with_multiple_sheets(complete_file_path, report_dict + copy_of_db_as_dict_array, [f"{period_1}_Pay_Period_Report"] + array_of_sheet_names)

        # json_string = json.dumps(final_list, indent=4)
        # filename = program_files_path + "z_time_clock_report.json"
        # jsonFile = open(filename, "w")
        # jsonFile.write(json_string)
        # jsonFile.close()
        body = f"""Time Clock Report,

Below is the ZTimeClock report for this pay period, {period_2}, and an identical copy of the database as of {datetime.now().strftime("%m/%d/%Y at %I:%M:%S %p")}. Please reply to this email for any questions.

Happy Payrolling :)

Sincerely,
ZTimeClock
        """
        subject = f"ZTimeClock {period_2} Pay Period Report for Chemtrol"
        send_email(AdminInformation.select("EmailAddress"), AdminInformation.select("EmailAddressPassword"), AdminInformation.select("EmailAddress"), body, subject, complete_file_path)

        os.remove(complete_file_path)

# I'm not sure how to send a database file. It has a problem with the following line of code:
# mime_type, mime_subtype = mime_type.split('/')
# and says that it is NoneType.

    root.after(60*60*1000, send_report_if_pay_day)
    return

# Fetches all employee ids from the database. This is often useful for looping through every single employee.
def get_all_emp_ids():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    ids = c.execute("SELECT ID, FirstName, LastName FROM employees ORDER BY LastName").fetchall()

    conn.commit()
    conn.close()
    return ids

# This functions displays a specific greeting based on the time of day.
def greeting_time():
    global day_time_greeting
    string = ""
    hour = int(time.strftime("%H"))
    if hour < 12:
        string = "Good Morning"
    elif hour < 18:
        string = "Good Afternoon"
    else:
        string = "Good Evening"

    day_time_greeting.config(text=string)
    day_time_greeting.after(1000, greeting_time)

# Subtracts two timestamps as strings in the following format, "%Y-%m-%d %H:%M:%S", and returns the difference.
def subtract_time(t2, t1):
    d1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S").timestamp()
    d2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S").timestamp()
    return d2 - d1

# Adds a list of timestamps in the format of "%H:%M:%S" and returns the sum.
def add_time_stamps(array):
    d1 = datetime.strptime(array[0], "%H:%M:%S")
    for str in range(1, len(array)):
        d1 += datetime.strptime(str, "%H:%M:%S")
    return d1

# Formats a given number of seconds to hh:mm:ss, and returns the result as a string.
def format_seconds_to_hhmmss(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)

# Fetches the current time, date, and day of the week, and displays that on the screen. This function waits every 1 second until it calls itself again, as the displayed time changes every second.
def clock():
    hour = time.strftime("%I")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    am_pm = time.strftime("%p")
    day = time.strftime("%A")
    current_date = time.strftime("%x")
    program_clock.config(text=hour + ":" + minute + ":" + second + " " + am_pm)
    day_of_week.config(text=day[:3] + " " + current_date)
    program_clock.after(1000, clock)

# Grabs all the week days up until and including the weekday of the passed in date.
def getWeekDays(todays_date, format):
    array_of_week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_day = datetime.strptime(todays_date, format).weekday()
    today = datetime.strptime(todays_date, format)
    day_of_week = today
    result_array = []
    for i in range(week_day + 1):
        day_of_week = str(today - timedelta(days=week_day-i))
        result_array.append([array_of_week_days[i], day_of_week[5:7] + "/" + day_of_week[8:10] + "/" + day_of_week[0:4]])
    return result_array

# Creates and returns list of dates in the interval [start, end], both inclusive, as a string array.
def getArrayOfDates(start, end, entered_format, result_format):
    start_date = datetime.strptime(start, entered_format)
    end_date = datetime.strptime(end, entered_format)
    result_array = [start_date.strftime(result_format)]
    while start_date < end_date:
        start_date += timedelta(days=1)
        result_array.append(start_date.strftime(result_format))
    return result_array

# Adds/subtracts a given number of dates to a specific date.
def add_subtract_days(todays_date, format, num_of_days):
    today = datetime.strptime(todays_date, format)
    new_date = str(today + timedelta(days=num_of_days))
    new_date = new_date[5:7] + "/" + new_date[8:10] + "/" + new_date[0:4]
    return new_date

# Grabs today's weekday and date, and returns a 2 element list containing the weekday and date respectively.
def getTodaysWeekDayAndDate():
    today = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d")
    array_of_week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_day = array_of_week_days[today.weekday()]
    todays_date = str(today.date())
    #todays_date = todays_date[5:7] + "/" + todays_date[8:10] + "/" + todays_date[0:4]
    todays_date = todays_date[:10]
    result = [week_day, todays_date]
    return result

# Returns the weekday of a specific date as a string.
def getWeekDayFromDate(entered_date, format):
    array_of_week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_day = datetime.strptime(entered_date, format).weekday()
    return array_of_week_days[week_day]

# Returns a date in another specified format.
def change_date_format(entered_date, input_format, output_format):
    initial_format = datetime.strptime(entered_date, input_format)
    new_format = initial_format.strftime(output_format)
    return new_format


# This function is enabled when an employee (or admin) clicks the submit button to clock in or clock out. It serves as the main function to display all the employee
# and admin info that pops up on the screen. Also, this function deals with the logic to clock in or clock out, or display the message that an employee forgot to clock out
# and modifies the database accordingly. It also selects a random greeting message every time an employee clocks out or in.
def enter():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    global greeting
    global time_in
    global time_out
    global time_duration
    global button
    button.config(text="Clear", command=lambda: clear([greeting, time_in, time_out, time_duration, day_total, period_total, period_days, period_daily_hours, employee_task_header_label, employee_task_label, enter_actual_clock_out_time_label], [forward, backward, enter_actual_clock_out_time_entry, actual_clock_out_time_submit_button], True, None))

    
    #Add the following as parameters to the clear function above.
    #Labels: employee_list_label, employee_hours_label, start_date_label, end_date_label
    #Buttons: employee_hours_button, employee_start_date, employee_end_date

    
    #root.bind("<Return>", lambda event=None: button.invoke())
    root.bind("<Return>", lambda event=None: button.invoke())
    
        


    if id_field.get() != AdminInformation.select("AdminPassword"):
        global entered_id
        if len(id_field.get()) != 0:
            if id_field.get()[0] == "e":
                entered_id = "E" + id_field.get()[1:]
            elif id_field.get()[0] != "E":
                entered_id = "E" + id_field.get()
            else:
                entered_id = id_field.get()
        else:
            entered_id = ""

        
        emp_record = c.execute("SELECT FirstName, LastName FROM employees WHERE ID = @0", (entered_id,)).fetchone()
        if emp_record is not None and len(id_field.get()) != 0:
            name = str(emp_record[0]) + " " + str(emp_record[1])

            time_clock_entries_record = c.execute("SELECT row, ClockIn, ClockOut FROM time_clock_entries WHERE empID = '" + entered_id + "' ORDER BY row DESC LIMIT 1;").fetchone()

            inOrOut = ""
            greeting_text = []
            
            if time_clock_entries_record is None or (time_clock_entries_record[1] is not None and time_clock_entries_record[2] is not None):
                #Clocked IN
                inOrOut = "In"
                greeting_text = ["Welcome", "Greetings", "Hello", "Have a great day", "Have a productive day", "Have a fun work day"]
                c.execute("INSERT INTO time_clock_entries(empID, ClockIn) VALUES('" + str(entered_id) + "', DateTime('now', 'localtime'));")
                conn.commit()
            elif time_clock_entries_record[1] is not None and time_clock_entries_record[2] == None:
                #Clocked OUT
                inOrOut = "Out"
                greeting_text = ["Goodbye", "Have a nice day", "See you later", "Have a wonderful day", "Thank you for your great work"]

                if time_clock_entries_record[1][:10] == getTodaysWeekDayAndDate()[1]:
                    c.execute("UPDATE time_clock_entries SET ClockOut = DateTime('now', 'localtime') WHERE row = " + str(time_clock_entries_record[0]) + ";")
                    conn.commit()
                else:

                    rand = random.randint(0, len(greeting_text)-1)
                    conn.commit()
                    conn.close()

                    clocked_in_time = datetime.strptime(time_clock_entries_record[1][11:], "%H:%M:%S")

                    enter_actual_clock_out_time_entry.delete(0, "end")
                    enter_actual_clock_out_time_entry.place(relx=.46, rely=.65, anchor=N)

                    actual_clock_out_time_submit_button.config(command=lambda: insert_request(entered_id, enter_actual_clock_out_time_entry.get(), "%I:%M:%S %p", clocked_in_time.strftime("%H:%M:%S")))
                    actual_clock_out_time_submit_button.place(relx=.55, rely=.6375)                    
                    
                    return greeting.config(text=name + ",\nyou forgot to clock out after your last clock in on " + getWeekDayFromDate(time_clock_entries_record[1][:10], "%Y-%m-%d") + ", " + datetime.strptime(time_clock_entries_record[1][:10], "%Y-%m-%d").strftime("%m/%d/%Y") + " at " + clocked_in_time.strftime("%I:%M:%S %p") + ".\n\nEnter the time you clocked out at in the following format \"HH:MM:SS am/pm\", in order to be able to clock in again. Your request will be sent to management for approval.", fg="red")
                    

            rand = random.randint(0, len(greeting_text)-1)

            forward.place(relx=.52, rely=.6, anchor=N)
            backward.place(relx=.48, rely=.6, anchor=N)

            global current_date_mm_dd_yy
            current_date_mm_dd_yy = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date()
            calculate_and_display_day_totals(0, entered_id)

            greeting.config(text=greeting_text[rand] + "\n" + name + "\n\nYou are clocked " + inOrOut, fg="green")

            calculate_and_display_period_totals_for_employees(entered_id)

            #Retreive task from database table and display it on the screen
            fetch_and_display_task(entered_id)
            
            id_field.delete(0, END)
        else:
            greeting.config(text="Incorrect Password", fg="red")

        conn.commit()
        conn.close()
    else:
        id_field.delete(0, END)
        greeting.config(text="Hello Admin!", fg="green")

        #main_menu.config(text="Main Menu")
        main_menu.place(relx=.5, rely=.425, anchor=N)

        global main_menu_buttons
        main_menu_buttons = [["Employees", employee_codes_function], ["Assign Tasks", assign_tasks_function], ["Period Totals", period_totals_function], ["Historical Totals", historical_totals_function], ["Resolve Requests", resolve_requests], ["Send Copy of DB", send_copy_of_db]]

        global employee_codes_child_buttons
        employee_codes_child_buttons = [["Add New Employee", employee_codes__add_new_employee_function], ["Edit", employee_codes__edit_function], ["Delete", employee_codes__delete_function], ["View", employee_codes__view_function]]

        fill_frame(main_menu, main_menu_buttons, "Main Menu", None)



        conn.commit()
        conn.close()

# This function fetches and displays an employees task based on the global variable (date) defined in the enter function. The idea of this function is that when an
# employee toggles between certain days, the displayed task will also change accordingly.
def fetch_and_display_task(id):
    task = selectTask(id, str(current_date_mm_dd_yy), "%Y-%m-%d")
    if current_date_mm_dd_yy == datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date():
        employee_task_header_label.config(text="Today's Task")
    else:
        employee_task_header_label.config(text=str(current_date_mm_dd_yy)[5:7] + "/" + str(current_date_mm_dd_yy)[8:10] + "/" + str(current_date_mm_dd_yy)[2:4] + " Task")

    employee_task_label.config(text=task)
    return

# Calculuates and displays the period totals for an employee. The period total calculation depends on the number of total hours an employee was clocked in for, and also
# takes into account their daily lunch breaks.
def calculate_and_display_period_totals_for_employees(id):
    dates = getPeriodFromDateString(str(current_date_mm_dd_yy), "%Y-%m-%d")
    current_period_dates = getPeriodDays()

    displayed_dates = "Date\n-----------\n"
    displayed_daily_hours = "Total Hours\n-----------\n"
    period_hours_sum = 0
    for adate in dates:
        displayed_dates += adate + "\n"
        #period_hours_sum += getRawTotalEmployeeHours(adate, "%m/%d/%y", id_field.get())
        #displayed_daily_hours += str(getRawTotalEmployeeHours(adate, "%m/%d/%y", id_field.get())) + "\n"
        period_hours_sum += getTotalDailyHoursAccountingForBreaks(adate, "%m/%d/%y", id)
        displayed_daily_hours += str(getTotalDailyHoursAccountingForBreaks(adate, "%m/%d/%y", id)) + "\n"
    if dates[0] == current_period_dates[0]:
        period_total.config(text="Current\nPeriod's Total Hours: " + str(round(period_hours_sum, 3)))
    else:
        #print(current_date_mm_dd_yy - dates[-1])

        last_day_of_period = ""
        current_date = str(current_date_mm_dd_yy)
        day = int(current_date[8:10])
        month = current_date[5:7]
        year = current_date[:4]
        num_of_days_in_month = monthrange(current_date_mm_dd_yy.year, int(month))[1]
        #mm/dd/yy
        if day >= 1 and day < 16:
            last_day_of_period = f"{month}/15/{year}"
        else:
            last_day_of_period = f"{month}/{num_of_days_in_month}/{year}"
        period_total.config(text=last_day_of_period + "\nPeriod's Total Hours: " + str(round(period_hours_sum, 3)))

    period_days.config(text=displayed_dates)
    period_daily_hours.config(text=displayed_daily_hours)

# This function toggles to the previous day that an employee sees, and displays that day's totals.
def previous_day_totals():
    # conn = sqlite3.connect(database_file)
    # c = conn.cursor()

    

    # global current_date_mm_dd_yy
    # global entered_id
    # current_date_mm_dd_yy -= timedelta(days=1)

    # time_in_out_records = c.execute("SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = '" + str(entered_id) + "' AND ClockIn LIKE '%" + str(current_date_mm_dd_yy) + "%';").fetchall()

    # print_time_in_records = ""
    # print_time_out_records = ""
    # print_duration_records = ""
    # total_seconds = 0
    # #times_array = []
    # for record in time_in_out_records:
    #     print_time_in_records += datetime.strptime(record[0][11:], "%H:%M:%S").strftime("%I:%M:%S %p") + "\n"
                
    #     if record[1] is not None:
    #         print_time_out_records += datetime.strptime(record[1][11:], "%H:%M:%S").strftime("%I:%M:%S %p") + "\n"
    #         t1 = datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S").timestamp()
    #         t2 = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S").timestamp()
    #         total_seconds += t1 - t2
    #         diff = format_seconds_to_hhmmss(t1 - t2)
    #         print_duration_records += diff + "\n"

    #     else:
    #         print_time_out_records += "\n"

    # time_in.config(text="\nTime In\n-----------\n" + print_time_in_records)

    # time_out.config(text="\nTime Out\n-----------\n" + print_time_out_records)

    # #time_duration.config(text="\nDuration\n-----------\n" + print_duration_records + "\nDay Total " + format_seconds_to_hhmmss(total_seconds))
    # time_duration.config(text="\nDuration\n-----------\n" + print_duration_records)

    # day_total.config(text=str(current_date_mm_dd_yy)[5:7] + "/" + str(current_date_mm_dd_yy)[8:10] + "/" + str(current_date_mm_dd_yy)[:4] + " Total - " + format_seconds_to_hhmmss(total_seconds))
    
    # conn.commit()
    # conn.close()
    global entered_id
    calculate_and_display_day_totals(-1, entered_id)
    fetch_and_display_task(entered_id)
    calculate_and_display_period_totals_for_employees(entered_id)
    return

# This function toggles to the next day that an employee sees, and displays that day's totals.
def next_day_totals():
    global entered_id
    calculate_and_display_day_totals(1, entered_id)
    fetch_and_display_task(entered_id)
    calculate_and_display_period_totals_for_employees(entered_id)
    return

# This function deals with a specific part of the information that an employee sees when they clock in or out. It calculates and displays a specific day's hourly totals
# accounting for breaks, and also gives a break down of exactly all of their clock in and out times. It also displays whether or not an employee forgot to clock out at
# the end of a certain day. In the calculations, if a employee forgot to clock out, the duration for that record (clock in and clock out) will equal 0. This will be
# modified once the admin changes this through the main menu.
def calculate_and_display_day_totals(num_added_days, id):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    global current_date_mm_dd_yy
    

    if current_date_mm_dd_yy + timedelta(days=num_added_days) >= datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date():
        forward.config(state=DISABLED)
        #return
    else:
        forward.config(state=NORMAL)

    current_date_mm_dd_yy += timedelta(days=num_added_days)

    time_in_out_records = c.execute("SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = @0 AND ClockIn LIKE @1;", (id, '%' + current_date_mm_dd_yy.strftime("%Y-%m-%d") + '%',)).fetchall()

    print_time_in_records = ""
    print_time_out_records = ""
    print_duration_records = ""
    total_seconds = 0
    #times_array = []
    for record in time_in_out_records:
        print_time_in_records += datetime.strptime(record[0][11:], "%H:%M:%S").strftime("%I:%M:%S %p") + "\n"
                
        if record[1] is not None:
            if record[1] != "FORGOT":
                print_time_out_records += datetime.strptime(record[1][11:], "%H:%M:%S").strftime("%I:%M:%S %p") + "\n"
                t1 = datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S").timestamp()
                t2 = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S").timestamp()
                total_seconds += t1 - t2
                diff = format_seconds_to_hhmmss(t1 - t2)
                print_duration_records += diff + "\n"
            else:
                print_time_out_records += "FORGOT\n"

        else:
            print_time_out_records += "\n"

    time_in.config(text="\nTime In\n-----------\n" + print_time_in_records)

    time_out.config(text="\nTime Out\n-----------\n" + print_time_out_records)

    #time_duration.config(text="\nDuration\n-----------\n" + print_duration_records + "\nDay Total " + format_seconds_to_hhmmss(total_seconds))
    time_duration.config(text="\nDuration\n-----------\n" + print_duration_records)

    if current_date_mm_dd_yy == datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date():
        #format_seconds_to_hhmmss(total_seconds), this returns the raw duration that an employee spends at work.
        # The below function, getTotalDailyHoursAccountingForBreaks, shows the employee their total paid hours, which is calculated by considering the break hours and total day duration.
        day_total.config(text="Today's\nTotal Hours: " + str(getTotalDailyHoursAccountingForBreaks(str(current_date_mm_dd_yy), "%Y-%m-%d", id)))
    else:
        day_total.config(text=current_date_mm_dd_yy.strftime("%m/%d/%y") + "\nTotal Hours: " + str(getTotalDailyHoursAccountingForBreaks(str(current_date_mm_dd_yy), "%Y-%m-%d", id)))
    
    conn.commit()
    conn.close()
    return


# This function clears the contents of label, button, and entry widgets. It is mainly used to clear the screen between employees.
def clear(all_labels, all_buttons, bool, reset_commands):
    #all_labels = [greeting, time_in, time_out, time_duration, employee_list_label, employee_hours_label]

    for label in all_labels:
        clear_widget_text(label)

    for single_button in all_buttons:
        single_button.place_forget()

    if reset_commands is not None:
        for row in reset_commands:
            row[0].config(command=row[1])

    #employee_hours_button.place_forget()
    if bool:
        button.config(text="Enter", command=enter)
        root.bind("<Return>", lambda event=None: button.invoke())
    
    clear_frame(main_menu)
    main_menu.place_forget()

# This function fills the labelframe (a widget that contains other widgets) in a certain format. It mainly allows me to easily and quickly create a menu or submenu with
# any number of buttons. It also deals with the function that each button is linked with.
def fill_frame(frame, button_names_and_funcs, frame_header, return_to_array):
    clear_frame(frame)
    frame.config(text=frame_header)
    global num_of_menu_items
    num_of_menu_items = len(button_names_and_funcs)
    for i in range(1, num_of_menu_items + 1):
        #menu_item_number = Label(frame, text=str(i) + ") ", font=("Arial", 15))
        #menu_item_number.grid(row=i-1, column=0, pady=15)
        menu_item = Button(frame, text=button_names_and_funcs[i-1][0], command=button_names_and_funcs[i-1][1])
        menu_item.grid(row=i-1, column=1, pady=15)
    #["text", function]
    if return_to_array != None:
        return_to_menu = Button(frame, text="Return to " + return_to_array[0], command=return_to_array[1])
        return_to_menu.grid(row=num_of_menu_items, column=0, columnspan=2, pady=10)

# Clears the main_menu frame that the admin sees. This happens when the admin goes through the main menu.
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# A function that returns and displays all the buttons in the main menu, as well as all the functions each button is linked to. This is necessary because lots of other
# sub menu options contain a button that allows the admin to go back to the main menu, and that return button is linked to this function.
def main_menu_function():
    fill_frame(main_menu, main_menu_buttons, "Main Menu", None)
    return

# Returns and displays all the buttons in the employee codes button within the main_menu. Basically, a function here is necessary because the "employee codes" button 
# acts as a folder for other buttons, and must be referred to later.
def employee_codes_function():
    clear_frame(main_menu)
    #main_menu.config(text="Employee Codes")
    fill_frame(main_menu, employee_codes_child_buttons, "Main Menu > Employees", ["Main Menu", main_menu_function])
    # return_to_main_menu = Button(main_menu, text="Return to Main Menu", command=lambda: fill_frame(main_menu, main_menu_buttons, "Main Menu"))
    # return_to_main_menu.grid(row=num_of_menu_items, column=0, columnspan=2)
    global_confirmation_text.set("")
    return

# Fills the main menu with buttons related to assigning tasks. Because the "assign tasks" option is a folder for other buttons, it is helpful to create a function for it
# to call later.
def assign_tasks_function():
    fill_frame(main_menu, [["Assign by Department", assign_tasks__by_department], ["Assign by Employee", assign_tasks__by_employee]], "Main Menu > Assign Tasks", ["Main Menu", main_menu_function])
    return

# This function displays the screen that the admin sees when assigning tasks to employees by their department. It contains checkboxes, buttons, entries, and more, and
# sends all that info to another function to deal with inserting/updating employee tasks.
def assign_tasks__by_department():
    clear_frame(main_menu)
    main_menu.config(text = "Main Menu > Assign Tasks > By Department")
    assign_tasks_by_department_label = Label(main_menu, text="Department: ", font=("Arial", 15), pady=3, padx=10)
    assign_tasks_by_department_label.grid(row=0, column=0, sticky="e")

    #tkinter.ttk.Separator(main_menu, orient=VERTICAL).grid(row=0, column=1, rowspan=6, sticky="nsw", padx=10)

    none_department = StringVar()
    MG_department = StringVar()
    MK_department = StringVar()
    PD_department = StringVar()
    CL_department = StringVar()

    departments = ["None", "MG", "MK", "PD", "CL"]
    department_strvars = [none_department, MG_department, MK_department, PD_department, CL_department]

    next_row = 0
    for department, strvar, counter in zip(departments, department_strvars, range(len(departments))):
        Checkbutton(main_menu, text=department, variable=strvar, onvalue=department, offvalue="").grid(row=counter, column=1, sticky="w", pady=3)
        if counter == len(departments) - 1:
            next_row = counter + 1

    Label(main_menu, text="Seperate entries with (s) by commas and no spaces", font=("Arial", 8), pady=10, anchor=CENTER).grid(row=next_row, column=0, columnspan=2, sticky="ew")

    exclude_label = Label(main_menu, text="ID(s) to Exclude: ", font=("Arial", 15), pady=3, padx=10)
    exclude_label.grid(row=next_row+1, column=0, sticky="e")

    exclude_entry_widget = Entry(main_menu)
    exclude_entry_widget.grid(row=next_row+1, column=1, sticky="w")

    tkinter.ttk.Separator(main_menu, orient=HORIZONTAL).grid(row=next_row+2, column=0, columnspan=2, padx=10)

    #root.unbind("<Return>")

    task_label = Label(main_menu, text="Task: ", font=("Arial", 15), pady=3, padx=10)
    task_label.grid(row=next_row+3, column=0, sticky="e")

    task_entry = Text(main_menu, width=15, height=2)
    task_entry.grid(row=next_row+3, column=1, sticky="w")

    date_label = Label(main_menu, text="Date(s) mm/dd/yyyy: ", font=("Arial", 15), pady=3, padx=10)
    date_label.grid(row=next_row+4, column=0, sticky="e")

    date_entry = Entry(main_menu)
    date_entry.grid(row=next_row+4, column=1, sticky="w")

    submit_button = Button(main_menu, text="Assign Tasks", command=lambda: assign_tasks__by_department_submit_button_function(department_strvars, exclude_entry_widget.get(), task_entry.get("1.0","end-1c"), date_entry.get()))
    submit_button.grid(row=next_row+5, column=0, columnspan=2, pady=3)

    return_to_employee_codes = Button(main_menu, text="Return to Assign Tasks", command=assign_tasks_function)
    return_to_employee_codes.grid(row=next_row+6, column=0, columnspan=2, pady=3)

    return

# This function funnels all the input from the assign_tasks__by_department() function and updates the database to reflect those changes. Note: employees are only allowed to have
# one task per day, so if the admin attempts to assign another task for a specific employee on a given day, this function makes sure that that employee only has 
# one task for that day. In this case, this function will overide that employee's previous task with the new task.
def assign_tasks__by_department_submit_button_function(strvars, excluded_emps, single_task_string, date_string):

    if single_task_string == "" or date_string == "" or all(var.get() == "" for var in strvars):
        messagebox.showerror("Empty field(s)!", "No tasks were assigned. 'Task', 'Date', or 'Department' fields were blank.")
        return

    conn = sqlite3.connect(database_file)
    c = conn.cursor()



    employees_array = []
    excluded_emps = excluded_emps.split(",")
    date_string = date_string.split(",")
    for strvar in strvars:
        value = strvar.get()
        if value != "":
            if value == "None":
                all_matching_emp_ids = c.execute("SELECT ID FROM employees WHERE Department = '" + value + "' OR Department = '';").fetchall()
            else:
                all_matching_emp_ids = c.execute("SELECT ID FROM employees WHERE Department = '" + value + "';").fetchall()
            for matching_id in all_matching_emp_ids:
                if str(matching_id[0]) not in excluded_emps:
                    employees_array.append(str(matching_id[0]))

    replaced = ""

    for emp in employees_array:
        for single_date in date_string:
            try:
                datetime.strptime(single_date, "%m/%d/%Y")
            except ValueError:
                messagebox.showerror("Wrong Date Format!", "Format must be in (mm/dd/yyyy)")
                return
            
            today = datetime.strptime(getTodaysWeekDayAndDate()[1], "%Y-%m-%d")
            
            if datetime.strptime(single_date, "%m/%d/%Y") < today:
                messagebox.showerror("Cannot Assign Tasks on Past Dates!", "Check your dates such that each one is greater than or equal to today's date.")
                return

            old_date = single_date.split("/")
            if len(old_date[0]) < 2:
                old_date[0] = "0" + old_date[0]
            if len(old_date[1]) < 2:
                old_date[1] = "0" + old_date[1]
            single_date = "/".join(old_date)

            task_id_for_matching_emp_and_date = c.execute("SELECT task_id, task FROM employee_tasks WHERE employee_id = '" + emp + "' AND task_date = '" + single_date + "';").fetchone()
            name = c.execute(f"SELECT FirstName, LastName FROM employees WHERE ID = '{emp}';").fetchone()
            if task_id_for_matching_emp_and_date != None:
                c.execute("UPDATE employee_tasks SET task = '" + single_task_string + "' WHERE task_id = '" + str(task_id_for_matching_emp_and_date[0]) + "';")
                replaced += f"{name[0]} {name[1]}'s task, '{task_id_for_matching_emp_and_date[1]}', on {single_date} was over-written.\n\n"
            else:
                sql_statement = f"INSERT INTO employee_tasks(employee_id, task_date, task) VALUES('{emp}', '{single_date}', '{single_task_string}')"
                c.execute(sql_statement)
                replaced += f"A task for {name[0]} {name[1]} on {single_date} was added.\n\n"
    
    messagebox.showinfo("Successful!", "Your tasks have been succesfully assigned.\n\n" + replaced)

    conn.commit()
    conn.close()
    return

# Returns the screen that the admin sees when assigning tasks by employee. It has entry, button, and label widgets in order to do so.
def assign_tasks__by_employee():
    clear_frame(main_menu)
    main_menu.config(text = "Main Menu > Assign Tasks > By Employee")
    Label(main_menu, text="Seperate entries labeled with \"(s)\" by commas and no spaces", font=("Arial", 8), pady=10, anchor=CENTER).grid(row=0, column=0, columnspan=2, sticky="ew")

    emp_label = Label(main_menu, text="Employee ID(s): ", font=("Arial", 15), pady=10, padx=10)
    emp_label.grid(row=1, column=0, sticky="e")

    emp_id_entry = Entry(main_menu)
    emp_id_entry.grid(row=1, column=1, sticky="w")

    task_label = Label(main_menu, text="Task: ", font=("Arial", 15), pady=10, padx=10)
    task_label.grid(row=2, column=0, sticky="e")

    task_entry = Text(main_menu, width=15, height=2)
    task_entry.grid(row=2, column=1, sticky="w")

    date_label = Label(main_menu, text="Date(s) mm/dd/yyyy: ", font=("Arial", 15), pady=10, padx=10)
    date_label.grid(row=3, column=0, sticky="e")

    date_entry = Entry(main_menu)
    date_entry.grid(row=3, column=1, sticky="w")

    submit_button = Button(main_menu, text="Assign Tasks", command=lambda: assign_tasks__by_employee_submit_button(emp_id_entry.get(), task_entry.get("1.0","end-1c"), date_entry.get()))
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)

    return_to_employee_codes = Button(main_menu, text="Return to Assign Tasks", command=assign_tasks_function)
    return_to_employee_codes.grid(row=5, column=0, columnspan=2, pady=10)
    return

# Funnels all the info collected from the screen, which was created by the assign_tasks__by_employee() function, and updates the database. It only allows employees to have
# one task per day, so if necessary, it will overide certain tasks if the admin says so.
def assign_tasks__by_employee_submit_button(id_string, task, date_string):
    if task == "" or date_string == "" or id_string == "":
        messagebox.showerror("Empty field(s)!", "No tasks were assigned. 'Task', 'Date', or 'Department' fields were blank.")
        return

    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    date_array = date_string.split(",")
    id_array = id_string.split(",")

    all_ids = c.execute("SELECT ID FROM employees;").fetchall()
    
    print(all_ids)
    successful_ids = []
    unsuccessful_ids = []
    for single_id in id_array:
        all_types = (int, str)
        for type in all_types:
            try:
                if (type(single_id),) in all_ids:
                    successful_ids.append(type(single_id))
                else:
                    unsuccessful_ids.append(type(single_id))
                break
            except:
                pass
    
    successful_dates = []
    unsuccessful_dates = []
    for single_date in date_array:
        if validate_timestamp(single_date, "%m/%d/%Y"):
            old_date = single_date.split("/")
            if len(old_date[0]) < 2:
                old_date[0] = "0" + old_date[0]
            if len(old_date[1]) < 2:
                old_date[1] = "0" + old_date[1]
            single_date = "/".join(old_date)
            successful_dates.append(single_date)
        else:
            unsuccessful_dates.append(single_date)


    print("Successful Ids:", successful_ids)
    print("Unsuccessful Ids:", unsuccessful_ids)

    successful = "Successful:\n"
    successful_over_written = "\tOver-written:\n"
    successful_updated = "\tNew:\n"
    unsuccessful = "Unsuccessful:\n"
    unsuccessful_ids_str = "\tIDs:\n"
    unsuccessful_dates_str = "\tDates:\n"

    for single_id in successful_ids:
        for single_date in successful_dates:
            task_from_table = c.execute("SELECT task_id, task FROM employee_tasks WHERE employee_id = @0 AND task_date = @1;", (single_id, single_date,)).fetchone()
            
            name = c.execute(f"SELECT FirstName, LastName FROM employees WHERE ID = @0;", (single_id,)).fetchone()
            if task_from_table != None:
                c.execute("UPDATE employee_tasks SET task = @0 WHERE task_id = @1;", (task, task_from_table[0],))
                successful_over_written += f"\t\t\"{name[0]} {name[1]}\" task > \"{task_from_table[1]}\" on \"{single_date}\" < over-written.\n"
            else:
                c.execute("INSERT INTO employee_tasks(employee_id, task_date, task) VALUES(@0, @1, @2);", (single_id, single_date, task,))
                successful_updated += f"\t\t\"{name[0]} {name[1]}\" > task added on \"{single_date}\"\n"
    
    for id in unsuccessful_ids:
        unsuccessful_ids_str += f"\t\t\"{str(id)}\"\n"
    for date in unsuccessful_dates:
        unsuccessful_dates_str += f"\t\t\"{date}\"\n"

    conn.commit()
    conn.close()
    message = successful + successful_over_written + successful_updated + unsuccessful + unsuccessful_ids_str + unsuccessful_dates_str
    messagebox.showinfo("Report", message)
    return

# This function returns the period days of a certain period. It passes in a number and generates the period days, both displayed and calculated as a tuple.
# For instance, if the argument = 0, it will fetch the period days of today's period. If the argument = 1, it will fetch the period days of the period after the current one.
# Negative numbers do the same thing, except they go back periods. This function is useful for when the admin toggles between the reports and summaries of certain
# periods. Note: there is a difference between displayed and calculated period days. Calculated period days are strictly all the days between either the 1st - 15th or the 16th - last_day_of_month.
# This is used in all the calculations for period totals, both for employees and the admin. Displayed period days are similar to the calculated period days, however, they 
# take into account for whether or not the last day of the period is a weekday or not. If the last day of the period lands on a weekend, the displayed period days will
# end at the last weekday before the end of the period. The displayed period days are useful when displaying the period days in a report, and the calculated period days are useful when
# looping through every single day in a period from the 1st - 15th or the 16th - last_day_of_month to do payroll calculations.
def get_period_days(num):
    today = datetime.today()
    day = ""
    additional_months = 0
    if 0 < today.day < 16:
        if num >= 0:
            additional_months = int(num / 2)
        elif num / 2 != int(num / 2):
            additional_months = int(num / 2 - 1)
        else:
            additional_months = int(num / 2)

        if num % 2 == 0:
            day = "01"
        else:
            day = "16"
    else:
        if num >= 0:
            additional_months = int((num + 1) / 2)
        elif num / 2 != int(num / 2):
            additional_months = int((num + 1) / 2)
        else:
            additional_months = int((num + 1) / 2 - 1)

        if num % 2 == 0:
            day = "16"
        else:
            day = "01"

    temporary_date = datetime.strptime((today + relativedelta(months=additional_months)).strftime("%m/%d/%Y"), "%m/%d/%Y").strftime("%m/%d/%Y")
    beginning_of_period = temporary_date[:3] + day + temporary_date[5:]

    end_of_period = datetime.strptime(beginning_of_period, "%m/%d/%Y")
    while not is_this_a_pay_day(end_of_period.strftime("%m/%d/%Y"), "%m/%d/%Y"):
        end_of_period += timedelta(days=1)

    last_day_of_calculated_period_days = 0
    if day == "16":
        # mm/dd/yy
        last_day_of_calculated_period_days = str(monthrange(int(beginning_of_period[6:]), int(beginning_of_period[:2]))[1])
    else:
        last_day_of_calculated_period_days = "15"

    # (displayed_period_boundaries, calculated_pay_days_from_1_to_15)
    
    return ((datetime.strptime(beginning_of_period, "%m/%d/%Y").strftime("%m/%d/%y") , end_of_period.strftime("%m/%d/%y")), tuple(getArrayOfDates(beginning_of_period, end_of_period.strftime("%m/%d/%Y")[:3] + last_day_of_calculated_period_days + end_of_period.strftime("%m/%d/%Y")[5:], "%m/%d/%Y", "%m/%d/%y")))

# This function allows the admin to toggle between periods to view the payroll information for all the employees.
def next_previous_period(num):
    global period_count
    period_count += num
    return display_period_totals(get_period_days(period_count))

# Displays the payroll totals for a given range of dates. Loops through each employee's timeclock entries for every single date and performs calculations. This also creates
# an excel file report with the same information.
def display_period_totals(period_days_input):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    displayed_period_range, period_days = period_days_input

    Label(main_menu, text=displayed_period_range[0] + " - " + displayed_period_range[1], font=("Arial", 8, "bold"), pady=10).grid(row=1, column=5)

    try:
        global next_period
        if period_days_input == get_period_days(0):
            next_period.config(state=DISABLED)
        else:
            next_period.config(state=NORMAL)
    except:
        pass

    all_ids = get_all_emp_ids()

    label_headers = [
        "ID\n---------------\n",
        "FLast\n---------------\n",
        "TotalPay\n---------------\n",
        "TotalHours\n---------------\n",
        "RegHours\n---------------\n",
        "OvertimeHours\n---------------\n",
        "DoubleTimeHours\n---------------\n",
        "RegPay\n---------------\n",
        "OvertimePay\n---------------\n",
        "DoubleTimePay\n---------------\n"
    ]

    label_dictionary = {
        "ID": [],
        "FLast": [],
        "Total Pay": [],
        "Total Hours": [],
        "Regular Hours": [],
        "Overtime Hours": [],
        "Double Time Hours": [],
        "Regular Pay": [],
        "Overtime Pay": [],
        "Double Time Pay": []
    }

    for record in all_ids:
        id = record[0]
        
        dictionary_info = calculate_employee_pay(period_days[0], period_days[-1], "%m/%d/%y", str(id))
        for key, value in dictionary_info.items():
            label_dictionary[key].append(str(value))


    for counter, value, header in zip(range(len(label_dictionary)), label_dictionary.values(), label_headers):
        text = header + "\n"
        for elem in value:
            text += elem + "\n"
        Label(main_menu, text=text, font=("Arial", 8), pady=10, padx=10).grid(row=2, column=counter)

    return_to_main_menu = Button(main_menu, text="Return to Main Menu", font=("Arial", 8), command=main_menu_function)
    return_to_main_menu.grid(row=3, column=5, pady=10)

    period_1 = datetime.strptime(displayed_period_range[1], "%m/%d/%y").strftime("%m%d%y")
    period_2 = datetime.strptime(displayed_period_range[1], "%m/%d/%y").strftime("%m/%d/%y")
    file_name = program_files_path + period_1 + "Pay_Period_Report.xlsx"
    body = f"""Time Clock Report,

Below is the ZTimeClock report for the following pay period, {period_2}. Please reply to this email for any questions.

Happy Payrolling :)

Sincerely,
ZTimeClock
    """
    subject = f"ZTimeClock {period_2} Pay Period Report for Chemtrol"
    create_file = Button(main_menu, text="Generate Excel Report and Email Myself", font=("Arial", 8), pady=10, command=lambda: CreateExcelFile.create_excel_file(file_name, label_dictionary, email_report_bool = True, sender_address = AdminInformation.select("EmailAddress"), sender_pswd = AdminInformation.select("EmailAddressPassword"), receiver_address = AdminInformation.select("EmailAddress"), subject = subject, body = body))
    create_file.grid(row=1, column=9)

    

    conn.commit()
    conn.close()
    return


def send_copy_of_db():
    copy_of_db_as_dict_array, array_of_sheet_names = get_database_copy()
    # CreateExcelFile.create_excel_file_with_multiple_sheets(program_files_path + "Copy_Of_Database.xlsx", copy_of_db_as_dict_array, array_of_sheet_names)
    
    current_time = datetime.now().strftime("%m/%d/%Y at %I:%M:%S %p")

    body = f"""Time Clock Report,

Below is an identical copy of the ZTimeClock database for Chemtrol's Employee Timeclock System, as of {current_time}. Please reply to this email for any questions.

Good luck :)

Sincerely,
ZTimeClock
        """
    subject = f"ZTimeClock Copy of Chemtrol's Employee Timeclock Database as of {current_time}"
    send_email_with_db_attachment(AdminInformation.select("EmailAddress"), AdminInformation.select("EmailAddressPassword"), AdminInformation.select("EmailAddress"), body, subject, database_file)

    # os.remove(program_files_path + "Copy_Of_Database.xlsx")

    messagebox.showinfo("Successful!", "An email containing an identical copy of the database has been sent to yourself.")

    return

# A class to create excel files in different formats. Although there is only one method here, more can be created if necessary depending on the different formats the
# admin prefers.
class CreateExcelFile:

    @staticmethod
    def dict_to_list(dictionary):
        dict_values_to_list = []
        for value in dictionary.values():
            dict_values_to_list.append(value)
        
        data = []
        for i in range(len(dict_values_to_list[0])):
            sub_array = []
            for j in range(len(dict_values_to_list)):
                sub_array.append(dict_values_to_list[j][i])
            data.append(sub_array)

        columns = []
        for label in dictionary.keys():
            columns.append({"header": label})
        
        return data, columns
    
    @staticmethod
    def create_excel_file_with_multiple_sheets(complete_file_path, array_of_dicts, sheet_names):
        if len(array_of_dicts) != len(sheet_names):
            return
        splitted = complete_file_path.split("\\")

        file_name = splitted[-1]
        file_path = "\\".join(splitted[0:len(splitted) - 1])

        workbook = xl.Workbook(file_path + "\\" + file_name)

        sheet_name_counter = 0
        for dictionary in array_of_dicts:
            data, columns = CreateExcelFile.dict_to_list(dictionary)
            # Create a subsheet and fill it with the data from the dictionary.
            sheet = workbook.add_worksheet(sheet_names[sheet_name_counter])
            sheet_name_counter += 1

            abc = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")

            sheet.add_table("A1:" + abc[len(columns) - 1] + str(len(data) + 2), {"data": data, "columns": columns})

        
        workbook.close()








        os.path.join(file_path, file_name)




    def create_excel_file(complete_file_path, dictionary, email_report_bool = False, sender_address = False, sender_pswd = False, receiver_address = False, subject = False, body = False):
        """
        file_name is the name of the Excel file WITH the extension.

        The labels of the passed in dictionary will become the columns of the Excel table.
        Expects that the values in the dictionary are lists. All values must have equally sized lists.
        """
        data, columns = CreateExcelFile.dict_to_list(dictionary)

        # first_char_of_filename = CreateExcelFile.every_index(complete_file_path, "\\")[-1] + 1
        splitted = complete_file_path.split("\\")

        file_name = splitted[-1]
        file_path = "\\".join(splitted[0:len(splitted) - 1])
        workbook = xl.Workbook(complete_file_path)
        sheet = workbook.add_worksheet()

        abc = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")

        sheet.add_table("A1:" + abc[len(columns) - 1] + str(len(data) + 1), {"data": data, "columns": columns})

        workbook.close()
        
        os.path.join(file_path, file_name)
        
        if email_report_bool:
            try:
                send_email(sender_address, sender_pswd, receiver_address, body, subject, complete_file_path)
            except:
                messagebox.showinfo("Error!", "Could not attach file due to an unexpected error.")
                return
            os.remove(complete_file_path)
            messagebox.showinfo("Successful", "Report has been sent!")


    # @staticmethod
    # def create_excel_file_with_table(file_name, dictionary):
    #     """
    #     file_name is the name of the Excel file without the extension. Include full file path using the character "\\"

    #     The labels of the passed in dictionary will become the columns of the Excel table.
    #     Expects that the values in the dictionary are lists. All values must have equally sized lists.
    #     """
    #     dict_values_to_list = []
    #     for value in dictionary.values():
    #         dict_values_to_list.append(value)
        
    #     data = []
    #     for i in range(len(dict_values_to_list[0])):
    #         sub_array = []
    #         for j in range(len(dict_values_to_list)):
    #             sub_array.append(dict_values_to_list[j][i])
    #         data.append(sub_array)

    #     columns = []
    #     for label in dictionary.keys():
    #         columns.append({"header": label})

    #     files = [("Excel File", "*.xlsx")]

    #     splitted = file_name.split("\\")
    #     file_name = splitted[-1]

    #     entered_complete_file_name = asksaveasfilename(filetypes=files, defaultextension=files, initialfile=file_name, initialdir=program_files_path)
        
    #         # if (CreateExcelFile.every_index(file_name, "/")[-1] + 1) != "DNE":

    #     splitted = entered_complete_file_name.split("/")
    #     entered_file_name = splitted[-1]
    #     entered_file_path = "/".join(splitted[0:len(splitted) - 1]) + "/"

    #     workbook = xl.Workbook(entered_file_name)
    #     sheet = workbook.add_worksheet()

    #     abc = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")

    #     sheet.add_table("A1:" + abc[len(columns) - 1] + str(len(data) + 1), {"data": data, "columns": columns})

    #     workbook.close()

    #     os.path.join(entered_file_path, entered_file_name)

    #     messagebox.showinfo("Successful", f"{entered_file_name} has been saved in {entered_file_path}!")


    # @staticmethod
    # def every_index(string, char):
    #     result_list = []
    #     for index, letter in enumerate(string):
    #         if letter == char:
    #             result_list.append(index)
    #     if len(result_list) == 0:
    #         return "DNE"
    #     return result_list


# The main period totals function that allows the admin to see each and every period's totals.
def period_totals_function():
    clear_frame(main_menu)
    main_menu.config(text="Main Menu > Period Totals")

    global period_count
    period_count = 0

    global next_period
    next_period = Button(main_menu, text="Next", font=("Arial", 8), pady=10, command=lambda: next_previous_period(1))
    next_period.grid(row=1, column=6)

    previous_period = Button(main_menu, text="Previous", font=("Arial", 8), pady=10, command=lambda: next_previous_period(-1))
    previous_period.grid(row=1, column=4)
    
    next_period.config(state=DISABLED)

    display_period_totals(get_period_days(0))

    return

# Clears the entry of an entry widget.
def clear_entry(event, entry):
    entry.delete(0, END)
    entry.unbind('<Button-1>', event)

# Very similar to the period totals function, but allows the admin to enter any specific range of dates (inclusive).
def historical_totals_function():
    clear_frame(main_menu)
    main_menu.config(text="Main Menu > Historical Totals")

    global period_count
    period_count = 0

    start_date = Entry(main_menu, font=("Arial", 8), width=18)
    start_date.grid(row=1, column=0, columnspan=2, padx=5)
    start_date.insert(0, "Start Date mm/dd/yyyy")

    spacer = Label(main_menu, text = "", font=("Arial", 8), width=5)
    spacer.grid(row=1, column=1, columnspan=2, padx=5)

    end_date = Entry(main_menu, font=("Arial", 8), width=18)
    end_date.grid(row=1, column=2, columnspan=2, padx=5)
    end_date.insert(0, "End Date mm/dd/yyyy")

    generate = Button(main_menu, text="Generate", font=("Arial", 8), pady=10, command=lambda: validate_grabArray_sendto_display_period_totals(start_date.get(), end_date.get()))
    generate.grid(row=1, column=4, padx=5)

    

    display_period_totals(get_period_days(0))
    return

# Validates and grabs the array of dates that the admin specified in historical_totals_function() and displays and generates a report for that range of dates.
def validate_grabArray_sendto_display_period_totals(start, end):
    is_valid = validate_timestamp(start, "%m/%d/%Y") and validate_timestamp(end, "%m/%d/%Y")
    if is_valid:
        period_days = tuple(getArrayOfDates(start, end, "%m/%d/%Y", "%m/%d/%y"))
        display_period_totals(((period_days[0], period_days[-1]), period_days))
    else:
        messagebox.showerror("Invalid Entry", "Please enter start and end dates in the format of \"mm/dd/yyyy\"!")
        return

# Grabs all the requests that employees make when they forget to clock out on the same day they clocked in at.
def get_requests():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    requests = c.execute("SELECT row, empID, ClockIn, Request FROM time_clock_entries WHERE ClockOut = 'FORGOT' ORDER BY EmpID ASC").fetchall()
    row = []
    empID = []
    ClockIn = []
    Request = []
    for record in requests:
        row.append(record[0])
        empID.append(record[1])
        ClockIn.append(record[2])
        Request.append(record[3])
    conn.commit()
    conn.close()
    return {
        "Row": row,
        "empID": empID,
        "ClockIn": ClockIn,
        "Request": Request
        }

# The parent function for the admin to resolve employee requests.
def resolve_requests():
    clear_frame(main_menu)
    main_menu.config(text="Main Menu > Resolve Requests")
    global global_index
    global previous_request
    global next_request
    global_index = 0
    
    requests = get_requests()
    # all_entries_and_btns = []
    # for i in range(len(requests["Row"])):
    #     all_entries_and_btns.append([Entry(main_menu, font=("Arial", 15), width=11), Button(main_menu, text="Commit Change", font=("Arial", 8))])

    display_individual_request(requests, 0)
    return

# Displays a single employee's request, and allows the admin to modify their request and commit changes.
def display_individual_request(requests, increment):
    clear_frame(main_menu)
    global global_index

    # requests = get_requests()

    previous_request = Button(main_menu, text="<", font=("Arial", 8), pady=5, command=lambda: display_individual_request(requests, -1), width=6)
    previous_request.grid(row=0, column=0)
    next_request = Button(main_menu, text=">", font=("Arial", 8), pady=5, command=lambda: display_individual_request(requests, 1), width=6)
    next_request.grid(row=0, column=2)

    if len(requests["Row"]) == 1:
        next_request.config(state=DISABLED)
        previous_request.config(state=DISABLED)

    if global_index + increment == len(requests["Row"]) - 1:
        next_request.config(state=DISABLED)
    elif global_index + increment == 0:
        previous_request.config(state=DISABLED)


    global_index += increment

    #                  [Row, empID, ClockIn, RequestTimeStamp]
    if len(requests["Row"]) == 0:
        resolved_all_requests()
        return
    elif len(requests["Row"]) == 1:
        global_index = 0
    employee_request = [value[global_index] for value in requests.values()]

    Label(main_menu, text=f"{global_index + 1} of {len(requests['Row'])}", font=("Arial", 20, "bold"), pady=5).grid(row=0, column=1)

    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    first_name, last_name = c.execute("SELECT FirstName, LastName FROM employees WHERE ID = @0", (employee_request[1],)).fetchone()

    conn.commit()
    conn.close()

    Label(main_menu, text=first_name + " " + last_name, font=("Arial", 20, "bold"), pady=5).grid(row=1, column=1)
    Label(main_menu, text=f"Employee ID: \"{employee_request[1]}\"", font=("Arial", 15), pady=5).grid(row=2, column=1)

    clock_in_timestamp = datetime.strptime(employee_request[2], "%Y-%m-%d %H:%M:%S")
    clock_in_date = clock_in_timestamp.strftime("%m/%d/%y")
    clock_in_time = clock_in_timestamp.strftime("%I:%M:%S %p")
    clock_in_weekday = getWeekDayFromDate(clock_in_date, "%m/%d/%y")

    requested_clock_out_timestamp = datetime.strptime(employee_request[3], "%Y-%m-%d %H:%M:%S") if employee_request[3] is not None else "None"
    requested_clock_out_time = requested_clock_out_timestamp.strftime("%I:%M:%S %p") if type(requested_clock_out_timestamp) == datetime else "None"

    Label(main_menu, text=f"{clock_in_weekday}, {clock_in_date}", font=("Arial", 15), pady=5).grid(row=3, column=1)

    Label(main_menu, text="", font=("Arial", 15), pady=5).grid(row=4, column=1)


    Label(main_menu, text="Clock In ", font=("Arial", 15), pady=5).grid(row=5, column=0)
    Label(main_menu, text=f"{clock_in_time} ", font=("Arial", 15), pady=5).grid(row=6, column=0)

    Label(main_menu, text="Clock Out", font=("Arial", 15), pady=5).grid(row=5, column=1)
    admin_clock_out = Entry(main_menu, font=("Arial", 15), width=11)
    admin_clock_out.grid(row=6, column=1)
    admin_clock_out.insert(0, f"{requested_clock_out_time}")
    # all_entries_and_btns[global_index][0].grid(row=6, column=1)
    # all_entries_and_btns[global_index][0].insert(0, f"{requested_clock_out_time}")
    Label(main_menu, text="", font=("Arial", 8)).grid(row=7, column=1)
    commit_btn = Button(main_menu, text="Commit Change", font=("Arial", 8), command=lambda: commit_request(employee_request[0], clock_in_timestamp.strftime("%I:%M:%S %p"), admin_clock_out.get(), first_name, last_name, employee_request[1]))
    commit_btn.grid(row=8, column=1)
    # all_entries_and_btns[global_index][1].config(command=lambda: commit_request(employee_request[0], all_entries_and_btns[global_index][0].get(), first_name, last_name, employee_request[1], all_entries_and_btns[global_index][0], all_entries_and_btns[global_index][1]))
    # all_entries_and_btns[global_index][1].grid(row=8, column=1)

    Label(main_menu, text=" Request ", font=("Arial", 15), pady=5).grid(row=5, column=2)
    Label(main_menu, text=f"{requested_clock_out_time}", font=("Arial", 15), pady=5).grid(row=6, column=2)

    Label(main_menu, text="", font=("Arial", 8)).grid(row=9, column=1)
    Button(main_menu, text="Return to Main Menu", font=("Arial", 8), command=main_menu_function).grid(row=10, column=1)

    return

# This function makes commits to the database based on the information funneled from display_individual_request().
def commit_request(row, employee_clock_in, admin_request, first, last, id):
    """Commit the admin's request to resolve an employee's mistake of forgetting to clock out on the same day."""
    # [Row, empID, ClockIn, RequestTimeStamp]
    # employee_request

    if validate_timestamp(admin_request, "%I:%M:%S %p"):
        if datetime.strptime(admin_request, "%I:%M:%S %p").time() < datetime.strptime(employee_clock_in, "%I:%M:%S %p").time():
            messagebox.showerror("Invalid Timestamp", "Please enter a timestamp after or equal to the clock in time!")
            return
        conn = sqlite3.connect(database_file)
        c = conn.cursor()

        formatted_admin_request = datetime.strptime(admin_request, "%I:%M:%S %p").strftime("%H:%M:%S")

        clock_in = c.execute("SELECT ClockIn FROM time_clock_entries WHERE Row = @0", (row,)).fetchone()[0]
        ymd = datetime.strptime(clock_in, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

        c.execute("UPDATE time_clock_entries SET ClockOut = @0 WHERE Row = @1", (ymd + " " + formatted_admin_request, row,))

        conn.commit()
        conn.close()
        messagebox.showinfo("Successful!", f"The clock out time for the following employee:\n\"{first} {last}\" (id = \"{id}\")\n has been changed to \"{admin_request}\".")
        requests = get_requests()
        global global_index
        if len(requests["Row"]) == 0:
            resolved_all_requests()
        else:
            if global_index - 1 <= 0:
                display_individual_request(requests, 0)
            else:
                display_individual_request(requests, -1)
    else:
        messagebox.showerror("Invalid Timestamp", "Please re-enter the timestamp in the format of \"HH:MM:SS am/pm\". Here is an example: \"03:47:29 pm\"")
    return

# This function simply displays that the admin finished resolving all the employee requests and sends the admin back to the main_menu.
def resolved_all_requests():
    clear_frame(main_menu)
    main_menu_function()
    messagebox.showinfo("All Requests Successfully Resolved!", "There are no more employee requests. You have successfully resolved all of them.")

# The screen that allows the admin to add a new employee.
def employee_codes__add_new_employee_function():
    clear_frame(main_menu)
    main_menu.config(text = main_menu["text"] + " > Add New Employee")
    #main_menu.config(text="Add New Employee")

    padding = 3

    id_label = Label(main_menu, text="ID: ", font=("Arial", 15), pady=5)
    id_label.grid(row=0, column=0, sticky=E)

    employee_codes__add_new_employee_id = Entry(main_menu, width=25)
    employee_codes__add_new_employee_id.grid(row=0, column=1)

    f_name_label = Label(main_menu, text="First Name: ", font=("Arial", 15), pady=padding)
    f_name_label.grid(row=1, column=0, sticky=E)

    employee_codes__add_new_employee_first_name = Entry(main_menu, width=25)
    employee_codes__add_new_employee_first_name.grid(row=1, column=1)

    l_name_label = Label(main_menu, text="Last Name: ", font=("Arial", 15), pady=padding)
    l_name_label.grid(row=2, column=0, sticky=E)

    employee_codes__add_new_employee_last_name = Entry(main_menu, width=25)
    employee_codes__add_new_employee_last_name.grid(row=2, column=1)

    department_label = Label(main_menu, text="Department: ", font=("Arial", 15), pady=padding)
    department_label.grid(row=3, column=0, sticky=NE)

    employee_codes__add_new_employee_department = Listbox(main_menu, height=4, width=25)
    employee_codes__add_new_employee_department.insert(1, "MG")
    employee_codes__add_new_employee_department.insert(2, "MK")
    employee_codes__add_new_employee_department.insert(3, "PD")
    employee_codes__add_new_employee_department.insert(4, "CL")
    employee_codes__add_new_employee_department.grid(row=3, column=1, sticky=W, pady=padding)

    hourly_pay_label = Label(main_menu, text="Hourly Pay: ", font=("Arial", 15), pady=padding)
    hourly_pay_label.grid(row=4, column=0, sticky=E)

    hourly_pay_entry_widget = Entry(main_menu, width=25)
    hourly_pay_entry_widget.grid(row=4, column=1, pady=padding)

    ot_allowed_label = Label(main_menu, text="OT Allowed: ", font=("Arial", 15), pady=padding)
    ot_allowed_label.grid(row=5, column=0, sticky=E)

    ot_allowed_listbox = Listbox(main_menu, height=2, width=25)
    ot_allowed_listbox.insert(1, "Yes")
    ot_allowed_listbox.insert(2, "No")
    ot_allowed_listbox.grid(row=5, column=1, sticky=W, pady=padding)

    max_daily_hours_label = Label(main_menu, text="Max Daily Hours: ", font=("Arial", 15), pady=padding)
    max_daily_hours_label.grid(row=6, column=0, sticky=E)

    max_daily_hours_entry = Entry(main_menu, width=25)
    max_daily_hours_entry.grid(row=6, column=1, pady=padding)

    add_to_database = Button(main_menu, text="Add Employee", command=lambda: add_new_employee(employee_codes__add_new_employee_id.get(), employee_codes__add_new_employee_first_name.get(), employee_codes__add_new_employee_last_name.get(), employee_codes__add_new_employee_department.get(ANCHOR), hourly_pay_entry_widget.get(), ot_allowed_listbox.get(ANCHOR), max_daily_hours_entry.get()))
    add_to_database.grid(row=7, column=0, columnspan=2, pady=padding)

    root.bind("<Return>", lambda event=None: add_to_database.invoke())

    return_to_employee_codes = Button(main_menu, text="Return to Employees", command=employee_codes_function)
    return_to_employee_codes.grid(row=8, column=0, columnspan=2, pady=padding)
    
    return

# Grabs the information that the admin enters to create a new employee and updates the database accordingly.
def add_new_employee(id, first, last, department, hourly_pay, ot_allowed, max_daily_hours):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    if id == "" or first == "" or last == "" or department == "" or hourly_pay == "" or ot_allowed == "" or max_daily_hours == "":
        messagebox.showerror("Empty Field", "Missing 'Id', 'First Name', 'Last Name', 'Department', 'Hourly Pay', 'OT Allowed', or 'Max Daily Hours'")
        #label_widget.config(text="Missing 'Id', 'First Name', 'Last Name', 'Department', 'Hourly Pay', 'OT Allowed', or 'Max Daily Hours'")
        return
    else:
        try:
            float(hourly_pay)
            float(max_daily_hours)
        except ValueError:
            messagebox.showerror("Invalid Field", "'Hourly Pay' and 'Max Daily Hours' must be numbers!")
            #label_widget.config(text="'Hourly Pay' and 'Max Daily Hours' must be numbers!")
            return

    result = ""
    try:
        c.execute(f"INSERT INTO employees(ID, FirstName, LastName, Department, HourlyPay, OTAllowed, MaxDailyHours) VALUES('{id}', '{first}', '{last}', '{department}', '{hourly_pay}', '{ot_allowed}', '{max_daily_hours}');")

    except sqlite3.IntegrityError:
        result = "ID already exists"
    else:
        result = "'" + first + " " + last + "' successfully added!"
    conn.commit()
    conn.close()
    messagebox.showinfo("Successful!", result)
    #label_widget.config(text=result)

# The screen that allows the admin to edit the information of a certain employee.
def employee_codes__edit_function():
    clear_frame(main_menu)
    main_menu.config(text = main_menu["text"] + " > Edit")

    id_label_widget = Label(main_menu, text="Enter Employee ID to Edit", font=("Arial", 15), pady=10)
    id_label_widget.grid(row=0, column=0, columnspan=2)

    id_entry_widget = Entry(main_menu, width=25)
    id_entry_widget.grid(row=1, column=0, columnspan=2, pady=10)

    #error_message = Label(main_menu, text="", font=("Arial", 15), pady=10)
    #confirmation_message = Label(main_menu, text="", font=("Arial", 15), pady=10)
    #confirmation_message.grid(row=11, column=0, columnspan=2)

    edit_button = Button(main_menu, text="Edit", command=lambda: employee_codes__edit__edit_button(id_entry_widget.get(), return_to_employee_codes))
    edit_button.grid(row=3, column=0, columnspan=2)

    root.bind("<Return>", lambda event=None: edit_button.invoke())

    return_to_employee_codes = Button(main_menu, text="Return to Employees", command=employee_codes_function)
    return_to_employee_codes.grid(row=4, column=0, columnspan=2, pady=10)

    return

# A sub-sub button within the main_menu that allows the admin to edit information of a specific employee.
def employee_codes__edit__edit_button(id, return_button):
    return_button.grid_forget()
    #confirmation_message.config(text="")
    

    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    try:
        emp_info = c.execute(f"SELECT * FROM employees WHERE ID = @0;", (id,)).fetchone()
    except Exception as e:
        #error_message.destroy()
        return_button.grid(row=10, column=0, columnspan=2, pady=10)
        messagebox.showerror("Error", str(e))
        #confirmation_message.config(text="Error: " + str(e))
        #confirmation_message.grid(row=11, column=0, columnspan=2)
        conn.commit()
        conn.close()
        return

    padding = 1
    id_label_widget = Label(main_menu, text="ID: ", font=("Arial", 15), pady=padding)
    id_entry_widget = Entry(main_menu, width=18)
    first_name_label_widget = Label(main_menu, text="First: ", font=("Arial", 15), pady=padding)
    first_name_entry_widget = Entry(main_menu, width=18)
    last_name_label_widget = Label(main_menu, text="Last: ", font=("Arial", 15), pady=padding)
    last_name_entry_widget = Entry(main_menu, width=18)
    deparment_label_widget = Label(main_menu, text="Department ('MG', 'MK', 'PD', 'CL'): ", font=("Arial", 15), pady=padding)
    department_entry_widget = Entry(main_menu, width=18)
    hourly_pay_label_widget = Label(main_menu, text="Hourly Pay: ", font=("Arial", 15), pady=padding)
    hourly_pay_entry_widget = Entry(main_menu, width=18)
    ot_allowed_label_widget = Label(main_menu, text="OT Allowed ('Yes', 'No'): ", font=("Arial", 15), pady=padding)
    ot_allowed_entry_widget = Entry(main_menu, width=18)
    max_daily_hours_label_widget = Label(main_menu, text="Max Daily Hours: ", font=("Arial", 15), pady=padding)
    max_daily_hours_entry_widget = Entry(main_menu, width=18)
    commit_changes = Button(main_menu, text="Commit Changes")
    
    #error_message = Label(main_menu, font=("Arial", 15), pady=10)
    #confirmation_message = Label(main_menu, text="", font=("Arial", 15), pady=10)
    #confirmation_message.grid(row=11, column=0, columnspan=2)


    if emp_info is not None:
        #error_message.grid_forget()
        #error_message.destroy()
        #confirmation_message.destroy()
        #confirmation_message.config(text="")
        
        #confirmation_message.destroy()
        #clear([error_message, id_label_widget, first_name_label_widget, last_name_label_widget, deparment_label_widget], [commit_changes], False, [])

        id_label_widget.grid(row=4, column=0, sticky=E)

        id_entry_widget.grid(row=4, column=1, sticky=W)
        id_entry_widget.insert(END, str(emp_info[0]))

        first_name_label_widget.grid(row=5, column=0, sticky=E)

        first_name_entry_widget.grid(row=5, column=1, sticky=W)
        first_name_entry_widget.insert(END, emp_info[1])

        last_name_label_widget.grid(row=6, column=0, sticky=E)

        last_name_entry_widget.grid(row=6, column=1, sticky=W)
        last_name_entry_widget.insert(END, emp_info[2])

        deparment_label_widget.grid(row=7, column=0, sticky=NE)

        department_options = ["MG", "MK", "PD", "CL"]

        department_entry_widget.grid(row=7, column=1, sticky=W, pady=padding)
        department_entry_widget.insert(END, emp_info[3])

        #department_listbox_widget.event_generate("<<ListboxSelect>>")

        hourly_pay_label_widget.grid(row=8, column=0, sticky=NE)

        hourly_pay_entry_widget.grid(row=8, column=1, sticky=W)
        hourly_pay_entry_widget.insert(END, emp_info[4])

        ot_allowed_label_widget.grid(row=9, column=0, sticky=NE)
        ot_allowed_entry_widget.grid(row=9, column=1, sticky=W, pady=padding)
        ot_allowed_entry_widget.insert(END, emp_info[5])

        max_daily_hours_label_widget.grid(row=10, column=0, sticky=NE)

        max_daily_hours_entry_widget.grid(row=10, column=1, sticky=W)
        max_daily_hours_entry_widget.insert(END, emp_info[6])





        
        #confirmation_message.grid(row=11, column=0, columnspan=2)

        #department_listbox_widget.curselection()
        #                                                                                       old_id, new_id,             new_first,                      new_last,                   new_department,                 new_hourly_pay,                 new_ot_allowed,                 new_max_daily_hours
        commit_changes.config(command=lambda: employee_codes__edit__edit_button__commit_changes(id, id_entry_widget.get(), first_name_entry_widget.get(), last_name_entry_widget.get(), department_entry_widget.get(), hourly_pay_entry_widget.get(), ot_allowed_entry_widget.get(), max_daily_hours_entry_widget.get()))
        commit_changes.grid(row=11, column=0, columnspan=2, pady=padding)

        root.bind("<Return>", lambda event=None: commit_changes.invoke())

        return_button.grid(row=12, column=0, columnspan=2, pady=padding)
        
    else:
        clear_frame(main_menu)

        main_menu.config(text="Edit")

        id_label_widget = Label(main_menu, text="Enter Employee ID to Edit", font=("Arial", 15), pady=10)
        id_label_widget.grid(row=0, column=0, columnspan=2)

        id_entry_widget = Entry(main_menu, width=25)
        id_entry_widget.grid(row=1, column=0, columnspan=2, pady=10)

        edit_button = Button(main_menu, text="Edit", command=lambda: employee_codes__edit__edit_button(id_entry_widget.get(), return_to_employee_codes))
        edit_button.grid(row=2, column=0, columnspan=2)

        return_to_employee_codes = Button(main_menu, text="Return to Employees", command=employee_codes_function)
        return_to_employee_codes.grid(row=3, column=0, columnspan=2, pady=10)

        messagebox.showerror("Invalid ID", f"ID \"{id}\" does not exist. Please try again.")
        # error_message = Label(main_menu, text="ID '" + id + "' Does Not Exist", font=("Arial", 15), pady=10)
        # error_message.grid(row=4, column=0, columnspan=2)

        #confirmation_message = Label(main_menu, text="", font=("Arial", 15), pady=10)
        #confirmation_message.grid(row=11, column=0, columnspan=2)

        

        root.bind("<Return>", lambda event=None: edit_button.invoke())

        
        
        conn.commit()
        conn.close()
        return
    
    

    conn.commit()
    conn.close()
    return

# This function funnels in information from employee_codes__edit_function(), (whatever info the admin modifies), and commits those changes to the database.
def employee_codes__edit__edit_button__commit_changes(old_id, new_id, new_first, new_last, new_department, new_hourly_pay, new_ot_allowed, new_max_daily_hours):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    hour = time.strftime("%I")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    am_pm = time.strftime("%p")

    current_time = hour + ":" + minute + ":" + second + " " + am_pm

    emp_info = c.execute("SELECT * FROM employees WHERE ID = '" + old_id + "';").fetchone()

    # if new_id == "" or new_first == "" or new_last == "" or new_hourly_pay == "":
    #     confirmation_message.config(text="Missing 'Id', 'First Name', 'Last Name', or 'Hourly Pay'")
    #     confirmation_message.grid(row=11, column=0, columnspan=2)
    #     return
    # else:
    #     try:
    #         float(new_hourly_pay)
    #     except ValueError:
    #         confirmation_message.config(text="'Hourly Pay' must be a number")
    #         confirmation_message.grid(row=11, column=0, columnspan=2)
    #         return

    try:
        
        
        departments = ["MG", "MK", "PD", "CL"]
        ot_responses = ["Yes", "No"]
        
        if new_id == "" or new_first == "" or new_last == "" or (new_department not in departments) or new_hourly_pay == "" or (new_ot_allowed not in ot_responses) or new_max_daily_hours == "":
            messagebox.showerror("Empty Field", "Missing 'Id', 'First Name', 'Last Name', valid 'Department', 'Hourly Pay', valid 'OT Allowed', or 'Max Daily Hours'")
            #confirmation_message.config(text="Missing 'Id', 'First Name', 'Last Name', valid 'Department', 'Hourly Pay', valid 'OT Allowed', or 'Max Daily Hours'")
            #confirmation_message.grid(row=13, column=0, columnspan=2)
            return
        else:
            try:
                float(new_hourly_pay)
                float(new_max_daily_hours)
            except ValueError:
                messagebox.showerror("Invalid Entry", "'Hourly Pay' and 'Max Daily Hours' must both be numbers")
                # confirmation_message.config(text="'Hourly Pay' and 'Max Daily Hours' must both be numbers")
                # confirmation_message.grid(row=13, column=0, columnspan=2)
                return

        edited_info = ""
        # "s" = string, "f" = float, "m" = $float
        types =    ["s", "s", "s", "s", "m", "s", "f"]
        #old_info = [emp_info[0], emp_info[1], emp_info[2], emp_info[3], emp_info[4], emp_info[5], emp_info[6]]
        displayed_labels_for_changes = ["ID", "First Name", "Last Name", "Department", "Hourly Pay", "OT Allowed", "Max Daily Hours"]
        new_info = [new_id, new_first, new_last, new_department, new_hourly_pay, new_ot_allowed, new_max_daily_hours]

        for type, label, old, new in zip(types, displayed_labels_for_changes, emp_info, new_info):
            if type == "s":
                if str(old) != str(new):
                    edited_info += label + ": '" + str(old) + "' => '" + str(new) + "'\n"
            elif type == "f":
                if float(old) != float(new):
                    edited_info += label + ": '" + str(float(old)) + "' => '" + str(float(new)) + "'\n"
            elif type == "m":
                if float(old) != float(new):
                    edited_info += label + ": '$" + str(float(old)) + "' => '$" + str(float(new)) + "'\n"

        if edited_info == "":
            messagebox.showinfo("No Changes", "No modifications were made. All information already matched.")
            #confirmation_message.config(text="No modifications made")
        else:
            employees_table_update = f"UPDATE employees SET ID = '{new_id}', FirstName = '{new_first}', LastName = '{new_last}', Department = '{new_department}', HourlyPay = '{new_hourly_pay}', OTAllowed = '{new_ot_allowed}', MaxDailyHours = '{new_max_daily_hours}' WHERE ID = '{old_id}';"
            time_clock_entries_table_update = f"UPDATE time_clock_entries SET empID = '{new_id}' WHERE empID = '{old_id}';"
            employee_tasks_table_update = f"UPDATE employee_tasks SET employee_id = '{new_id}' WHERE employee_id = '{old_id}';"
            updated_table_query_array = [employees_table_update, time_clock_entries_table_update, employee_tasks_table_update]
            for updated_table_query in updated_table_query_array:
                c.execute(updated_table_query)
            conn.commit()
            conn.close()
            messagebox.showinfo("Successful", old_id + "' was edited at " + current_time + "!\n" + edited_info)
            #confirmation_message.config(text="Successful! '" + old_id + "' was edited at " + current_time + "!\n" + edited_info)

    except Exception as e:
        if str(e) == "'NoneType' object is not iterable":
            messagebox.showerror("Invalid ID", f"ID '{old_id}' could not be found. You may have changed it.")
            #confirmation_message.config(text=f"ID '{old_id}' could not be found. You may have changed it.")
        else:
            messagebox.showerror("Unknown Error", "Unsuccessful. " + old_id + " was not edited at " + current_time + " due to the following error: " + str(e))
            #confirmation_message.config(text="Unsuccessful. " + old_id + " was not edited at " + current_time + " due to the following error: " + str(e))
        #confirmation_message.grid(row=11, column=0, columnspan=2)
    #else:
        # edited_info = ""
        # new_info = [new_id, new_first, new_last, new_department, new_hourly_pay]

        # for old, new in zip(emp_info, new_info):
        #     if str(old) != str(new):
        #         edited_info += "'" + str(old) + "' => '" + str(new) + "'\n"

        # if edited_info == "":
        #     confirmation_message.config(text="No modifications made")
        # else:
        #     confirmation_message.config(text="Successful! '" + old_id + "' was edited at " + current_time + "!\n" + edited_info)
        #confirmation_message.grid(row=11, column=0, columnspan=2)
    #confirmation_message.grid(row=13, column=0, columnspan=2)

    
    return

# The screen that the admin can delete employees from.
def employee_codes__delete_function():

    #global_confirmation_text

    clear_frame(main_menu)
    main_menu.config(text = main_menu["text"] + " > Delete")

    id_label_widget = Label(main_menu, text="Enter Employee Id to Delete", font=("Arial", 15), pady=10)
    id_label_widget.grid(row=0, column=0, columnspan=2)

    id_entry_widget = Entry(main_menu, width=25)
    id_entry_widget.grid(row=1, column=0, columnspan=2, pady=10)

    delete_button = Button(main_menu, text="Delete", command=lambda: employee_codes__delete_function__delete_button(id_entry_widget.get()))
    delete_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.bind("<Return>", lambda event=None: delete_button.invoke())

    return_to_employee_codes = Button(main_menu, text="Return to Employees", command=employee_codes_function)
    return_to_employee_codes.grid(row=3, column=0, columnspan=2, pady=10)
    return

# Deletes the specific employee entered by the admin from employee_codes__delete_function()
def employee_codes__delete_function__delete_button(id):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    # global global_confirmation_text
    name = c.execute("SELECT FirstName, LastName FROM employees WHERE ID = '" + id + "';").fetchone()
    try:
        if name == None:
            messagebox.showerror("Invalid ID", f"An employee with the id of \"{id}\" does not exist. Please try again.")
            #global_confirmation_text.set("'" + id + "' Does Not Exist.")
            conn.commit()
            conn.close()
            return
        response = messagebox.askyesno("Warning!", f"Are you sure you'd like to delete the employee, \"{name[0]} {name[1]}\", and all his/her data? This action is irreversible.")
        if response:
            c.execute("DELETE FROM employees WHERE ID = '" + id + "';")
            c.execute("DELETE FROM time_clock_entries WHERE empID = '" + id + "';")
            c.execute("DELETE FROM employee_tasks WHERE employee_id = '" + id + "';")
        else:
            conn.commit()
            conn.close()
            return
    except Exception as e:
        messagebox.showerror("Unknown Error", "Error:\n" + str(e))
        # global_confirmation_text.set("Error: " + str(e))
    else:
        messagebox.showinfo("Successful!", f"\"{id}\" ({name[0]} {name[1]}) has been successfully deleted.")
        # global_confirmation_text.set("'" + id + "' has been successfully deleted!")

    conn.commit()
    conn.close()
    return

# The admin screen where employees and all their information can be viewed. This creates another sub-menu with the option of viewing employee info and viewing timeclock entry info.
def employee_codes__view_function():
    fill_frame(main_menu, [["Employees", employee_codes__view_function__view_employees], ["Timeclock Entries", employee_codes__view_function__view_timeclock_entries]], "Main Menu > Employees > View", ["Employees", employee_codes_function])
    # return_to_main_menu = Button(main_menu, text="Return to Employee Codes", command=employee_codes_function)
    # return_to_main_menu.grid(row=num_of_menu_items, column=0, columnspan=2, pady=10)
    return

# The admin screen where employee information can be viewed.
def employee_codes__view_function__view_employees():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    main_menu.config(text = "Main Menu > Employees > View > Employees")

    clear_frame(main_menu)

    id_label = Label(main_menu, text="")
    first_name_label = Label(main_menu, text="")
    last_name_label = Label(main_menu, text="")
    department_label = Label(main_menu, text="")
    hourly_pay_label = Label(main_menu, text="")
    ot_allowed_label = Label(main_menu, text="")
    max_daily_hours_label = Label(main_menu, text="")
    master_label_array = [id_label, first_name_label, last_name_label, department_label, hourly_pay_label, ot_allowed_label, max_daily_hours_label]

    id = "ID\n-------------\n\n"
    first_name = "First Name\n-------------\n\n"
    last_name = "Last Name\n-------------\n\n"
    department = "Department\n-------------\n\n"
    hourly_pay = "Hourly Pay\n-------------\n\n"
    ot_allowed = "OT Allowed\n-------------\n\n"
    max_daily_hours = "Max Daily Hours\n-------------\n\n"
    master_field_array = [id, first_name, last_name, department, hourly_pay, ot_allowed, max_daily_hours]

    data = c.execute("SELECT * FROM employees").fetchall()

    for record in data:
        for item, db_fields_counter in zip(record, range(len(record))):
            master_field_array[db_fields_counter] += str(item) + "\n"

    #print(master_field_array)
    next_column = 0
    for label, field, column_counter in zip(master_label_array, master_field_array, range(len(master_label_array))):
        label.config(text=field)
        label.grid(row=0, column=column_counter)
        if column_counter == len(master_label_array) - 1:
            next_column = column_counter + 1

    return_button = Button(main_menu, text="Return to View", command=employee_codes__view_function)
    return_button.grid(row=1, column=3)

    root.bind("<Return>", lambda event=None: button.invoke())



    conn.commit()
    conn.close()
    return

# The admin screen where timeclock entry info can be viewed. The scrollbar was especially hard!
def employee_codes__view_function__view_timeclock_entries():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    main_menu.config(text = "Main Menu > Employees > View > Timeclock Entries")

    clear_frame(main_menu)

    data = c.execute("SELECT empID, ClockIn, ClockOut, Request FROM time_clock_entries ORDER BY empID").fetchall()

    main_frame = Frame(main_menu)
    main_frame.pack(fill=BOTH, expand=1)

    canvas = Canvas(main_frame)
    canvas.pack(side=LEFT, fill=BOTH, expand=1)
    
    scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=LEFT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    second_frame = Frame(canvas)

    canvas.create_window((0,0), window=second_frame, anchor="nw")

    #row_label = Label(second_frame, text="")
    emp_id_label = Label(second_frame, text="")
    clock_in_label = Label(second_frame, text="")
    clock_out_label = Label(second_frame, text="")
    requests_label = Label(second_frame, text="")
    master_label_array = [emp_id_label, clock_in_label, clock_out_label, requests_label]

    #row = "Row\n-------------\n\n"
    id = "ID\n-------------\n\n"
    clock_in = "Clock In\n-------------\n\n"
    clock_out = "Clock Out\n-------------\n\n"
    request = "Request\n-------------\n\n"
    master_field_array = [id, clock_in, clock_out, request]

    for record, r in zip(data, range(len(data))):
        #master_field_array[0] += str(r+1) + "\n\n"
        for item, db_fields_counter in zip(record, range(len(record))):
            if db_fields_counter == 1 and item != "FORGOT" and item is not None:
                master_field_array[db_fields_counter] += datetime.strptime(item, "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%y %I:%M:%S %p") + "\n\n"
            elif db_fields_counter == 2 and item != "FORGOT" and item is not None:
                master_field_array[db_fields_counter] += datetime.strptime(item, "%Y-%m-%d %H:%M:%S").strftime("%I:%M:%S %p") + "\n\n"
            elif db_fields_counter == 3:
                if item is None:
                    master_field_array[db_fields_counter] += "\n\n"
                else:
                    master_field_array[db_fields_counter] += datetime.strptime(item[11:], "%H:%M:%S").strftime("%I:%M:%S %p") + "\n\n"
            else:
                master_field_array[db_fields_counter] += str(item) + "\n\n"
    
    for label, field, column_counter in zip(master_label_array, master_field_array, range(len(master_label_array))):
        label.config(text=field)
        label.grid(row=0, column=column_counter)

    return_button = Button(second_frame, text="Return to View", command=employee_codes__view_function)
    return_button.grid(row=1, column=1, columnspan=2)

    root.bind("<Return>", lambda event=None: button.invoke())

    conn.commit()
    conn.close()
    return




















# Selects an employee's task on a given date.
def selectTask(emp_id, task_date, format):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    task = c.execute("SELECT task FROM employee_tasks WHERE employee_id = '" + emp_id + "' AND task_date = '" + str(datetime.strptime(task_date, format).strftime("%m/%d/%Y")) + "';").fetchone()
    conn.commit()
    conn.close()
    if task != None:
        return task[0]
    else:
        return "You don't have any tasks!"

# Grabs the current period's date range (for calculation use).
def getPeriodDays():
    result_str = []
    current_date = time.strftime("%x")
    day = int(current_date[3:5])
    month = current_date[0:2]
    year = current_date[6:8]
    num_of_days_in_month = monthrange(datetime.now().year, int(month))[1]
    #mm/dd/yy
    if day >= 1 and day < 16:
        for i in range(1, day+1):
            if i < 10:
                result_str.append(month + "/0" + str(i) + "/" + year)
            else:
                result_str.append(month + "/" + str(i) + "/" + year)
    else:
        for i in range(16, day+1):
            result_str.append(month + "/" + str(i) + "/" + year)
    return result_str

# Returns an array of dates in a period depending on what period a given date is in.
def getPeriodFromDateString(date_string, format):
    result_array_of_str_dates = []
    date = str(datetime.strptime(date_string, format).strftime("%m/%d/%y"))
    day = int(date[3:5])
    month = date[0:2]
    year = date[6:8]
    if day >= 1 and day < 16:
        for i in range(1, day+1):
            if i < 10:
                result_array_of_str_dates.append(month + "/0" + str(i) + "/" + year)
            else:
                result_array_of_str_dates.append(month + "/" + str(i) + "/" + year)
    else:
        for i in range(16, day+1):
            result_array_of_str_dates.append(month + "/" + str(i) + "/" + year)
    return result_array_of_str_dates


# %Y means 2021, %y means 21



#Fix later
# def getAllEmployeeHours(start, end, entered_format, result_format):

#     employee_hours_button.config(command=lambda: clear([employee_list_label, employee_hours_label], [], False, [[employee_hours_button, getAllEmployeeHours]]))

#     conn = sqlite3.connect(database_file)
#     c = conn.cursor()
    

#     employees_table = c.execute("SELECT * FROM employees;").fetchall()

#     conn.commit()
#     conn.close()

#     array_of_dates = getArrayOfDates(start, end, entered_format, result_format)

#     employee_list_string = "Employee\n---------------\n"
#     employee_hours_string = "Hours\n---------------\n"
#     for record in employees_table:
#         id = record[0]
#         employee_list_string += record[1] + " " + record[2] + "\n\n"  
#         for single_date in array_of_dates:
#             employee_hours_string += str(getTotalEmployeeHours(single_date, result_format, str(id))) + "\n\n"
                            
#     employee_list_label.config(text=employee_list_string)
#     employee_hours_label.config(text=employee_hours_string)
    

    
# Grabs an employees raw employee hours for a certain date. It simply subtracts the clock in timestamp from the clock out timestamp in the database. If an employee forgot
# to clock out, it make the duration for that record 0.
def getRawTotalEmployeeHours(entered_date, format, id):
    #Other commented version: getRawTotalEmployeeHours(start, end, id):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    time_in_out_records = c.execute("SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = '" + id + "' AND ClockIn LIKE '%" + str(datetime.strptime(entered_date, format).strftime("%Y-%m-%d")) + "%';").fetchall()

    total_seconds = 0
    for record in time_in_out_records:
        t0 = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S").timestamp()        
        if record[1] is not None:
            if record[1] == "FORGOT":
                #t1 = t0
                continue
            else:
                t1 = datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S").timestamp()
        else:
            # t1 = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f").timestamp()
            #t1 = t0
            continue   
        total_seconds += t1 - t0
    employee_hours = round(total_seconds / 3600, 3)
    conn.close()
    return employee_hours

# Grabs the result from getRawTotalEmployeeHours(), calculates an employee's total break time for the day, and contains logic to return an employee's total hours for the day accounting for breaks.
def getTotalDailyHoursAccountingForBreaks(entered_date, format, id):

    total_period_hours = getRawTotalEmployeeHours(entered_date, format, id)

    formatted_entered_date = str(datetime.strptime(entered_date, format).strftime("%Y-%m-%d"))

    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    time_in_out_records = c.execute("SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = '" + id + "' AND ClockIn LIKE '%" + formatted_entered_date + "%';").fetchall()

    conn.close()

    total_break_seconds = 0
    for record in range(len(time_in_out_records)):
        if record < len(time_in_out_records) - 1:
            out_to_lunch = datetime.strptime(time_in_out_records[record][1], "%Y-%m-%d %H:%M:%S").timestamp()
            back_from_lunch = datetime.strptime(time_in_out_records[record+1][0], "%Y-%m-%d %H:%M:%S").timestamp()
            total_break_seconds += back_from_lunch - out_to_lunch

    # total_break_seconds = 0
    # previous_record = None
    # for rec_num, record in enumerate(time_in_out_records):
    #     previous_record = record
    #     if rec_num == 0:
    #         continue
    #     clock_out = datetime.strptime(previous_record[1], "%Y-%m-%d %H:%M:%S").timestamp()
    #     clock_in = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S").timestamp()
    #     total_break_seconds += clock_in - clock_out
        
    
    
    # total_break_hours = round(total_break_seconds / 3600, 3)
    total_break_hours = total_break_seconds / 3600

    if total_period_hours >= 8:
        if total_break_hours >= .5:
            return total_period_hours
        else:
            return total_period_hours - (.5 - total_break_hours)
    else:
        return total_period_hours

# Uses the result from getTotalDailyHoursAccountingForBreaks() in order to calculate an employee's total paid employee hours in a specific range of dates.
def calculateTotalPaidEmpHours(start_date, end_date, entered_format, id):
    dates = getArrayOfDates(start_date, end_date, entered_format, "%Y-%m-%d")
    total_range_hours = 0
    array_of_total_hours_per_day = []
    for single_date in dates:
        day_hours_accounting_for_breaks = getTotalDailyHoursAccountingForBreaks(single_date, "%Y-%m-%d", id)
        total_range_hours += day_hours_accounting_for_breaks
        array_of_total_hours_per_day.append(day_hours_accounting_for_breaks)
    return total_range_hours, array_of_total_hours_per_day


# Calculates employee pay, accounting for regular, overtime, and double time hours, and returns the result as a dictionary.
def calculate_employee_pay(start_date, end_date, entered_format, id):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    array_of_hours_per_day = calculateTotalPaidEmpHours(start_date, end_date, entered_format, id)[1]

    ot_allowed = c.execute("SELECT OTAllowed FROM employees WHERE ID = @0", (id,)).fetchone()
    hourly_pay = c.execute("SELECT HourlyPay FROM employees WHERE ID = @0", (id,)).fetchone()

    first, last = c.execute("SELECT FirstName, LastName FROM employees WHERE ID = @0", (id,)).fetchone()
    conn.commit()
    conn.close()

    ot_allowed = ot_allowed[0].lower()
    hourly_pay = hourly_pay[0]


    regular_hours = 0
    overtime_hours = 0
    double_time_hours = 0
    if ot_allowed == "yes":
        for hours_per_day in array_of_hours_per_day:
            if hours_per_day <= 8:
                #regular_pay += hourly_pay * hours_per_day
                regular_hours += hours_per_day
            elif hours_per_day > 8 and hours_per_day < 12:
                #total_pay += hourly_pay * 8 + hourly_pay * 1.5 * (hours_per_day - 8)
                regular_hours += 8
                overtime_hours += hours_per_day - 8
            else:
                #total_pay += hourly_pay * 8 + hourly_pay * 1.5 * 4 + hourly_pay * 2 * (hours_per_day - 12)
                regular_hours += 8
                overtime_hours += 4
                double_time_hours += hours_per_day - 12
    elif ot_allowed == "no":
        #total_pay += hourly_pay * total_employee_hours
        regular_hours = calculateTotalPaidEmpHours(start_date, end_date, entered_format, id)[0]

    regular_hours = round(regular_hours, 2)
    overtime_hours = round(overtime_hours, 2)
    double_time_hours = round(double_time_hours, 2)

    hourly_pay = round(hourly_pay, 2)

    regular_pay = round(regular_hours * hourly_pay, 2)
    overtime_pay = round(hourly_pay * 1.5 * overtime_hours, 2)
    double_time_pay = round(hourly_pay * 2 * double_time_hours, 2)

    total_pay = round(regular_pay + overtime_pay + double_time_pay, 2)
    total_hours = round(calculateTotalPaidEmpHours(start_date, end_date, entered_format, id)[0], 2)
    
    # Uncomment the following to check if total_hours is correct.
    if total_hours != round(regular_hours + overtime_hours + double_time_hours, 2):
        print("ID", id, ":", "WRONG Hours")

    #returned_array = [total_pay, [regular_hours, overtime_hours, double_time_hours], [regular_pay, overtime_pay, double_time_pay]]

    dictionary = {
        "ID": id,
        "FLast": first[0] + last,
        "Regular Hours": regular_hours,
        "Regular Pay": regular_pay,
        "Overtime Hours": overtime_hours,
        "Overtime Pay": overtime_pay,
        "Double Time Hours": double_time_hours,
        "Double Time Pay": double_time_pay,
        "Total Hours": total_hours,
        "Total Pay": total_pay
    }

    return dictionary

    




        

    



    # The following works, however, since I fixed the time clock entries such that they can only be on the same day, all the nested if statements aren't necessary.
    # start_date = datetime.strptime(start, "%m/%d/%y").timestamp()
    # print(start_date)
    # end_date = datetime.strptime(end, "%m/%d/%y").timestamp()
    # print(end_date)

    # employee_hours = 0
    # time_in_out_records = c.execute("SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = '" + id + "';").fetchall()
    # total_seconds = 0
    # for time_record in time_in_out_records:
    #     t0 = datetime.strptime(time_record[0], "%Y-%m-%d %H:%M:%S").timestamp()
    #     t1 = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f").timestamp()
    #     if time_record[1] is not None:
    #         t1 = datetime.strptime(time_record[1], "%Y-%m-%d %H:%M:%S").timestamp()
                
    #     if end_date > start_date and t1 > t0:
    #         if t0 >= start_date and t1 <= end_date:
    #             total_seconds += t1 - t0
    #             print("1: " + str(total_seconds))
    #         elif t0 < start_date and t1 <= end_date:
    #             total_seconds += t1 - start_date
    #             print("2: " + str(total_seconds))
    #         elif t0 >= start_date and t1 > end_date:
    #             total_seconds += end_date - t0
    #             print("3: " + str(total_seconds))
    #         elif start_date < t0 and end_date < t0:
    #             total_seconds += end_date - start_date
    #             print("4: " + str(total_seconds))
    #         elif start_date > t1 and end_date > t1:
    #             total_seconds += end_date - start_date
    #             print("5: " + str(total_seconds))
                
    # employee_hours = round(total_seconds / 3600, 8)

    # conn.commit()
    # conn.close()
    # return employee_hours




#clear([start_date_label, end_date_label], )







# Clears the text of a widget.
def clear_widget_text(widget):
    widget['text'] = ""



global_confirmation_text = StringVar()


# The static main screen.
day_of_week = Label(root, text="", font=("Arial", 25), fg="blue", pady=45)
day_of_week.place(relx=.175, rely=0.0, anchor=N)

program_clock = Label(root, text="", font=("Arial", 25), fg="blue", pady=45)
program_clock.place(relx=.825, rely=0.0, anchor=N)

day_time_greeting = Label(root, text="", font=("Arial", 25), fg="blue")
day_time_greeting.place(relx=0.5, rely=0.13, anchor=N)

Label(root, text="Log in/out with your Employee ID, then\n\nhit the Clear Button/Enter Key to clear the screen after viewing", font=("Arial", 12), fg="black").place(relx=0.5, rely=0.20, anchor=N)
# Label(root, text="2. Press \"Finish\" to complete.", font=("Arial", 12), fg="black").place(relx=0.5, rely=0.23, anchor=N)

clock()
#root.after(1000, clock)
greeting_time()
send_report_if_pay_day()

header = Label(root, text="SBCS\nEmployee Time Clock", font=("Times New Roman", 25, "bold"), pady=22.5)
header.place(relx=0.5, rely=0.0, anchor=N)




#Employee Widgets:
id_field_label = Label(root, text="ID: ", font=("Arial", 20))
id_field_label.place(relx=0.39, rely=.28, anchor=N)

id_field = Entry(root, font=("Arial", 20), show="\u2022")
id_field.place(relx=.50, rely=.289, width=200, height=28, anchor=N)

button = Button(root, text="Enter", command=enter, font=("Arial", 15))
button.place(relx=.6, rely=.28)
root.bind("<Return>", lambda event=None: button.invoke())

greeting = Label(root, text="", font=("Arial", 18), wraplength=700)
greeting.place(relx=.5, rely=.36, anchor=N)

#rely = .35
#rely = .375
#rely = .4



enter_actual_clock_out_time_label = Label(root, text="", font=("Arial", 18))
enter_actual_clock_out_time_label.place(relx=.5, rely=.425, anchor=N)

enter_actual_clock_out_time_entry = Entry(root, font=("Arial", 18), width=13)

actual_clock_out_time_submit_button = Button(root, text="Submit", font=("Arial", 18))

time_in = Label(root, text="", font=("Arial", 10))
time_in.place(relx=.075, rely=.4, anchor=N)

time_out = Label(root, text="", font=("Arial", 10))
time_out.place(relx=.175, rely=.4, anchor=N)

forward = Button(root, text=">", font=("Arial", 15), command=next_day_totals)

backward = Button(root, text="<", font=("Arial", 15), command=previous_day_totals)

current_date_mm_dd_yy = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date()

day_total = Label(root, text="", font=("Arial", 20, "underline"))
day_total.place(relx=.175, rely=.3, anchor=N)

period_total = Label(root, text="", font=("Arial", 20, "underline"))
period_total.place(relx=.825, rely=.3, anchor=N)

period_days = Label(root, text="", font=("Arial", 10))
period_days.place(relx=.775, rely=.42, anchor=N)

period_daily_hours = Label(root, text="", font=("Arial", 10))
period_daily_hours.place(relx=.875, rely=.42, anchor=N)

time_duration = Label(root, text="", font=("Arial", 10))
time_duration.place(relx=.275, rely=.4, anchor=N)

employee_task_header_label = Label(root, text="", font=("Arial", 20, "underline"))
employee_task_header_label.place(relx=.5, rely=.7, anchor=N)

employee_task_label = Label(root, text="", font=("Arial", 13), wraplength=300, justify="center")
employee_task_label.place(relx=.5, rely=.77, anchor=N)

z_time_clock_label = Label(root, text="ZTimeClock Ver 1.01", font=("Arial", 10))
z_time_clock_label.place(relx=.945, rely=.97, anchor=N)

















# #Admin Widgets:

# #Employee Codes
# employee_codes_label_for_button = Label(root, text="", font=("Arial", 15))
# employee_codes_label_for_button.place(relx=.4605, rely=.29, anchor=N)
# employee_codes_button = Button(root, text="", font=("Arial", 15))

# #Assign Tasks
# assign_tasks_label_for_button = Label(root, text="", font=("Arial", 15))
# assign_tasks_label_for_button.place(relx=.4605, rely=.33, anchor=N)
# assign_tasks_button = Button(root, text="", font=("Arial", 15))

# #Current Period Totals
# period_totals_label_for_button = Label(root, text="", font=("Arial", 15))
# period_totals_label_for_button.place(relx=.4605, rely=.37, anchor=N)
# period_totals_button = Button(root, text="", font=("Arial", 15))

# #Historical Totals
# historical_totals_label_for_button = Label(root, text="", font=("Arial", 15))
# historical_totals_label_for_button.place(relx=.4605, rely=.41, anchor=N)
# historical_totals_button = Button(root, text="", font=("Arial", 15))


main_menu = LabelFrame(root, padx=50, pady=25)



employee_codes_label_for_button = Label(root)
employee_codes_button = Button(root)
#Sub buttons
employee_codes_button__add_new_employee_label_for_button = Label(root)
employee_codes_button__add_new_employee_button = Button(root)
employee_codes_button__edit__label_for_button = Label(root)
employee_codes_button__edit_button = Button(root)
employee_codes_button__delete_label_for_button = Label(root)
employee_codes_button__delete_button = Button(root)
employee_codes_button__view_label_for_button = Label(root)
employee_codes_button__view_button = Button(root)






assign_tasks_label_for_button = Label(root)
assign_tasks_button = Button(root)
period_totals_label_for_button = Label(root)
period_totals_button = Button(root)
historical_totals_label_for_button = Label(root)
historical_totals_button = Button(root)



















# employee_hours_button = Button(root, text="", font=("Arial", 10))

# employee_list_label = Label(root, text="", font=("Arial", 10))
# employee_list_label.place(relx=.48, rely=.32, anchor=N)

# employee_hours_label = Label(root, text="", font=("Arial", 10))
# employee_hours_label.place(relx=.52, rely=.32, anchor=N)

# start_date_label = Label(root, text="", font=("Arial", 10))
# start_date_label.place(relx=.4, rely=.28, anchor=CENTER)

# end_date_label = Label(root, text="", font=("Arial", 10))
# end_date_label.place(relx=.5, rely=.28, anchor=CENTER)

# employee_start_date = Entry(root, text="", font=("Arial", 10))
# employee_end_date = Entry(root, text="", font=("Arial", 10))

# Creates the mainloop of the application to constantly check for input events like clicking a button or entering text in a entry widget.
root.mainloop()

#[start_date_label, end_date_label, greeting, time_in, time_out, time_duration, employee_list_label, employee_hours_label], [employee_hours_button, employee_start_date, employee_end_date]