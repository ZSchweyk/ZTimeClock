from datetime import date, datetime, timedelta
import sqlite3
from dateutil.relativedelta import relativedelta
from calendar import monthrange, week
import pandas as pd

def getArrayOfDates(start, end, entered_format, result_format):
    start_date = datetime.strptime(start, entered_format)
    end_date = datetime.strptime(end, entered_format)
    result_array = [start_date.strftime(result_format)]
    while start_date < end_date:
        start_date += timedelta(days=1)
        result_array.append(start_date.strftime(result_format))
    return result_array

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
            print("first")
            additional_months = int((num + 1) / 2)
        elif num / 2 != int(num / 2):
            print("second")
            additional_months = int((num + 1) / 2)
        else:
            print("third")
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



print(get_period_days(-8))