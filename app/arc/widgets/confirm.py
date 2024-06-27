from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, ObjectProperty, NumericProperty


Builder.load_string('''
<Confirm>:
    size_hint: None, None
    size: "200dp", confirm_content.height
    opacity: 0

    MDBoxLayout:
        id: confirm_content
        orientation: "vertical"
        padding: "20dp"
        spacing: "10dp"
        md_bg_color: app.theme_cls.backgroundColor
        adaptive_height: True

        MDLabel:
            text: root.text
            adaptive_height: True

        BoxLayout:
            size_hint_y: None
            height: self.minimum_height
            spacing: "10dp"
            orientation: "horizontal"

            MDButton:   
                on_release: root.no()
            
                MDButtonText:
                    text: "Нет"

            MDButton:   
                on_release: root.yes()
            
                MDButtonText:
                    text: "Да"
''')

class Confirm(ModalView):
    yes = ObjectProperty()
    no = ObjectProperty()
    text = StringProperty("Уверены?")
    duration = NumericProperty(0.3)

    def open(self, *largs):
        anim = Animation(opacity=1, duration=self.duration)
        anim.start(self)
        super().open(*largs)
