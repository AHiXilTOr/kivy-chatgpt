from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, RoundedRectangle, Rectangle
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty

class PickSwitch(Widget):
    active = ObjectProperty()

    def __init__(self, active=False, func=None, bg=True, **kwargs):
        super().__init__(**kwargs)
        self.active = str(active).lower() == 'true'
        self.func = func
        self.size_hint = (None, 1)
        self.width = dp(50)
        self.bg = bg
        
        with self.canvas:
            self.bg_color = Color(0.2, 0.2, 0.2)
            self.bg_rect = RoundedRectangle(pos=(self.center_x - self.width/2, self.center_y - dp(9.5)), 
                                            size=(self.width, dp(19)), 
                                            source='', 
                                            radius=[(dp(10), dp(10)), (dp(10), dp(10)), (dp(10), dp(10)), (dp(10), dp(10))])
            self.knob_color = Color(.9, .9, .9)
            self.knob_ellipse = Ellipse(pos=(self.center_x - dp(6.25), self.center_y - dp(6.25)), size=(dp(12.5), dp(12.5)))
        
        if self.bg:
            with self.canvas.before:
                Color(*get_color_from_hex('#212123'))
                self.background_rect = Rectangle(pos=(self.x - dp(5), self.y), size=(self.width + dp(10), self.height))

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):

        if self.active:
            self.bg_color.rgba = (0.2, 0.7, 0.2, 1)
            knob_x = (self.center_x + self.knob_ellipse.size[0]) - dp(3)
        else:
            self.bg_color.rgba = (0.7, 0.2, 0.2, 1)
            knob_x = (self.center_x - self.knob_ellipse.size[0] * 2) + dp(3)
        
        
        self.bg_rect.pos = (self.center_x - self.width / 2, self.center_y - dp(9.5))
        self.knob_ellipse.pos = (knob_x, self.center_y - self.knob_ellipse.size[1] / 2)

        if self.func:
            self.func(self.active)

        if self.bg:
            self.background_rect.pos = (self.x - dp(5), self.y)
            self.background_rect.size = (self.width + dp(10), self.height)

    def movement(self, value):
        if value:
            self.bg_color.rgba = (0.2, 0.7, 0.2, 1)
            knob_x = (self.center_x + self.knob_ellipse.size[0]) - dp(3)
        else:
            self.bg_color.rgba = (0.7, 0.2, 0.2, 1)
            knob_x = (self.center_x - self.knob_ellipse.size[0] * 2) + dp(3)
            
        animation = Animation(pos=(knob_x, self.center_y - self.knob_ellipse.size[1] / 2), duration=0.2)
        animation.start(self.knob_ellipse)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.func:
                self.func(not self.active)
            self.movement(not self.active)
            self.active = not self.active
