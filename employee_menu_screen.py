import time

from my_import_statements import *
from static_widgets import StaticWidgets
import clock_in_or_out

Builder.load_file("employee_menu_screen.kv")


class EmployeeMenuScreen(StaticWidgets):
    emp_obj: Employee = None
    name_label = ObjectProperty(None)
    clock_in_or_out_label = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.name_label.text = self.emp_obj.first + " " + self.emp_obj.last

        self.clock_in_or_out_label.text = "Clock Out" if self.emp_obj.get_status() else "Clock In"

        self.back_button(back_to_text="Login Screen", back_to_screen="login", direction="right")

    def clock_in_or_out(self):
        if self.emp_obj.get_type() == "Salary":
            dialog = MDDialog(
                text="                               Unapplicable for Salaried employees.",
                radius=[20, 7, 20, 7]
            )
            dialog.open()
        elif not self.emp_obj.get_status() and not self.emp_obj.can_clock_in(min_wait_seconds=0):
            dialog = MDDialog(
                text=" " * 15 + "Must wait at least 10 minutes before clocking in again.",
                radius=[20, 7, 20, 7]
            )
            dialog.open()
        else:
            clock_in_or_out.ClockInOrOut.emp_obj = self.emp_obj
            MDApp.get_running_app().sm.transition.direction = "left"
            MDApp.get_running_app().sm.current = "clock in or out"
