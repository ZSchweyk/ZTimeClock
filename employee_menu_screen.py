from my_import_statements import *
from back_button import BackButton

Builder.load_file("employee_menu_screen.kv")

class EmployeeMenuScreen(BackButton):
    emp_obj = None
    greeting = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        

    def on_pre_enter(self, *args):
        self.greeting.text += self.emp_obj.first + " " + self.emp_obj.last
