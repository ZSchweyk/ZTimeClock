import kivy
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
import kivymd
from kivy.config import Config

Config.set("graphics", "resizable", False)

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.lang import Builder
from kivy.core.window import Window
from datetime import datetime
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager

from static_widgets import StaticWidgets
from login_screen import LoginScreen
from employee_menu_screen import EmployeeMenuScreen
from clock_in_or_out import ClockInOrOut
from view_hours import ViewHours
from request_vacation import RequestVacation
from view_time_off import ViewTimeOff

Window.size = (1280, 800)
Window.top = 350
Window.left = 600

class zTimeClock(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        Builder.load_file("login_screen.kv")
        self.sm = ScreenManager()
        self.sm.add_widget(StaticWidgets(name="static widgets"))
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(EmployeeMenuScreen(name="employee menu"))
        self.sm.add_widget(ClockInOrOut(name="clock in or out"))
        self.sm.add_widget(ViewHours(name="view hours"))
        self.sm.add_widget(RequestVacation(name="request vacation"))
        self.sm.add_widget(ViewTimeOff(name="view time off"))
        self.sm.current = "login"
        return self.sm


if __name__ == "__main__":
    zTimeClock().run()
