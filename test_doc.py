from datetime import date, datetime, timedelta
import sqlite3
from dateutil.relativedelta import relativedelta
from calendar import monthrange, week
import pandas as pd

dictionary = {
    "Name": ["Zeyn", "Rhyan", "Nader", "Deena"],
    "Age": [17, 16, 56, 40]
}
print(pd.DataFrame(dictionary))