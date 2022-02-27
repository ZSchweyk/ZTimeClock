import time

from my_import_statements import *
from static_widgets import StaticWidgets
import clock_in_or_out
import view_hours
import request_vacation
import view_time_off

Builder.load_file("employee_menu_screen.kv")


class EmployeeMenuScreen(StaticWidgets):
    emp_obj: Employee = None
    name_label = ObjectProperty(None)

    # clock_in_or_out_button = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_leave(self, *args):
        self.clear_widgets(self.button_array)

    def on_pre_enter(self, *args):
        self.name_label.text = self.emp_obj.first + " " + self.emp_obj.last

        if self.emp_obj.get_type() == "Hourly FT":
            # Show all buttons
            clock_in_or_out_button = MDRoundFlatButton(
                pos_hint={"center_x": .5, "center_y": .6},
                font_size=30,
                on_release=lambda x: self.clock_in_or_out()
            )
            clock_in_or_out_button.text = "Clock Out" if self.emp_obj.get_status() else "Clock In"
            self.add_widget(clock_in_or_out_button)

            view_hours_button = MDRoundFlatButton(
                text="View Hours",
                pos_hint={"center_x": .5, "center_y": .5},
                font_size=30,
                on_release=lambda x: self.view_hours()
            )
            self.add_widget(view_hours_button)

            view_time_off_button = MDRoundFlatButton(
                text="View Time Off",
                pos_hint={"center_x": .5, "center_y": .4},
                font_size=30,
                on_release=lambda x: self.view_time_off()
            )
            self.add_widget(view_time_off_button)

            request_vacation_button = MDRoundFlatButton(
                text="Request Vacation",
                pos_hint={"center_x": .5, "center_y": .3},
                font_size=30,
                on_release=lambda x: self.request_vacation()
            )
            self.add_widget(request_vacation_button)

            self.button_array = [
                clock_in_or_out_button,
                view_hours_button,
                view_time_off_button,
                request_vacation_button
            ]
        elif self.emp_obj.get_type() == "Hourly PT":
            # Show "Clock In/Out" and "View Hours"
            clock_in_or_out_button = MDRoundFlatButton(
                pos_hint={"center_x": .5, "center_y": .6},
                font_size=30,
                on_release=lambda x: self.clock_in_or_out()
            )
            clock_in_or_out_button.text = "Clock Out" if self.emp_obj.get_status() else "Clock In"
            self.add_widget(clock_in_or_out_button)

            view_hours_button = MDRoundFlatButton(
                text="View Hours",
                pos_hint={"center_x": .5, "center_y": .5},
                font_size=30,
                on_release=lambda x: self.view_hours()
            )
            self.add_widget(view_hours_button)

            self.button_array = [
                clock_in_or_out_button,
                view_hours_button
            ]
        else:
            # Show "View Time Off" and "Request Vacation"
            view_time_off_button = MDRoundFlatButton(
                text="View Time Off",
                pos_hint={"center_x": .5, "center_y": .6},
                font_size=30,
                on_release=lambda x: self.view_time_off()
            )
            self.add_widget(view_time_off_button)

            request_vacation_button = MDRoundFlatButton(
                text="Request Vacation",
                pos_hint={"center_x": .5, "center_y": .5},
                font_size=30,
                on_release=lambda x: self.request_vacation()
            )
            self.add_widget(request_vacation_button)

            self.button_array = [
                view_time_off_button,
                request_vacation_button
            ]

        self.back_button(back_to_screen="login", direction="right")

    def clock_in_or_out(self):
        self.emp_obj.min_wait_time = MIN_WAIT_TIME_IN_SECONDS_BEFORE_BEING_ABLE_TO_CLOCK_IN_AGAIN

        if not self.emp_obj.get_status() and not self.emp_obj.can_clock_in(min_wait_seconds=self.emp_obj.min_wait_time):
            dialog = MDDialog(
                text=" " * 15 + f"Must wait at least {self.emp_obj.min_wait_time / 60} minutes before clocking in again.",
                radius=[20, 7, 20, 7]
            )
            dialog.open()
        else:
            clock_in_or_out.ClockInOrOut.emp_obj = self.emp_obj
            self.change_screen("clock in or out", "left")

    def view_hours(self):
        view_hours.ViewHours.emp_obj = self.emp_obj
        self.change_screen("view hours", "left")

    def view_time_off(self):
        view_time_off.ViewTimeOff.emp_obj = self.emp_obj
        self.change_screen("view time off", "left")

    def request_vacation(self):
        request_vacation.RequestVacation.emp_obj = self.emp_obj
        self.change_screen("request vacation", "left")
