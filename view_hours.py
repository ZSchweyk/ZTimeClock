from my_import_statements import *
from static_widgets import StaticWidgets

Builder.load_file("view_hours.kv")


class ViewHours(StaticWidgets):
    def __init__(self, **kw):
        super().__init__(**kw)
