import sqlite3
from sqlite3.dbapi2 import Error
from datetime import date, datetime, timedelta


class ZSqlite:
    def __init__(self, db_path):
        self.db_path = db_path

    def exec_sql(self, sql_str, param=(), fetch_str=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(sql_str, param)
        if fetch_str == "one":
            query = c.fetchone()
        elif fetch_str == "all":
            query = c.fetchall()
        else:
            conn.commit()
            conn.close()
            return

        conn.commit()
        conn.close()

        return query


class Employee:
    db_path = "employee_time_clock.db"

    def __init__(self, emp_id):
        self.c = ZSqlite(self.db_path)
        data = self.c.exec_sql(
            "SELECT FirstName, LastName, Department, HourlyPay, OTAllowed, MaxDailyHours FROM employees WHERE ID = ?",
            param=(emp_id,), fetch_str="one")
        if data is None: raise Exception(f"Invalid Employee ID: {emp_id}")
        self.first, self.last, self.department, self.hourly_pay, self.ot_allowed, self.max_daily_hours = data
        self.emp_id = emp_id

    def get_raw_day_hours(self, entered_date, format):
        """
        Grabs an employees raw employee hours for a certain date.
        It simply subtracts the clock in timestamp from the clock out timestamp in the database.
        If an employee forgot to clock out, it makes the duration for that record 0.

        """

        time_in_out_records = self.c.exec_sql(
            "SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = ? AND ClockIn LIKE ?;",
            param=(self.emp_id, "%" + datetime.strptime(entered_date, format).strftime("%Y-%m-%d") + "%"),
            fetch_str="all")

        total_seconds = 0
        for record in time_in_out_records:
            t0 = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S").timestamp()
            if record[1] is not None:
                if record[1] == "FORGOT":
                    # t1 = t0
                    continue
                else:
                    t1 = datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S").timestamp()
            else:
                # t1 = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f").timestamp()
                # t1 = t0
                continue
            total_seconds += t1 - t0
        employee_hours = total_seconds / 3600
        return employee_hours

    # Grabs the result from getRawTotalEmployeeHours(), calculates an employee's total break time for the day, and contains logic to return an employee's total hours for the day accounting for breaks.
    def get_day_hours_accounting_for_breaks(self, entered_date, format):
        """
        Grabs the result from get_raw_day_hours(), calculates an employee's total break time for the day,
        and contains logic to return an employee's total hours for the day accounting for breaks.

        """
        total_period_hours = self.get_raw_day_hours(entered_date, format)

        formatted_entered_date = str(datetime.strptime(entered_date, format).strftime("%Y-%m-%d"))

        time_in_out_records = self.c.exec_sql("SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = ? AND ClockIn LIKE ?;", param=(self.emp_id, f"%{formatted_entered_date}%"), fetch_str="all")

        total_break_seconds = 0
        for record in range(len(time_in_out_records)):
            if record < len(time_in_out_records) - 1:
                out_to_lunch = datetime.strptime(time_in_out_records[record][1], "%Y-%m-%d %H:%M:%S").timestamp()
                back_from_lunch = datetime.strptime(time_in_out_records[record + 1][0], "%Y-%m-%d %H:%M:%S").timestamp()
                total_break_seconds += back_from_lunch - out_to_lunch

        total_break_hours = total_break_seconds / 3600
        if total_period_hours >= 8:
            if total_break_hours >= .5:
                return total_period_hours
            else:
                return total_period_hours - (.5 - total_break_hours)
        else:
            return total_period_hours


emp = Employee("E3543")
print(emp.first)
print(emp.last)
print(emp.department)
print(emp.hourly_pay)
print(emp.ot_allowed)
print(emp.max_daily_hours)
print(emp.get_raw_day_hours("11/9/21", "%m/%d/%y"))
