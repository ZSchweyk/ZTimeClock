from my_import_statements import *

class BackButton(Screen):
    def back_button(self, back_to_text="Return to Main Menu", back_to_screen="employee menu"):
        MDFlatButton(text=back_to_text, halign="center", pos_hint={"center_y": .1}, on_release=lambda: self.change_screen(back_to_screen))

    def change_screen(self, back_to_screen):
        MDApp.get_running_app().sm.current = back_to_screen