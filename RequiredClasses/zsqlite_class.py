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
