import random
from calendar import monthrange
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import time


def count_dec_places(num):
    num_as_str = str(num)
    try:
        dec_index = num_as_str.index(".")
        dec = num_as_str[dec_index + 1:]
        return len(dec)
    except:
        return 0


def round_to(num, nrst, limit):
    """
    Rounds a number to the nearest tenth, quarter..., and makes sure to not exceed a given limit.
    """
    dec = num - int(num)
    dec_remainder = round(dec % nrst, 5)
    print(dec_remainder)

    if dec_remainder == 0:
        return num
    if dec_remainder >= round(nrst / 2, 5):
        rounded_up = int(num) + (dec - dec_remainder) + nrst
        if rounded_up <= limit:
            return round(rounded_up, 5)
    rounded_down = int(num) + (dec - dec_remainder)
    return round(rounded_down if rounded_down <= limit else limit, 5)


# Creates and returns list of dates in the interval [start, end], both inclusive, as a string array.
def get_array_of_dates(start, end, entered_format, result_format):
    start_date = datetime.strptime(start, entered_format)
    end_date = datetime.strptime(end, entered_format)
    result_array = [start_date.strftime(result_format)]
    while start_date < end_date:
        start_date += timedelta(days=1)
        result_array.append(start_date.strftime(result_format))
    return result_array


# Grabs the current period's date range (for calculation use).
def get_period_days():
    result_str = []
    current_date = time.strftime("%x")
    day = int(current_date[3:5])
    month = current_date[0:2]
    year = current_date[6:8]
    # mm/dd/yy
    if 1 <= day < 16:
        for i in range(1, day + 1):
            if i < 10:
                result_str.append(month + "/0" + str(i) + "/" + year)
            else:
                result_str.append(month + "/" + str(i) + "/" + year)
    else:
        for i in range(16, day + 1):
            result_str.append(month + "/" + str(i) + "/" + year)
    return result_str


def format_seconds_to_hhmmss(seconds):
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)


def str_fraction_to_num(fraction: str):
    num, den = fraction.split("/")
    return float(num) / float(den)


# Returns an array of dates in a period depending on what period a given date is in.
def getPeriodFromDateString(date_string, format):
    result_array_of_str_dates = []
    date = str(datetime.strptime(date_string, format).strftime("%m/%d/%y"))
    day = int(date[3:5])
    month = date[0:2]
    year = date[6:8]
    if day >= 1 and day < 16:
        for i in range(1, day + 1):
            if i < 10:
                result_array_of_str_dates.append(month + "/0" + str(i) + "/" + year)
            else:
                result_array_of_str_dates.append(month + "/" + str(i) + "/" + year)
    else:
        for i in range(16, day + 1):
            result_array_of_str_dates.append(month + "/" + str(i) + "/" + year)
    return result_array_of_str_dates

def is_given_day_in_given_period(day_obj: datetime, period_of_day_obj: datetime):
    if 1 <= period_of_day_obj.day <= 15:
        starting_day = 1
        ending_day = 15
    else:
        starting_day = 16
        ending_day = monthrange(period_of_day_obj.year, period_of_day_obj.month)[1]

    current_day = datetime.strptime(f"{period_of_day_obj.month}/{starting_day}/{period_of_day_obj.year}", "%m/%d/%Y")
    dates_in_period = []
    while current_day.date() <= datetime.strptime(f"{period_of_day_obj.month}/{ending_day}/{period_of_day_obj.year}", "%m/%d/%Y").date():
        dates_in_period.append(current_day)
        current_day += timedelta(days=1)

    return day_obj in dates_in_period

# Checks if a given date is a payday. Note: 15th or last day of the month = end_of_pay_period. It will return True if the date is a weekday and the end_of_pay_period, a Friday but the end_of_pay_period is on the following weekend (1 or 2 days after it), or a Thursday and the end_of_pay_period is a Saturday.
def is_this_a_pay_day(date_in, format):
    date_in = datetime.strptime(date_in, format)
    last_day_of_month = monthrange(date_in.year, date_in.month)[1]

    # check if the date is the 15th, the end of the month, and it's a weekday
    if (date_in.day == 15 or date_in.day == last_day_of_month) and date_in.weekday() <= 4:
        return True
    else:
        # check if the date is <= the 15th, or the end of the month, by two days or less, and it's a Friday
        if ((date_in.day >= 13 and date_in.day <= 15) or (
                date_in.day >= last_day_of_month - 2 and date_in.day <= last_day_of_month)) and date_in.weekday() == 4:
            return True
        else:
            return False


# Creates and returns list of dates in the interval [start, end], both inclusive, as a string array.
def getArrayOfDates(start, end, entered_format, result_format):
    start_date = datetime.strptime(start, entered_format)
    end_date = datetime.strptime(end, entered_format)
    result_array = [start_date.strftime(result_format)]
    while start_date < end_date:
        start_date += timedelta(days=1)
        result_array.append(start_date.strftime(result_format))
    return result_array


# This function returns the period days of a certain period. It passes in a number and generates the period days, both displayed and calculated as a tuple.
# For instance, if the argument = 0, it will fetch the period days of today's period. If the argument = 1, it will fetch the period days of the period after the current one.
# Negative numbers do the same thing, except they go back periods. This function is useful for when the admin toggles between the reports and summaries of certain
# periods. Note: there is a difference between displayed and calculated period days. Calculated period days are strictly all the days between either the 1st - 15th or the 16th - last_day_of_month.
# This is used in all the calculations for period totals, both for employees and the admin. Displayed period days are similar to the calculated period days, however, they
# take into account for whether or not the last day of the period is a weekday or not. If the last day of the period lands on a weekend, the displayed period days will
# end at the last weekday before the end of the period. The displayed period days are useful when displaying the period days in a report, and the calculated period days are useful when
# looping through every single day in a period from the 1st - 15th or the 16th - last_day_of_month to do payroll calculations.
def get_period_days_with_num(num):
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

    temporary_date = datetime.strptime((today + relativedelta(months=additional_months)).strftime("%m/%d/%Y"),
                                       "%m/%d/%Y").strftime("%m/%d/%Y")
    beginning_of_period = temporary_date[:3] + day + temporary_date[5:]

    end_of_period = datetime.strptime(beginning_of_period, "%m/%d/%Y")
    while not is_this_a_pay_day(end_of_period.strftime("%m/%d/%Y"), "%m/%d/%Y"):
        end_of_period += timedelta(days=1)

    last_day_of_calculated_period_days = 0
    if day == "16":
        # mm/dd/yy
        last_day_of_calculated_period_days = str(
            monthrange(int(beginning_of_period[6:]), int(beginning_of_period[:2]))[1])
    else:
        last_day_of_calculated_period_days = "15"

    # (displayed_period_boundaries, calculated_pay_days_from_1_to_15)

    return (
        (datetime.strptime(beginning_of_period, "%m/%d/%Y").strftime("%m/%d/%y"), end_of_period.strftime("%m/%d/%y")),
        tuple(getArrayOfDates(beginning_of_period, end_of_period.strftime("%m/%d/%Y")[
                                                   :3] + last_day_of_calculated_period_days + end_of_period.strftime(
            "%m/%d/%Y")[5:], "%m/%d/%Y", "%m/%d/%y")))


# print(getPeriodFromDateString("12/13/2021", "%m/%d/%Y"))

def get_opposite_direction(direction):
    if direction == "up":
        return "down"
    elif direction == "down":
        return "up"
    elif direction == "right":
        return "left"
    else:
        return "right"


def pick_rand_direction():
    return random.choice(["up", "down", "left", "right"])


def validate_timestamp(time_stamp, format):
    try:
        datetime.strptime(time_stamp, format)
    except:
        return False
    return True
