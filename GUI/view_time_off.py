from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_time_off.kv")

class ViewTimeOff(StaticWidgets):
    emp_obj: Employee = None
    def __init__(self, **kw):
        super().__init__(**kw)
        self.back_button()