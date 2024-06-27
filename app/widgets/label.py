from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.core.clipboard import Clipboard
from kivy.uix.behaviors import TouchRippleBehavior
from kivy.clock import Clock

from kivymd.uix.snackbar import Snackbar

class MyLabel(TouchRippleBehavior, Label):
    padding = (dp(10), dp(10))
    long_press_duration = 0.4

    def __init__(self, widget=None, bg=True, anim=True, **kwargs):
        super().__init__(**kwargs)
        self._touch_count = 0
        self.bg = bg
        self.anim = anim
        self.ripple_fade_from_alpha = 0
        self.ripple_fade_to_alpha = .2

        self.size_hint = (None, None)
        
        if self.bg:
            with self.canvas.before:
                Color(*get_color_from_hex('#212123'))
                self.background_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect, text=self.update_rect)

        if widget:
            widget.bind(size=self.update_text_size)

        self.register_event_type('on_long_press')

    def update_rect(self, instance, value):
        if self.bg:
            self.background_rect.pos = instance.pos
            self.background_rect.size = instance.size
        self.update_texture()
    
    def update_text_size(self, instance, value):
        self.text_size[0] = instance.size[0]
        self.update_texture()

    def update_texture(self):
        self.texture_update()
        self.size = self.texture_size

    def on_touch_down(self, touch):
        if self.anim:
            if self.disabled:
                return False

            if self.collide_point(*touch.pos):
                touch.grab(self)
                self.ripple_show(touch)
                
                self._touch_count += 1
                self._long_press_clock = Clock.schedule_once(self._on_long_press, self.long_press_duration)

            return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if touch.grab_current is self and self.anim:
            touch.ungrab(self)

            self.ripple_fade()

            if self._long_press_clock:
                self._long_press_clock.cancel()
                self._long_press_clock = None

            return True
        return super().on_touch_up(touch)
    
    def _on_long_press(self, dt):
        self.dispatch('on_long_press')
        self._long_press_clock = None

    def on_long_press(self, *args):
        Clipboard.copy(self.text)
        Clock.schedule_once(self.open_snackbar, 0)

    def open_snackbar(self, *args):
        snackbar = Snackbar(
            text="Скопировано",
            font_size=sp(16),
            height=dp(50)
        )
        snackbar.bind(on_press=self.snackbar_dismissed)
        snackbar.open()
    
    def snackbar_dismissed(self, instance, *args):
        instance.dismiss()



