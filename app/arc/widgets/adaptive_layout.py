from kivy.metrics import dp
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout


class AdaptiveLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device = "desktop" if platform in ["win", "macosx", "linux"] else "mobile"

        self.on_window_size(Window)
        Window.bind(on_resize=self.on_window_size)

    def on_window_size(self, window, *args):
        if self.device == "desktop":

            if window.width > dp(600):
                self.size_hint_x = None
                self.width = dp(600)
                self.pos_hint = {"center_x": 0.5}
            else:
                self.size_hint_x = 1
