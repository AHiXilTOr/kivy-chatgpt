from kivy.animation import Animation
from kivy.uix.recycleview import RecycleView
from kivy.properties import OptionProperty, NumericProperty


class SmartRV(RecycleView):
    orientation = OptionProperty("vertical", options=["vertical", "horizontal"])

    children_height = NumericProperty()
    children_width = NumericProperty()

    vertical_behavior = OptionProperty(
        "scroll_to_top",
        options=["scroll_to_top", "scroll_to_center", "scroll_to_bottom"],
    )
    horizontal_behavior = OptionProperty(
        "scroll_to_left",
        options=["scroll_to_left", "scroll_to_center", "scroll_to_right"],
    )

    def scroll_to_item(self, index):
        if not self.data:
            return

        if self.orientation == "vertical":
            N = len(self.data)

            h = self.children_height
            H = self.height

            if self.vertical_behavior == "scroll_to_top":
                scroll_y = 1 - (index * h) / (N * h - H)
            elif self.vertical_behavior == "scroll_to_center":
                scroll_y = 1 - (index * h - H / 2 + h / 2) / (N * h - H)
            elif self.vertical_behavior == "scroll_to_bottom":
                scroll_y = 1 - (index * h - H + h) / (N * h - H)

            Animation(scroll_y=scroll_y, t="linear", d=0.5).start(self)

        elif self.orientation == "horizontal":
            N = len(self.data)

            w = self.children_width
            W = self.width

            if self.horizontal_behavior == "scroll_to_left":
                scroll_x = (index * w) / (N * w - W)

            elif self.horizontal_behavior == "scroll_to_center":
                scroll_x = (index * w - W / 2 + 1 / 2 * w) / (N * w - W)

            elif self.horizontal_behavior == "scroll_to_right":
                scroll_x = (index * w - W + w) / (N * w - W)

            Animation(scroll_x=scroll_x, t="linear", d=0.5).start(self)

    def scroll_to_last_item(self):
        Animation.cancel_all(self, "scroll_y")
        if self.height < self.layout_manager.height:
            last_index = len(self.data) - 1
            self.scroll_to_item(last_index)
