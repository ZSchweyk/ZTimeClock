from kivy.metrics import dp

from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_hours.kv")

class ViewHours(StaticWidgets):
    emp_obj: Employee = None
    clock_in_or_out: bool = None
    name_and_status = ObjectProperty(None)
    date_and_total_day_hours = ObjectProperty(None)
    # time_in = ObjectProperty(None)
    # time_out = ObjectProperty(None)
    # duration = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

    def show_day_totals(self, day):
        daily_records, total_day_hours = \
            self.emp_obj.get_records_and_hours_for_day(day.strftime("%m/%d/%y"), "%m/%d/%y")
        self.date_and_total_day_hours.text=" "*6+f"{day.strftime('%m/%d/%y')}\nTotal Hours: {round(total_day_hours, 2)}"

        # self.time_in.text = "    Time In\n" + "-" * 20 + "\n"
        # self.time_out.text = "   Time Out\n" + "-" * 20 + "\n"
        # self.duration.text = "   Duration\n" + "-" * 20 + "\n"
        # for rec in daily_records:
        #     self.time_in.text += rec[0] + "\n"
        #     self.time_out.text += rec[1] + "\n"
        #     self.duration.text += "   " + rec[2] + "\n"


        left_table = MDDataTable(
            use_pagination=True,
            check=False,
            size_hint=(.35, .5),
            column_data=[
                ("Time In", dp(30)),
                ("Time Out", dp(30)),
                ("Duration", dp(30))
            ],
            row_data=daily_records
        )

        self.add_widget(left_table)


    def show_period_totals(self):
        pass

    def on_pre_enter(self, *args):
        self.back_button()
        if self.clock_in_or_out:
            if self.emp_obj.clock_in_or_out(min_wait_seconds=0):
                self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last + \
                                            f"\nYou're clocked {'in' if self.emp_obj.get_status() else 'out'}"
        else:
            self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last + "\nHere are your hours"

        self.show_day_totals(datetime.today())

