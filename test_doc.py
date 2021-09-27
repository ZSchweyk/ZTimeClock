from datetime import date, datetime, timedelta
import sqlite3
from dateutil.relativedelta import relativedelta
from calendar import monthrange, week
from tkinter import messagebox
# from datascience import Table

def validate_timestamp(time_string, format):
    try:
        datetime.strptime(time_string, format)
    except ValueError:
        return False
    else:
        return True

def assign_tasks__by_employee_submit_button(id_string, task, date_string):
    if task == "" or date_string == "" or id_string == "":
        messagebox.showerror("Empty field(s)!", "No tasks were assigned. 'Task', 'Date', or 'Department' fields were blank.")
        return

    conn = sqlite3.connect("employee_time_clock.db")
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
            successful_dates.append(single_date)
        else:
            unsuccessful_dates.append(single_date)


    print("Successful Ids:", successful_ids)
    print("Unsuccessful Ids:", unsuccessful_ids)

    successful = "Successful:\n"
    successful_over_written = "\tOver-written:\n"
    successful_updated = "\tNew:\n"
    unsuccessful = "Unsuccessful\n"
    unsuccessful_ids_str = "\tIDs:\n"
    unsuccessful_dates_str = "\tDates:\n"

    for single_id in successful_ids:
        for single_date in successful_dates:
            task_from_table = c.execute("SELECT task_id, task FROM employee_tasks WHERE employee_id = @0 AND task_date = @1;", (single_id, single_date,)).fetchone()
            
            name = c.execute(f"SELECT FirstName, LastName FROM employees WHERE ID = @0;", (single_id,)).fetchone()
            if task_from_table != None:
                c.execute("UPDATE employee_tasks SET task = @0 WHERE task_id = @1;", (task, task_from_table[0],))
                successful_over_written += f"\t\t\"{name[0]} {name[1]}'s\" task, \"{task_from_table[1]}\", on \"{single_date}\" was over-written.\n"
            else:
                c.execute("INSERT INTO employee_tasks(employee_id, task_date, task) VALUES(@0, @1, @2);", (single_id, single_date, task,))
                successful_updated += f"\t\tA task for \"{name[0]} {name[1]}\" on \"{single_date}\" was added.\n"
    
    for id in unsuccessful_ids:
        unsuccessful_ids_str += f"\t\t{str(id)}\n"
    for date in unsuccessful_dates:
        unsuccessful_dates_str += f"\t\t{date}\n"

    conn.commit()
    conn.close()
    message = successful + successful_over_written + successful_updated + unsuccessful + unsuccessful_ids_str + unsuccessful_dates_str
    messagebox.showinfo("Report", message)
    return


assign_tasks__by_employee_submit_button("1342,5761,12,4251,566,test", "test", "9/27/2021")