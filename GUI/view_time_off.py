from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_time_off.kv")

class ViewTimeOff(StaticWidgets):
    emp_obj: Employee = None

    def __init__(self, **kw):
        super().__init__(**kw)
        self.back_button()

    def on_pre_enter(self, *args):
        table = MDDataTable(
            size_hint=(.55, .25),
            pos_hint={"center_x": .5, "top": .7},
            column_data=[
                          ("", dp(20)),
                          ("Period", dp(20)),
                          ("Total Accrued", dp(30)),
                          ("Total Taken", dp(30)),
                          ("Total Balance", dp(30))
            ],
            row_data=[
                (
                    "Vacation",
                    "",
                    "",
                    "",
                    ""
                ),

                (
                    "Sick",
                    "",
                    "",
                    "",
                    ""
                )

            ]

        )
        self.add_widget(table)
