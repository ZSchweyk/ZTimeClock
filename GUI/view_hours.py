from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_hours.kv")


class ViewHours(StaticWidgets):
    emp_obj: Employee = None
    date_and_total_day_hours = ObjectProperty(None)
    period_and_total_period_hours = ObjectProperty(None)
    next_day = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.back_button()

    def on_leave(self, *args):
        self.z_clear_widgets()
        self.clear_widgets([self.name_and_status])

    def day_totals(self, day):
        daily_records, total_day_hours = \
            self.emp_obj.get_records_and_hours_for_day(day.strftime("%m/%d/%y"), "%m/%d/%y")

        if day + timedelta(days=1) > self.last_clock_in:
            self.next_day.disabled = True
        else:
            self.next_day.disabled = False

        if day.date() == datetime.today():
            self.date_and_total_day_hours.text = f"Today's\nTotal Hours: {round(total_day_hours, 2)}"
        else:
            self.date_and_total_day_hours.text = f"{day.strftime('%m/%d/%y')}\nTotal Hours: {round(total_day_hours, 2)}"

        for rec in daily_records:
            if rec[1] != "FORGOT":
                item = OneLineListItem(text=f"       {rec[0]}     {rec[1]}     {rec[2]}")
            else:
                item = OneLineListItem(text=f"       {rec[0]}        {rec[1]}     {rec[2]}")
            self.day_list.add_widget(item)
        if len(daily_records) >= 8:
            self.day_sv.do_scroll = True
            self.day_sv.scroll_to(item)
        else:
            self.day_sv.do_scroll = False
            self.day_sv.scroll_y = 1



    def period_totals(self, day_obj):
        day_records, total_period_hours = self.emp_obj.get_records_and_daily_hours_for_period(day_obj.strftime("%m/%d/%y"), "%m/%d/%y")
        for day, day_hours in day_records:
            str_duration = str(round(day_hours, 2))
            if str_duration == "0.0":
                item = OneLineListItem(text=f" {day}                   0")
            elif len(str_duration) == 3:
                item = OneLineListItem(text=f" {day}                 {str_duration}")
            elif len(str_duration) == 4:
                item = OneLineListItem(text=f" {day}                {str_duration}")
            else:
                item = OneLineListItem(text=f" {day}                {str_duration}")

            self.period_list.add_widget(item)

        if 1 <= day_obj.day <= 15:
            last_day_of_period = 15
        else:
            last_day_of_period = monthrange(day_obj.year, day_obj.month)

        self.period_and_total_period_hours.text = day_obj.strftime(f"%m/{last_day_of_period}/%y") + f"\n Total: {round(total_period_hours, 2)}"

    def z_clear_widgets(self):
        self.day_list.clear_widgets()
        self.period_list.clear_widgets()

    def change_day(self, inc):
        if inc != 0:
            self.z_clear_widgets()
        self.current_day += timedelta(days=inc)
        self.day_totals(self.current_day)
        self.period_totals(self.current_day)

    def on_pre_enter(self, *args):
        self.name_and_status = Label(
            pos_hint={"center_x": .5, "center_y": .6},
            halign="center",
            font_size=30
        )
        self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last + \
                                    f"\nYou're clocked {'IN' if self.emp_obj.get_status() else 'OUT'}"
        self.add_widget(self.name_and_status)

        # Setup the day totals
        self.day_sv = ScrollView(
            pos_hint={"center_x": .16, "top": .55},
            size_hint=(.3, .44)
        )
        self.add_widget(self.day_sv)
        self.day_list = MDList()
        self.day_sv.add_widget(self.day_list)

        # Setup the period totals
        self.period_sv = ScrollView(
            pos_hint={"center_x": .853, "top": .55},
            size_hint=(.2, .4)
        )
        self.add_widget(self.period_sv)
        self.period_list = MDList()
        self.period_sv.add_widget(self.period_list)

        self.last_clock_in = datetime.strptime(self.emp_obj.get_last_entry(desired_column="ClockIn")[:10], "%Y-%m-%d")
        self.current_day = self.last_clock_in
        self.change_day(0)
