from my_import_statements import *

Builder.load_file("static_widgets.kv")

class StaticWidgets(Screen):
    day_and_date_label = ObjectProperty(None)
    time_label = ObjectProperty(None)
    greeting_label = ObjectProperty(None)
    last_mouse_move: datetime = None

    def __init__(self, **kw):
        super().__init__(**kw)
        self.week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        Clock.schedule_interval(lambda x: self.update_clock(), 1)
        self.screen_clear = Clock.schedule_interval(lambda x: self.automatic_screen_clear(NUM_SECONDS_UNTIL_AUTOMATIC_LOG_OUT), .1)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window_obj, pos):
        self.last_mouse_move = datetime.now()

    def automatic_screen_clear(self, min_num_sec):
        if MDApp.get_running_app().sm.current != "login":
            # print(datetime.now().timestamp() - self.last_mouse_move.timestamp())
            if datetime.now().timestamp() - self.last_mouse_move.timestamp() >= min_num_sec:
                self.change_screen("login", "right")
        else:
            self.last_mouse_move = datetime.now()

    def update_clock(self):
        now = datetime.now()
        self.day_and_date_label.text = self.week_days[now.weekday()][:3] + " " + now.strftime("%m/%d/%Y")
        self.time_label.text = now.strftime("%I:%M:%S %p")

        if now.hour < 12:
            self.greeting_label.text = "Good Morning"
        elif now.hour < 17:
            self.greeting_label.text = "Good Afternoon"
        else:
            self.greeting_label.text = "Good Evening"

    def back_button(self, back_to_screen="employee menu", direction="right"):
        b = MDFillRoundFlatButton(text="Back",
                              pos_hint={"center_x": .05, "center_y": .05},
                              on_release=lambda x: self.change_screen(back_to_screen, direction),
                              text_color=(1, 0, 1, 1),
                              md_bg_color=(1,1,1,1),
                              font_size=30
                              )
        self.add_widget(b)

    def change_screen(self, back_to_screen, direction):
        MDApp.get_running_app().sm.transition.direction = direction
        MDApp.get_running_app().sm.current = back_to_screen

    @staticmethod
    def hide_widget(wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

