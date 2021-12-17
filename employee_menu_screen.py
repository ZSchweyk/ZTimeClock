from my_import_statements import *
from static_widgets import StaticWidgets
import view_hours

Builder.load_file("employee_menu_screen.kv")

class EmployeeMenuScreen(StaticWidgets):
    emp_obj: Employee = None
    greeting = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.greeting.text = "Hello\n" + self.emp_obj.first + " " + self.emp_obj.last
        clock_in_or_out = MDRoundFlatButton(text="Clock Out" if self.emp_obj.get_status else "Clock In",
                          pos_hint={"center_x": .5, "center_y": .5},
                          font_size=30,
                          on_release=lambda x: self.view_hours(clock_in_out=True)
                          )
        self.add_widget(clock_in_or_out)
        self.back_button(back_to_text="Return to Log in/out Screen", back_to_screen="login", direction="right")

    def view_hours(self, day=datetime.today(), clock_in_out=False):
        view_hours.ViewHours.emp_obj = self.emp_obj
        MDApp.get_running_app().sm.transition.direction = "left"
        MDApp.get_running_app().sm.current = "view hours"
