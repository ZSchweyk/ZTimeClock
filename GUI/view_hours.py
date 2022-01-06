from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_hours.kv")


class ViewHours(StaticWidgets):
    emp_obj: Employee = None

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.back_button()