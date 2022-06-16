from .UsefulFunctions import *
from calendar import monthrange
from RequiredClasses.zsqlite_class import ZSqlite


class Employee(ZSqlite):
    db_path: str = None

    def __init__(self, emp_id):
        super().__init__(self.db_path)
        data = self.exec_sql(
            "SELECT FirstName, LastName, Department, HourlyPay, OTAllowed, MaxDailyHours, HireDate, TermDate, Hourly, PartTime, Birthday, EMail, CellNum FROM employees WHERE ID = ?;",
            param=(emp_id,), fetch_str="one")
        if data is None: raise Exception(f"Invalid Employee ID: \"{emp_id}\"")
        self.first, self.last, self.department, self.hourly_pay, self.ot_allowed, self.max_daily_hours, self.hire_date, self.term_date, self.hourly, self.part_time, self.birthday, self.email, self.cell_num = data
        self.ot_allowed = self.ot_allowed.lower()
        self.emp_id = emp_id
        self.min_wait_time = 10 * 60

    def __repr__(self):
        return f"Employee({self.emp_id})"

    def get_type(self):
        if self.hourly.lower() == "salary":
            return "Salary"
        elif self.part_time.lower() == "ptime":
            return "Hourly PT"
        else:
            return "Hourly FT"

    def get_raw_day_hours(self, entered_date, format):
        """
        Grabs an employees raw employee hours for a certain date.
        It simply subtracts the clock in timestamp from the clock out timestamp in the database.
        If an employee forgot to clock out, it makes the duration for that record 0.

        """

        time_in_out_records = self.exec_sql(
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

        time_in_out_records = self.exec_sql(
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
        task = self.exec_sql("SELECT task FROM employee_tasks WHERE employee_id = ? AND task_date = ?;",
                             param=(self.emp_id, datetime.strptime(task_date, format).strftime("%m/%d/%Y")),
                             fetch_str="one")
        if task is not None:
            return task[0]
        else:
            return "You don't have any tasks!"

    def get_last_entry(self, desired_column=""):
        if self.get_status():
            column = "ClockIn"
        else:
            column = "ClockOut"
        column = desired_column if desired_column == "ClockIn" or desired_column == "ClockOut" else column
        return self.exec_sql(
            f"SELECT {column} FROM time_clock_entries WHERE empID = ? ORDER BY row DESC LIMIT 1;",
            param=(self.emp_id,),
            fetch_str="one"
        )[0]

    def came_to_work_on(self, day: datetime):
        query = self.exec_sql(
            "SELECT ClockIn FROM time_clock_entries WHERE ClockIn LIKE ? LIMIT 1;",
            param=(day.strftime("%Y-%m-%d%%"),),
            fetch_str="one"
        )
        return query is not None

    def get_status(self):
        # "SELECT row, ClockIn, ClockOut FROM time_clock_entries WHERE empID = '" + entered_id + "' ORDER BY row DESC LIMIT 1;"
        last_record = self.exec_sql(
            "SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = ? ORDER BY row DESC LIMIT 1;",
            param=(self.emp_id,),
            fetch_str="one")

        if last_record is None or (last_record[0] is not None and last_record[1] is not None):
            # They either haven't ever clocked in or out, or they are clocked out.
            return False
        elif last_record[0] is not None and last_record[1] is None:
            # They are clocked in.
            return True

    def request_clock_out(self, timestamp, format="%I:%M:%S %p"):
        print(timestamp)
        print(datetime.strptime(timestamp, format).strftime("%H:%M:%S"))
        if self.get_status():
            row_to_insert, clock_in = self.exec_sql(
                "SELECT row, ClockIn FROM time_clock_entries WHERE empID = ? ORDER BY row DESC LIMIT 1;",
                param=(self.emp_id,),
                fetch_str="one")
            date_to_insert = clock_in[:11] + datetime.strptime(timestamp, format).strftime("%H:%M:%S")
            self.exec_sql(
                "UPDATE time_clock_entries SET ClockOut = 'FORGOT', Request = ? WHERE row = ?;",
                param=(date_to_insert, row_to_insert,)
            )
            return True
        else:
            return False

    def clock_in_or_out(self):
        if self.get_status():
            # Clock them out
            row_to_insert, clock_in = self.exec_sql(
                "SELECT row, ClockIn FROM time_clock_entries WHERE empID = ? ORDER BY row DESC LIMIT 1;",
                param=(self.emp_id,),
                fetch_str="one")
            if datetime.today().date() == datetime.strptime(clock_in, "%Y-%m-%d %H:%M:%S").date():
                self.exec_sql("UPDATE time_clock_entries SET ClockOut = DateTime('now', 'localtime') WHERE row = ?",
                              param=(row_to_insert,)
                              )
                return True
            else:
                return False
        else:
            # Clock them in
            if self.can_clock_in(min_wait_seconds=self.min_wait_time):
                self.exec_sql(
                    "INSERT INTO time_clock_entries(empID, ClockIn) VALUES(?, DateTime('now', 'localtime'))",
                    param=(self.emp_id,)
                )
                return True
            else:
                return False

    def can_clock_in(self, min_wait_seconds=0):
        if not self.get_status():
            clock_out = self.exec_sql(
                "SELECT ClockOut FROM time_clock_entries WHERE empID = ? AND ClockIn != '' AND ClockOut != '' ORDER BY row DESC LIMIT 1;",
                param=(self.emp_id,),
                fetch_str="one")[0]
            if clock_out == "FORGOT":
                return True
            clock_out = datetime.strptime(clock_out, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - clock_out).seconds >= min_wait_seconds:
                return True
            return False

    def get_records_and_hours_for_day(self, desired_date, format):
        desired_date = datetime.strptime(desired_date, format).strftime("%Y-%m-%d")
        records = self.exec_sql(
            "SELECT ClockIn, ClockOut FROM time_clock_entries WHERE empID = ? AND date(ClockIn) = ?;",
            param=(self.emp_id, desired_date), fetch_str="all")
        clockin_clockout_duration = []
        seconds = 0
        for clock_in, clock_out in records:
            clock_in = datetime.strptime(clock_in, "%Y-%m-%d %H:%M:%S")
            if clock_out is not None:
                if clock_out == "FORGOT":
                    clockin_clockout_duration.append([clock_in.strftime("%I:%M:%S %p"),
                                                      "FORGOT",
                                                      ""
                                                      ])
                else:
                    clock_out = datetime.strptime(clock_out, "%Y-%m-%d %H:%M:%S")
                    seconds += clock_out.timestamp() - clock_in.timestamp()
                    clockin_clockout_duration.append([clock_in.strftime("%I:%M:%S %p"),
                                                      clock_out.strftime("%I:%M:%S %p"),
                                                      format_seconds_to_hhmmss(
                                                          clock_out.timestamp() - clock_in.timestamp())
                                                      ])
            else:
                clockin_clockout_duration.append([clock_in.strftime("%I:%M:%S %p"), "", ""])

        return clockin_clockout_duration, seconds / (60 * 60)

    def get_records_and_daily_hours_for_period(self, current_day, date_format):
        period_days_until_current_day = getPeriodFromDateString(current_day, date_format)
        total_hours = 0
        daily_hours = []
        for day in period_days_until_current_day:
            r_and_h = self.get_records_and_hours_for_day(day, "%m/%d/%y")
            total_hours += r_and_h[1]
            daily_hours.append([day, r_and_h[1]])
        return daily_hours, total_hours

    def get_vac_and_sick(self, from_date="", to_date=datetime.today().strftime("%m/%d/%Y"),
                         dates_format="%m/%d/%Y"):
        if from_date == "":
            from_date = datetime.strptime(self.hire_date, "%m/%d/%Y")
        else:
            from_date = datetime.strptime(from_date, dates_format)
        to_date = datetime.strptime(to_date, dates_format)
        # print(from_date.strftime("%m/%d/%Y"))
        # print(to_date.strftime("%m/%d/%Y"))

        unique_dates_array = [t[0] for t in
                              list(set(self.exec_sql("SELECT Date FROM vac_sick_rates;", fetch_str="all")))]
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
                                 self.exec_sql("SELECT Tier FROM vac_sick_rates WHERE Date = ?;", param=(tier_date,),
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

            tier_record = self.exec_sql(
                "SELECT SickGracePeriod, VacGracePeriod, MonthlySickRate, MonthlyVacRate FROM vac_sick_rates WHERE Date = ? AND Tier = ?",
                param=(tier_date, final_tier), fetch_str="one")
            # print(tier_record)

            sick_grace = tier_record[0]
            sick_daily_rate = str_fraction_to_num(tier_record[2]) * 12 / 365

            vac_grace = tier_record[1]
            vac_daily_rate = str_fraction_to_num(tier_record[3]) * 12 / 365

            # loop_date += timedelta(days=1)
            total_vac_accrued += vac_daily_rate
            total_sick_accrued += sick_daily_rate
            loop_counter += 1

            #   if loop_date.day == from_date.day:
            # print(loop_date.strftime("%m/%d/%Y"), end=" ")
            # print("sick_rate:", sick_daily_rate, end=" ")
            # print("vac_rate:", vac_daily_rate, end=" ")
            # print("Sick:", total_sick_accrued, "  Vac:", total_vac_accrued)
            loop_date += timedelta(days=1)
        return {
            "SickAccrued": total_sick_accrued,
            "VacAccrued": total_vac_accrued
        }

    def get_time_off(self, period="", period_format="%m/%d/%Y"):
        flast = (self.first[0] + self.last).upper()
        if period == "":
            total_vact = self.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE UPPER(EmpID) = ? AND UPPER(LeaveType) = 'VACT'",
                param=(flast,),
                fetch_str="one"
            )
            total_sick = self.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE UPPER(EmpID) = ? AND UPPER(LeaveType) = 'SICK'",
                param=(flast,),
                fetch_str="one"
            )
        else:
            total_vact = self.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE PeriodEnd = ? AND UPPER(EmpID) = ? AND UPPER(LeaveType) = 'VACT'",
                param=(datetime.strptime(period, period_format).strftime("%m/%d/%y"), flast),
                fetch_str="one"
            )
            total_sick = self.exec_sql(
                "SELECT SUM(LeaveHours) FROM time_off_taken WHERE PeriodEnd = ? AND UPPER(EmpID) = ? AND UPPER(LeaveType) = 'SICK'",
                param=(datetime.strptime(period, period_format).strftime("%m/%d/%y"), flast),
                fetch_str="one"
            )
        return {
            "Vacation": total_vact[0] if total_vact[0] is not None else 0,
            "Sick": total_sick[0] if total_sick[0] is not None else 0
        }
