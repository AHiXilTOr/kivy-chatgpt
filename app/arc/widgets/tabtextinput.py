from kivy.utils import platform
from kivy.properties import ObjectProperty

from kivymd.uix.textfield import MDTextField


class TabTextInput(MDTextField):
    enter_action = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device = "desktop" if platform in ["win", "macosx", "linux"] else "mobile"
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key, key_str = keycode
        if key in (9, 13) and "shift" not in modifiers and self.device == "desktop":
            self.enter_action(self)
        else:
            super().keyboard_on_key_down(window, keycode, text, modifiers)
