import time

from my_import_statements import *
from static_widgets import StaticWidgets
import view_hours

Builder.load_file("employee_menu_screen.kv")


class EmployeeMenuScreen(StaticWidgets):
    emp_obj: Employee = None
    name_label = ObjectProperty(None)
    clock_in_or_out = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.name_label.text = self.emp_obj.first + " " + self.emp_obj.last

        self.clock_in_or_out.text = "Clock Out" if self.emp_obj.get_status() else "Clock In"

        # self.clock_in_or_out = MDRoundFlatButton(
        #                   text="Clock Out" if self.emp_obj.get_status() else "Clock In",
        #                   pos_hint={"center_x": .5, "center_y": .6},
        #                   font_size=30,
        #                   on_release=lambda x: self.view_hours(clock_in_out=True)
        #                   )
        # self.add_widget(self.clock_in_or_out)

        self.back_button(back_to_text="Login Screen", back_to_screen="login", direction="right")

    def view_hours(self, clock_in_out=False):
        if self.emp_obj.get_type() == "Salary":
            dialog = MDDialog(
                text="                               Unapplicable for Salaried employees.",
                radius=[20, 7, 20, 7]
            )
            dialog.open()
        elif clock_in_out and not self.emp_obj.get_status() and not self.emp_obj.can_clock_in(min_wait_seconds=0):
            dialog = MDDialog(
                text="                                     You can't clock back in so soon.",
                radius=[20, 7, 20, 7]
            )
            dialog.open()
        else:
            view_hours.ViewHours.emp_obj = self.emp_obj
            view_hours.ViewHours.clock_in_or_out = clock_in_out
            MDApp.get_running_app().sm.transition.direction = "left"
            MDApp.get_running_app().sm.current = "view hours"
