from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_hours.kv")


class ViewHours(StaticWidgets):
    emp_obj: Employee = None
    date_and_total_day_hours = ObjectProperty(None)
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

        if day + timedelta(days=1) > datetime.today():
            self.next_day.disabled = True
        else:
            self.next_day.disabled = False

        if day.date() == datetime.today():
            self.date_and_total_day_hours.text = f"Today's\nTotal Hours: {round(total_day_hours, 2)}"
        else:
            self.date_and_total_day_hours.text = f"{day.strftime('%m/%d/%y')}\nTotal Hours: {round(total_day_hours, 2)}"

        for rec in daily_records:
            item = OneLineListItem(text=f"       {rec[0]}     {rec[1]}     {rec[2]}")
            self.day_list.add_widget(item)
        if len(daily_records) >= 6:
            self.day_sv.do_scroll = True
            self.day_sv.scroll_to(item, animate=True)
        else:
            self.day_sv.do_scroll = False



    def period_totals(self, day):
        pass

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
            size_hint=(.3, .3)
        )
        self.add_widget(self.day_sv)
        self.day_list = MDList()
        self.day_sv.add_widget(self.day_list)

        # Setup the period totals
        self.period_sv = ScrollView(
            pos_hint={"center_x": .835, "top": .5},
            size_hint=(.3, .3)
        )
        self.add_widget(self.period_sv)
        self.period_list = MDList()
        self.period_sv.add_widget(self.period_list)

        self.current_day = datetime.today()
        self.change_day(0)
