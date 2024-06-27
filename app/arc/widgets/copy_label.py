from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard

from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.behaviors import RectangularRippleBehavior

import re


class CopyLabel(RectangularRippleBehavior, Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_event_type("on_long_press")
        self.snackbar = MDSnackbar(
            MDSnackbarText(text="Скопировано", bold=True), duration=0.5, radius=[dp(8), dp(8), 0, 0]
        )

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if len(self.text) == 0:
                return True

            touch.grab(self)
            self._long_press_clock = Clock.schedule_once(self._on_long_press, 0.3)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)

            self.fade_out()

            if self._long_press_clock:
                self._long_press_clock.cancel()
                self._long_press_clock = None

            return True
        return super().on_touch_up(touch)

    def _on_long_press(self, dt):
        self.dispatch("on_long_press")
        self._long_press_clock = None

    def on_long_press(self, *args):
        self.copy()

    def copy(self):
        cleaned_text = re.sub(
            r"\[b\].*?\[/b\]|\[.*?\]|\d{2}:\d{2}:\d{2}\s+\d{2}.\d{2}.\d{4}",
            "",
            self.text,
        )
        cleaned_text = cleaned_text.strip()

        Clipboard.copy(cleaned_text)
        Window.parent.remove_widget(self.snackbar)
        self.snackbar.open()
