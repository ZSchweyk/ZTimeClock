from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("request_vacation.kv")

# class MyTextInput(MDTextField):
#     def on_parent(self, widget, parent):
#         self.focus = True



class RequestVacation(StaticWidgets):
    emp_obj: Employee = None
    from_field = ObjectProperty(None)
    to_field = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)


        self.back_button()

    def on_pre_enter(self, *args):
        Clock.schedule_interval(lambda x: setattr(self.from_field, "focus", True), .06)
        Clock.schedule_interval(lambda x: setattr(self.to_field, "focus", True), .06)


