from my_import_statements import *
from back_button import BackButton

Builder.load_file("employee_menu_screen.kv")

class EmployeeMenuScreen(Screen):
    emp_obj = None
    greeting = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

        

    def on_pre_enter(self, *args):
        self.greeting.text += self.emp_obj.first + " " + self.emp_obj.last
        clock_in_or_out = MDRoundFlatButton(text="Clock Out" if self.emp_obj.get_status else "Clock In",
                          pos_hint={"center_x": .5, "center_y": .5},
                          font_size=30
                          # on_release=#Change Screen
                          )
        self.add_widget(clock_in_or_out)
        # self.back_button(back_to_text="Return to Log in/out Screen", back_to_screen="login")
