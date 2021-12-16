from my_import_statements import *
from back_button import BackButton

Builder.load_file("view_hours.kv")

class ViewHours(BackButton):
    emp_obj: Employee = None

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.back_button()

