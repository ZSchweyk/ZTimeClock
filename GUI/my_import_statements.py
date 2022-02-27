import sys
sys.path.insert(0, "..")

from settings import *

import kivy
import kivymd
from kivy.config import Config
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.picker import MDTimePicker
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.window import Window
from datetime import datetime
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from RequiredClasses.employee_class import Employee
from RequiredClasses.zsqlite_class import ZSqlite
from RequiredClasses.UsefulFunctions import *
import random
import time
from threading import Thread

Employee.db_path = "../employee_time_clock.db"
c = ZSqlite(Employee.db_path)

