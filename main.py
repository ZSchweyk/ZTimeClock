import kivy
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

from login_screen import LoginScreen
from employee_menu_screen import EmployeeMenuScreen
from view_hours import ViewHours
from back_button import BackButton

Window.size = (1250, 800)


class ZTimeClock(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        Builder.load_file("login_screen.kv")
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(EmployeeMenuScreen(name="employee menu"))
        self.sm.add_widget(ViewHours(name="view hours"))
        self.sm.add_widget(BackButton(name="back button"))
        self.sm.current = "login"
        return self.sm


if __name__ == "__main__":
    ZTimeClock().run()
