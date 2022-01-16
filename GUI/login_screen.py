import employee_menu_screen

from my_import_statements import *

from static_widgets import StaticWidgets

class LoginScreen(StaticWidgets):
    quote_of_the_day = ObjectProperty(None)
    emp_id = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.display_quote_of_the_day()
        Clock.schedule_interval(lambda x: self.display_quote_of_the_day, 60 * 60 * 24)
        Clock.schedule_interval(self.keep_entry_focused, 2)
        Window.bind(on_key_down=self.enter)

    def keep_entry_focused(self, t):
        self.emp_id.focus = True
        self.emp_id.hint_text = "Enter Employee ID"

    def enter(self, instance, keyboard, keycode, text, modifiers):
        if self.emp_id.focus and keycode == 40 or keycode == 88:
            try:
                if self.emp_id.text != c.exec_sql(
                        "SELECT FieldValue from admin_information WHERE FieldProperty = 'AdminPassword';",
                        fetch_str="one")[0]:
                    if len(self.emp_id.text) != 0:
                        if self.emp_id.text[0] == "e":
                            entered_id = "E" + self.emp_id.text[1:]
                        elif self.emp_id.text[0] != "E":
                            entered_id = "E" + self.emp_id.text
                        else:
                            entered_id = self.emp_id.text
                    else:
                        entered_id = ""

                    emp_obj = Employee(entered_id, db_path)
                    employee_menu_screen.EmployeeMenuScreen.emp_obj = emp_obj
                    # del emp_obj

            except:
                self.emp_id.text = ""
                self.emp_id.hint_text = "Incorrect Password"
                return
            self.emp_id.text = ""
            self.change_screen("employee menu", "left")

    # @staticmethod
    # def go_to_employee_menu_screen():
    #     MDApp.get_running_app().sm.transition.direction = "left"
    #     MDApp.get_running_app().sm.current = "employee menu"

    def display_quote_of_the_day(self):
        with open("quotes.txt", "r", encoding="utf8") as f:
            list_of_quotes = f.readlines()
            rand_index = random.randint(0, len(list_of_quotes) - 1)
            new_str = []
            for index, word in enumerate(list_of_quotes[rand_index].split()):
                new_str.append(word)
                if len(new_str) == 15:
                    new_str[-1] += "\n"

            self.quote_of_the_day.text = " ".join(new_str)

