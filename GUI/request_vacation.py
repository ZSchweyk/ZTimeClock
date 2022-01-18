from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("request_vacation.kv")

# class MyTextInput(MDTextField):
#     def on_parent(self, widget, parent):
#         self.focus = True



class RequestVacation(StaticWidgets):
    emp_obj: Employee = None
    confirmation_label = ObjectProperty(None)
    send_request_btn = ObjectProperty(None)
    cancel_request_btn = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.back_button()

    @staticmethod
    def hide_widget(wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True


    def open_calendar(self):
        today = datetime.today()
        date_picker = MDDatePicker(year=today.year,
                     month=today.month,
                     mode="range",
                     # min_date=date.today()
        )
        date_picker.bind(on_save=self.on_save)
        date_picker.open()

    def on_save(self, instance, value, date_range):
        if len(date_range) == 0:
            return
        self.date_range = date_range
        start = self.date_range[0].strftime("%m/%d/%Y")
        end = self.date_range[-1].strftime("%m/%d/%Y")
        self.duration = (self.date_range[-1] - self.date_range[0]).days + 1
        self.num_weekdays = sum([single_date.weekday() <= 4 for single_date in self.date_range])
        self.confirmation_label.text = f"Your request for {self.duration} total days ({self.num_weekdays} weekdays) of vacation,\n" \
                                       f"from {start} - {end},\n" \
                                       f"is about to be sent to management for approval."
        self.hide_widget(self.send_request_btn, dohide=False)
        self.hide_widget(self.cancel_request_btn, dohide=False)
        # send or cancel
        # Request sent. A reply will be sent to your email in 1 week.
        # Send that request with the emp's email, and to reply within 1 week.

    def send_request(self):
        now = datetime.now()

        body = f"""Hello Nader,

A vacation request has been made by {self.emp_obj.first} {self.emp_obj.last} on {now.strftime("%m/%d/%Y")} at {now.strftime("%I:%M %p")}.

Date Range: {self.date_range[0].strftime("%m/%d/%Y")} - {self.date_range[-1].strftime("%m/%d/%Y")}
Duration: {self.duration}
Number of Weekdays: {self.num_weekdays}

Please respond to {self.emp_obj.email} within 1 week.

Sincerely,
ZTimeClock


"""
        send_email_with_db_attachment("ChemtrolAlerts@gmail.com", "", "zschweyk@gmail.com", body, f"Vacation Request from {self.emp_obj.first} {self.emp_obj.last} on {now.strftime('%m/%d/%Y')} at {now.strftime('%I:%M %p')}", "")
        dialog = MDDialog(
            text=f"Request sent. A reply will be emailed to you within one week.",
            radius=[20, 7, 20, 7],
        )
        dialog.open()
        self.change_screen("employee menu", "right")

    def cancel_request(self):
        self.confirmation_label.text = ""
        self.hide_widget(self.send_request_btn)
        self.hide_widget(self.cancel_request_btn)


    def on_pre_enter(self, *args):
        self.confirmation_label.text = ""
        self.hide_widget(self.send_request_btn)
        self.hide_widget(self.cancel_request_btn)



