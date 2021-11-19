import sqlite3
from sqlite3.dbapi2 import Error
from datetime import date, datetime, timedelta
from UsefulFunctions import *




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
        if data is None: raise Exception(f"Invalid Employee ID: \"{emp_id}\"")
        self.first, self.last, self.department, self.hourly_pay, self.ot_allowed, self.max_daily_hours = data
        self.ot_allowed = self.ot_allowed.lower()
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

        time_in_out_records = self.c.exec_sql(
            "SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = ? AND ClockIn LIKE ?;",
            param=(self.emp_id, f"%{formatted_entered_date}%"), fetch_str="all")

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

    # Uses the result from getTotalDailyHoursAccountingForBreaks() in order to calculate an employee's total paid employee hours in a specific range of dates.
    def get_range_hours_accounting_for_breaks(self, start_date, end_date, entered_format):
        dates = get_array_of_dates(start_date, end_date, entered_format, "%Y-%m-%d")
        total_range_hours = 0
        array_of_total_hours_per_day = []
        for single_date in dates:
            day_hours_accounting_for_breaks = self.get_day_hours_accounting_for_breaks(single_date, "%Y-%m-%d")
            total_range_hours += day_hours_accounting_for_breaks
            array_of_total_hours_per_day.append(day_hours_accounting_for_breaks)
        return total_range_hours, array_of_total_hours_per_day

    # Calculates employee pay, accounting for regular, overtime, and double time hours, and returns the result as a dictionary.
    def get_hours_and_pay(self, start_date, end_date, entered_format):
        conn = sqlite3.connect(database_file)
        c = conn.cursor()

        array_of_hours_per_day = self.get_range_hours_accounting_for_breaks(start_date, end_date, entered_format)[1]

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
                    regular_hours += hours_per_day
                elif hours_per_day > 8 and hours_per_day < 12:
                    regular_hours += 8
                    overtime_hours += hours_per_day - 8
                else:
                    regular_hours += 8
                    overtime_hours += 4
                    double_time_hours += hours_per_day - 12
        elif ot_allowed == "no":
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
        # if total_hours != round(regular_hours + overtime_hours + double_time_hours, 2):
        #     print("ID", id, ":", "WRONG Hours")

        # returned_array = [total_pay, [regular_hours, overtime_hours, double_time_hours], [regular_pay, overtime_pay, double_time_pay]]

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


emp = Employee("E3543")
print(emp.first)
print(emp.last)
print(emp.department)
print(emp.hourly_pay)
print(emp.ot_allowed)
print(emp.max_daily_hours)
print(emp.get_raw_day_hours("11/9/21", "%m/%d/%y"))
print("Total Hours:", emp.get_range_hours_accounting_for_breaks("11/1/21", "11/15/21", "%m/%d/%y")[0])
