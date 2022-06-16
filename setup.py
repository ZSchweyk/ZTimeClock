#https://stackabuse.com/creating-executable-files-from-python-scripts-with-py2exe/

from distutils.core import setup # Need this to handle modules
import py2exe 

from ast import Index
from sqlite3.dbapi2 import Error, PARSE_DECLTYPES
from tkinter import *
from tkinter import ttk
import tkinter.ttk
from tkinter import messagebox
import sqlite3
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import random
from calendar import month, monthrange, week
from typing import AsyncContextManager
import smtplib
import mimetypes
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
#from openpyxl import load_workbook
import xlsxwriter as xl
import json
from tkinter.filedialog import askdirectory, asksaveasfile, asksaveasfilename
import os
import sys

setup(windows=['ztimeclock.py'])
