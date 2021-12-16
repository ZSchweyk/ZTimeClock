import kivy
import kivymd
from kivy.config import Config

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRoundFlatButton
from kivy.lang import Builder
from kivy.core.window import Window
from datetime import datetime
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from employee_class import Employee, ZSqlite
import random
import time