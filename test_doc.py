from datetime import date, datetime, timedelta
import sqlite3
from dateutil.relativedelta import relativedelta
from calendar import monthrange, week
# from datascience import Table

def get_requests():
    conn = sqlite3.connect("employee_time_clock.db")
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

print(get_requests())