from datetime import date, datetime, timedelta
import sqlite3
from dateutil.relativedelta import relativedelta
from calendar import monthrange, week

def every_index(string, char):
    result_list = []
    for index, letter in enumerate(string):
        if letter == char:
            result_list.append(index)

    return result_list

print(every_index("zasdfzasdfz", "z"))