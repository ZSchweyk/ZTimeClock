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