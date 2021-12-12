import sqlite3
from sqlite3.dbapi2 import Error
from datetime import date, datetime, timedelta
from UsefulFunctions import *
from calendar import monthrange


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
            "SELECT FirstName, LastName, Department, HourlyPay, OTAllowed, MaxDailyHours, HireDate, TermDate, Hourly, PartTime, Birthday, EMail, CellNum FROM employees WHERE ID = ?;",
            param=(emp_id,), fetch_str="one")
        if data is None: raise Exception(f"Invalid Employee ID: \"{emp_id}\"")
        self.first, self.last, self.department, self.hourly_pay, self.ot_allowed, self.max_daily_hours, self.hire_date, self.term_date, self.hourly, self.part_time, self.birthday, self.email, self.cell_num = data
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

    def get_hours_and_pay(self, start_date, end_date, entered_format):
        """
        Calculates employee pay, accounting for regular, overtime, and double time hours, and returns the result as a dictionary.

        """

        try:
            round(self.hourly_pay, 2)
        except TypeError:
            return {
                "ID": self.emp_id,
                "FLast": self.first[0] + self.last,
                "Regular Hours": "",
                "Regular Pay": "",
                "Overtime Hours": "",
                "Overtime Pay": "",
                "Double Time Hours": "",
                "Double Time Pay": "",
                "Total Hours": 0,
                "Total Pay": ""
            }

        array_of_hours_per_day = self.get_range_hours_accounting_for_breaks(start_date, end_date, entered_format)

        regular_hours = 0
        overtime_hours = 0
        double_time_hours = 0
        if self.ot_allowed == "yes":
            for hours_per_day in array_of_hours_per_day[1]:
                if hours_per_day <= 8:
                    regular_hours += hours_per_day
                elif 8 < hours_per_day <= 12:
                    regular_hours += 8
                    overtime_hours += hours_per_day - 8
                else:
                    regular_hours += 8
                    overtime_hours += 4
                    double_time_hours += hours_per_day - 12
        elif self.ot_allowed == "no":
            regular_hours = array_of_hours_per_day[0]

        regular_hours = round(regular_hours, 2)
        overtime_hours = round(overtime_hours, 2)
        double_time_hours = round(double_time_hours, 2)

        hourly_pay = round(self.hourly_pay, 2)

        regular_pay = round(hourly_pay * regular_hours, 2)
        overtime_pay = round(hourly_pay * 1.5 * overtime_hours, 2)
        double_time_pay = round(hourly_pay * 2 * double_time_hours, 2)

        total_pay = round(regular_pay + overtime_pay + double_time_pay, 2)
        total_hours = round(array_of_hours_per_day[0], 2)

        # Uncomment the following to check if total_hours is correct.
        # if total_hours != round(regular_hours + overtime_hours + double_time_hours, 2):
        #     print("ID", id, ":", "WRONG Hours")

        # returned_array = [total_pay, [regular_hours, overtime_hours, double_time_hours], [regular_pay, overtime_pay, double_time_pay]]

        dictionary = {
            "ID": self.emp_id,
            "FLast": self.first[0] + self.last,
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

    def max_hours_allowed_on_payday(self):
        current_period_dates = get_period_days()
        emp_worked_hours_for_period = \
            self.get_hours_and_pay(current_period_dates[0], current_period_dates[-1], "%m/%d/%y")["Regular Hours"]

        total_period_hours_allowed = self.max_daily_hours * sum(
            [datetime.strptime(adate, "%m/%d/%y").isoweekday() < 6 for adate in current_period_dates])
        total_hours_possible_on_payday = total_period_hours_allowed - emp_worked_hours_for_period
        if total_hours_possible_on_payday >= self.max_daily_hours:
            return self.max_daily_hours
        else:
            return total_hours_possible_on_payday

    # Selects an employee's task on a given date.
    def select_task(self, task_date, format):
        task = self.c.exec_sql("SELECT task FROM employee_tasks WHERE employee_id = ? AND task_date = ?;",
                               param=(self.emp_id, datetime.strptime(task_date, format).strftime("%m/%d/%Y")),
                               fetch_str="one")
        if task is not None:
            return task[0]
        else:
            return "You don't have any tasks!"

    def get_status(self):
        # "SELECT row, ClockIn, ClockOut FROM time_clock_entries WHERE empID = '" + entered_id + "' ORDER BY row DESC LIMIT 1;"
        last_record = self.c.exec_sql(
            "SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = ? ORDER BY row DESC LIMIT 1;",
            param=(self.emp_id,),
            fetch_str="one")

        if last_record is None or (last_record[0] is not None and last_record[1] is not None):
            # They either haven't ever clocked in or out, or they are clocked out.
            return False
        elif last_record[0] is not None and last_record[1] is None:
            # They are clocked in.
            return True

    def get_records(self, start, end, format):
        total_hours = self.get_range_hours_accounting_for_breaks(start, end, format)[0]
        # YYYY-MM-DD
        start_reformatted = datetime.strptime(start, format).strftime("%Y-%m-%d")
        end_reformatted = datetime.strptime(end, format).strftime("%Y-%m-%d")
        records = self.c.exec_sql(
            "SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = ? AND date(ClockIn) BETWEEN ? AND ?;",
            param=(self.emp_id, start_reformatted, end_reformatted), fetch_str="all")
        return [[clock_in, clock_out, format_seconds_to_hhmmss(
            datetime.strptime(clock_out, "%Y-%m-%d %H:%M:%S").timestamp() -
            datetime.strptime(clock_in, "%Y-%m-%d %H:%M:%S").timestamp())]
                for clock_in, clock_out in records]

    def get_vac_and_sick(self, from_date="", to_date=datetime.today().strftime("%m/%d/%Y"),
                         dates_format="%m/%d/%Y"):
        if from_date == "":
            from_date = datetime.strptime(self.hire_date, "%m/%d/%Y")
        else:
            from_date = datetime.strptime(from_date, dates_format)
        to_date = datetime.strptime(to_date, dates_format)
        print(from_date.strftime("%m/%d/%Y"))
        print(to_date.strftime("%m/%d/%Y"))

        unique_dates_array = [t[0] for t in
                              list(set(self.c.exec_sql("SELECT Date FROM vac_sick_rates;", fetch_str="all")))]
        # unique_dates_array.append("1/1/3000")

        sorted_unique_dates_array = sorted([datetime.strptime(d, "%m/%d/%Y") for d in unique_dates_array])

        # print(sorted_unique_dates_array)

        since = datetime.strptime(self.hire_date, "%m/%d/%Y")

        loop_date = from_date
        total_sick_accrued = 0
        total_vac_accrued = 0
        loop_counter = 1
        while loop_date <= to_date:
            # tier_date = None
            for index, date_obj in enumerate(sorted_unique_dates_array):
                if loop_date < date_obj:
                    previous_index = index - 1
                    if previous_index >= 0:
                        tier_date = sorted_unique_dates_array[previous_index]
                    else:
                        print("Date < Smallest Tier Date")
                        tier_date = sorted_unique_dates_array[0]
                        loop_date = datetime.strptime(tier_date.strftime("%m/%d/%Y"), "%m/%d/%Y")
                    break
                if index == len(sorted_unique_dates_array) - 1:
                    tier_date = sorted_unique_dates_array[index]
            # assert tier_date is not None, "Older tier must be defined in vac_sick_rates table."
            # print(type(tier_date))
            tier_date = tier_date.strftime("%m/%d/%Y")

            tier_array = sorted([tier[0] for tier in
                                 self.c.exec_sql("SELECT Tier FROM vac_sick_rates WHERE Date = ?;", param=(tier_date,),
                                                 fetch_str="all")])

            total_work_duration = ((loop_date - since).days / 365)
            for index, tier_num in enumerate(tier_array):
                if total_work_duration < tier_num:
                    previous_index = index - 1
                    if previous_index >= 0:
                        final_tier = tier_array[previous_index]
                        break
                    else:
                        # Should never be negative
                        raise Exception("Employee total duration is somehow negative.")
                if index == len(tier_array) - 1:
                    final_tier = tier_array[index]

            tier_record = self.c.exec_sql(
                "SELECT SickGracePeriod, VacGracePeriod, MonthlySickRate, MonthlyVacRate FROM vac_sick_rates WHERE Date = ? AND Tier = ?",
                param=(tier_date, final_tier), fetch_str="one")
            # print(tier_record)

            sick_grace = tier_record[0]
            sick_daily_rate = str_fraction_to_num(tier_record[2]) * 12 / 365

            vac_grace = tier_record[1]
            vac_daily_rate = str_fraction_to_num(tier_record[3]) * 12 / 365



            #loop_date += timedelta(days=1)
            total_vac_accrued += vac_daily_rate
            total_sick_accrued += sick_daily_rate
            loop_counter += 1

         #   if loop_date.day == from_date.day:
            print(loop_date.strftime("%m/%d/%Y"), end=" ")
            print("sick_rate:", sick_daily_rate, end=" ")
            print("vac_rate:", vac_daily_rate, end=" ")
            print("Sick:", total_sick_accrued, "  Vac:", total_vac_accrued)
            loop_date += timedelta(days=1)
        return {
            "SickAccrued": total_sick_accrued,
            "VacAccrued": total_vac_accrued
        }

    def get_time_off(self, period="", period_format="%m/%d/%Y"):
        flast = (self.first[0] + self.last).upper()
        if period == "":
            total_vact = self.c.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE UPPER(EmpID) = ? AND UPPER(LeaveType) = 'VACT'",
                param=(flast,),
                fetch_str="all"
            )
            total_sick = self.c.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE UPPER(EmpID) = ? AND UPPER(LeaveType) = 'SICK'",
                param=(flast,),
                fetch_str="all"
            )
        else:
            total_vact = self.c.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE PeriodEnd = ? UPPER(EmpID) = ? AND UPPER(LeaveType) = 'VACT'",
                param=(flast, datetime.strptime(period, period_format).strftime("%m/%d/%Y")),
                fetch_str="all"
            )
            total_sick = self.c.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE PeriodEnd = ? UPPER(EmpID) = ? AND UPPER(LeaveType) = 'SICK'",
                param=(flast, datetime.strptime(period, period_format).strftime("%m/%d/%Y")),
                fetch_str="all"
            )
        return {
            "Vact": total_vact[0][0],
            "Sick": total_sick[0][0]
        }




emp = Employee("E1341")
# d = emp.get_vac_and_sick()
# print("Sick:", d["SickAccrued"])
# print("Vacation:", d["VacAccrued"])
print(emp.get_time_off()["Sick"])

# print(emp.first)
# print(emp.last)
# print(emp.department)
# print(emp.hourly_pay)
# print(emp.ot_allowed)
# print(emp.max_daily_hours)
# print(emp.get_raw_day_hours("11/9/21", "%m/%d/%y"))
# print("Total Hours:", emp.get_range_hours_accounting_for_breaks("11/1/21", "11/15/21", "%m/%d/%y")[0])
# print("Hours and Pay:", emp.get_hours_and_pay("11/1/21", "11/15/21", "%m/%d/%y"))
# print("Max Hours Allowed on Payday:", emp.max_hours_allowed_on_payday())
# print("Task:", emp.select_task("11/1/21", "%m/%d/%y"))
# print("Status:", emp.get_status())
