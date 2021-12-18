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
        self.date_and_total_day_hours.text = f"Today's\nTotal Hours: {round(total_day_hours, 2)}"

        self.time_in.text = "Time In\n" + "-" * 25 + "\n"
        self.time_out.text = "Time Out\n" + "-" * 25 + "\n"
        self.duration.text = "Duration\n" + "-" * 25 + "\n"
        y_pos = .37
        self.labels = []
        for rec in daily_records:
            time_in = Label(text=rec[0], pos_hint={"center_x": .4, "center_y": y_pos}, halign="center")
            time_out = Label(text=rec[1], pos_hint={"center_x": .5, "center_y": y_pos}, halign="center")
            duration = Label(text=rec[2], pos_hint={"center_x": .6, "center_y": y_pos}, halign="center")
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
                                        f"\nYou're clocked {'IN' if self.emp_obj.get_status() else 'OUT'}"

        # self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last + "\nHere are your hours"

        Thread(target=lambda: self.show_day_totals(datetime.today())).start()




