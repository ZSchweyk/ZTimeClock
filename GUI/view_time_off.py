from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_time_off.kv")

class ViewTimeOff(StaticWidgets):
    emp_obj: Employee = None
    period_label = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.back_button()
        self.period = 0

    def keyboard_btn(self, instance, keyboard, keycode, text, modifiers):
        # print(keycode)
        if keycode == 80:
            self.change_period(-1)
        elif keycode == 79:
            self.change_period(1)

    def change_period(self, increment):
        if self.period == 0 and increment == 1:
            return
        self.period += increment
        last_day_of_period = get_period_days_with_num(self.period)[0][1]
        self.period_label.text = last_day_of_period

        time_off = self.emp_obj.get_time_off(period=last_day_of_period, period_format="%m/%d/%Y")
        last_day_of_period = datetime.strptime(last_day_of_period, "%m/%d/%Y")
        total_accrued = self.emp_obj.get_vac_and_sick(last_day_of_period.strftime("01/01/%Y"), last_day_of_period.strftime("%m/%d/%Y"))

        self.table.row_data = [
            (
                "Vacation",
                time_off["Vacation"],
                round(total_accrued["VacAccrued"], 3),
                "",
                ""
            ),
            (
                "Sick",
                time_off["Sick"],
                round(total_accrued["SickAccrued"], 3),
                "",
                ""
            )
        ]


    def on_pre_enter(self, *args):
        self.table = MDDataTable(
            size_hint=(.55, .25),
            pos_hint={"center_x": .5, "top": .5},
            column_data=[
                          ("", dp(20)),
                          ("Period", dp(20)),
                          ("Total Accrued", dp(30)),
                          ("Total Taken", dp(30)),
                          ("Total Balance", dp(30))
            ]
        )
        self.period = 0
        self.change_period(0)
        self.add_widget(self.table)
        Window.bind(on_key_down=self.keyboard_btn)
