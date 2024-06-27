from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.uix.image import Image

def canvas_rectangle(box, color='#212123', radius=[(0, 0), (0, 0), (0, 0), (0, 0)], source=None):
    if not source:
        color = get_color_from_hex(color)
        
        with box.canvas.before:
            Color(*color)
            box.rect = RoundedRectangle(size=box.size, pos=box.pos, radius=radius)

        def update_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        box.bind(pos=update_rect, size=update_rect)
    else:
        image = Image(source=source)
        box.add_widget(image)
    