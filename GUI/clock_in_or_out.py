from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("clock_in_or_out.kv")


class OneLineListItemAligned(OneLineListItem):
    def __init__(self, halign, **kwargs):
        super(OneLineListItemAligned, self).__init__(**kwargs)
        self.ids._lbl_primary.halign = halign


class ClockInOrOut(StaticWidgets):
    emp_obj: Employee = None

    def __init__(self, **kw):
        super().__init__(**kw)

    def show_day_totals(self, day):
        daily_records, total_day_hours = \
            self.emp_obj.get_records_and_hours_for_day(day.strftime("%m/%d/%y"), "%m/%d/%y")
        self.date_and_total_day_hours.text = f"Today's\nTotal Hours: {round(total_day_hours, 2)}"

        self.widgets = []
        self.widgets.append([self.sv])
        self.ml = MDList()
        self.sv.add_widget(self.ml)
        item = None
        for rec in daily_records:
            item = OneLineListItem(text=f"       {rec[0]}     {rec[1]}     {rec[2]}")
            self.ml.add_widget(item)
        if len(daily_records) >= 6:
            self.sv.do_scroll = True
            self.sv.scroll_to(item, animate=True)
        else:
            self.sv.do_scroll = False

    def on_leave(self, *args):
        Thread(target=self.z_clear_widgets())

    def z_clear_widgets(self):
        try:
            self.clear_widgets([
                self.sv,
                self.ml,
                self.date_and_total_day_hours,
                self.name_and_status,
                self.time_in,
                self.time_out,
                self.duration
            ])

        except:
            self.clear_widgets([
                self.pick_time_text_box,
                self.instructions
            ])
        self.clear_widgets([self.name_and_status])

    def show_period_totals(self):
        pass

    def on_pre_enter(self, *args):
        self.name_and_status = Label(
            pos_hint={"center_y": .7},
            halign="center",
            font_size=30
        )
        self.add_widget(self.name_and_status)

        self.back_button()

        # self.emp_obj.min_wait_time = 10 * 60 by default. clock_in_or_out automatically checks if the duration
        # between clock out and clock in is >= self.emp_obj.min_wait_time. To change it, set it in
        # employee_menu_screen.py in the clock_in_or_out method.

        # Reasons why this would be False:
        #   1. They try to clock in before self.emp_obj.min_wait_time has passed
        #   2. They try to clock out on a different day than their previous clock in
        #
        # The test in the clock_in_or_out method in the employee_menu_screen will make sure that #1 passes
        if self.emp_obj.clock_in_or_out():

            self.sv = ScrollView(
                pos_hint={"center_x": .5, "top": .4},
                size_hint=(.3, .3),
            )
            self.add_widget(self.sv)

            self.date_and_total_day_hours = Label(
                pos_hint={"center_y": .55},
                halign="center",
                font_size=27
            )
            self.add_widget(self.date_and_total_day_hours)

            self.time_in = Label(
                pos_hint={"center_x": .42, "center_y": .43},
                halign="center",
                text="In\n----------------------"
            )
            self.add_widget(self.time_in)

            self.time_out = Label(
                pos_hint={"center_x": .505, "center_y": .43},
                halign="center",
                text="Out\n----------------------"
            )
            self.add_widget(self.time_out)

            self.duration = Label(
                pos_hint={"center_x": .58025, "center_y": .43},
                halign="center",
                text="Duration\n---------------"
            )
            self.add_widget(self.duration)

            self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last + \
                                        f"\nYou're clocked {'IN' if self.emp_obj.get_status() else 'OUT'}"
            Thread(target=lambda: self.show_day_totals(datetime.today())).start()
        else:
            # self.z_clear_widgets()
            # self.clear_widgets([self.date_and_total_day_hours, self.time_in, self.time_out, self.duration])
            self.name_and_status.text = self.emp_obj.first + " " + self.emp_obj.last
            last_entry = datetime.strptime(self.emp_obj.get_last_entry(), "%Y-%m-%d %H:%M:%S")
            week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            self.instructions = Label(
                text=f"On your last workday, {week_days[last_entry.weekday()]} {last_entry.strftime('%m/%d/%y')}, "
                     f"you clocked in at {last_entry.strftime('%I:%M:%S %p')} and forgot to clock out.\n"
                     "Please enter the time you left work on that day.",
                pos_hint={"center_y": .6},
                halign="center"
            )
            self.add_widget(self.instructions)

            self.pick_time_text_box = MDTextField(
                hint_text="HH:MM am/pm",
                font_size=25,
                pos_hint={"center_y": .5, "center_x": .5},
                size_hint=(.15, .085)
            )
            Clock.schedule_interval(lambda x: setattr(self.pick_time_text_box, "focus", True), .01)
            self.add_widget(self.pick_time_text_box)

            b = MDFillRoundFlatButton(text="Submit",
                                      pos_hint={"center_x": .5, "center_y": .4},
                                      on_release=lambda btn: self.enter_request(self.pick_time_text_box.text, "%I:%M %p"),
                                      text_color=(1, 0, 1, 1),
                                      md_bg_color=(1, 1, 1, 1),
                                      font_size=30
                                      )
            self.add_widget(b)

            return

    def enter_request(self, timestamp, format):
        if validate_timestamp(timestamp, format):
            clock_in = datetime.strptime(self.emp_obj.get_last_entry(), "%Y-%m-%d %H:%M:%S")
            clock_out = datetime.strptime(timestamp, format)

            if clock_out.time() > clock_in.time():
                formatted_clock_out_time = clock_out.strftime("%I:%M:%S %p")
                self.emp_obj.manually_clock_out(formatted_clock_out_time)

                dialog = MDDialog(
                    text="Thank You. " +
                        f"Your timestamp request of \"{timestamp}\" has been sent to management for approval. " +
                        "Be sure to clock in again for today, if you're starting your shift.",
                    radius=[20, 7, 20, 7]
                )
                send_back_to_menu = True
            else:
                dialog = MDDialog(
                    text="Error. Please type in a time greater than when you clocked in.",
                    radius=[20, 7, 20, 7]
                )
                send_back_to_menu = False
        else:
            dialog = MDDialog(
                text="Wrong Time Format. Enter timestamp in the format of \"HH:MM am/pm\"",
                radius=[20, 7, 20, 7],
                # buttons=[
                #     MDFlatButton(
                #         text="OKAY",
                #     )
                # ]
            )
            send_back_to_menu = False

        dialog.open()
        if send_back_to_menu:
            self.change_screen("employee menu", "right")
        return

