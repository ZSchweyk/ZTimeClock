from kivy.metrics import dp

from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("clock_in_or_out.kv")

class ClockInOrOut(StaticWidgets):
    emp_obj: Employee = None
    name_and_status = ObjectProperty(None)
    date_and_total_day_hours = ObjectProperty(None)
    time_in = ObjectProperty(None)
    time_out = ObjectProperty(None)
    duration = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

    def show_day_totals(self, day):
        daily_records, total_day_hours = \
            self.emp_obj.get_records_and_hours_for_day(day.strftime("%m/%d/%y"), "%m/%d/%y")
        self.date_and_total_day_hours.text=" "*6+f"{day.strftime('%m/%d/%y')}\nTotal Hours: {round(total_day_hours, 2)}"

        self.time_in.text = "      Time In\n" + "-" * 25 + "\n"
        self.time_out.text = "    Time Out\n" + "-" * 25 + "\n"
        self.duration.text = "     Duration\n" + "-" * 25 + "\n"
        y_pos = .57
        self.labels = []
        for rec in daily_records:
            time_in = MDLabel(text=" " + rec[0], pos_hint={"center_x": .52, "center_y": y_pos})
            time_out = MDLabel(text="  " + rec[1], pos_hint={"center_x": .62, "center_y": y_pos})
            duration = MDLabel(text="     " + rec[2], pos_hint={"center_x": .72, "center_y": y_pos})
            self.labels.append([time_in, time_out, duration])
            self.add_widget(time_in)
            self.add_widget(time_out)
            self.add_widget(duration)
            y_pos -= .03

    def on_leave(self, *args):
        Thread(target=self.clear_labels())

    def clear_labels(self):
        for time_in, time_out, duration in self.labels:
            time_in.text = ""
            time_out.text = ""
            duration.text = ""

    def show_period_totals(self):
        pass

    def on_pre_enter(self, *args):
        self.back_button()
        if self.emp_obj.clock_in_or_out(min_wait_seconds=0):
            self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last + \
                                        f"\nYou're clocked {'in' if self.emp_obj.get_status() else 'out'}"

        # self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last + "\nHere are your hours"

        Thread(target=lambda: self.show_day_totals(datetime.today())).start()




