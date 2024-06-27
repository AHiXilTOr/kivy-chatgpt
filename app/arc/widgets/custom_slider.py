from kivymd.uix.slider import MDSlider

class CustomSlider(MDSlider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = "50dp"
        self.hint_bg_color = "gray"
        self.hint_text_color = "white"
        self.show_off = False
        self.step_point_size = 0
