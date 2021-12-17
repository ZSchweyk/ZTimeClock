from my_import_statements import *

Builder.load_file("static_widgets.kv")

class StaticWidgets(Screen):
    day_and_date_label = ObjectProperty(None)
    time_label = ObjectProperty(None)
    greeting_label = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.update_clock("")
        Clock.schedule_interval(self.update_clock, 1)

    def update_clock(self, t):
        now = datetime.now()
        self.day_and_date_label.text = self.week_days[now.weekday()][:3] + " " + now.strftime("%m/%d/%Y")
        self.time_label.text = now.strftime("%I:%M:%S %p")
        if now.hour < 12:
            self.greeting_label.text = "Good Morning"
        elif now.hour < 17:
            self.greeting_label.text = "Good Afternoon"
        else:
            self.greeting_label.text = "Good Evening"

    def back_button(self, back_to_text="Return to Main Menu", back_to_screen="employee menu", direction="right"):
        b = MDRoundFlatButton(text=back_to_text,
                              pos_hint={"center_x": .5, "center_y": .1},
                              on_release=lambda x: self.change_screen(back_to_screen, direction),
                              text_color=(1, 0, 1, 1),
                              line_color=(1, 0, 1, 1)
                              )
        self.add_widget(b)

    def change_screen(self, back_to_screen, direction):
        MDApp.get_running_app().sm.transition.direction = direction
        MDApp.get_running_app().sm.current = back_to_screen

