"""Setting screen"""

import os
from arc.screens.base_screen import Base
from arc.utils.config import save_config
from kivy import __version__ as __versionkv__
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.utils import hex_colormap
from kivymd import __version__ as __versionkvmd__
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.utils.fpsmonitor import FpsMonitor
from main import __version__
from materialyoucolor.utils.platform_utils import SCHEMES
from sys import version


Builder.load_file(os.path.join(os.path.dirname(__file__), "setting_screen.kv"))


class Info(ModalView):
    pass


class SettingScreen(Base):
    def scheme(self, menu_button):
        menu_items = []

        for name_color, hex_value in hex_colormap.items():
            name_palette = name_color.capitalize()
            on_release_func = lambda x=name_palette: self.switch_palette(x)
            inverted_text_color = self.invert_color(hex_value)
            menu_items.append(
                {
                    "text": name_palette,
                    "on_release": on_release_func,
                    "md_bg_color": hex_value,
                    "outline_width": 10,
                    "text_color": inverted_text_color,
                }
            )

        MDDropdownMenu(caller=menu_button, items=menu_items).open()

    def invert_color(self, hex_color):
        hex_color = hex_color.lstrip("#")
        rgb_color = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        brightness = (
            0.299 * rgb_color[0] + 0.587 * rgb_color[1] + 0.114 * rgb_color[2]
        ) / 255
        return "#000000" if brightness > 0.5 else "#FFFFFF"

    def switch_palette(self, selected_palette):
        self.theme_cls.primary_palette = selected_palette
        save_config("settings", "scheme", selected_palette, self.env)

    def scheme_type(self, menu_button):
        menu_items = []

        for scheme_name in SCHEMES.keys():
            menu_items.append(
                {
                    "text": scheme_name,
                    "on_release": lambda x=scheme_name: self.update_scheme_name(x),
                }
            )

        MDDropdownMenu(caller=menu_button, items=menu_items).open()

    def update_scheme_name(self, scheme_name):
        self.theme_cls.dynamic_scheme_name = scheme_name
        save_config("settings", "scheme_type", scheme_name, self.env)

    def change_theme(self, instance, value):
        print(self.rgb_to_hex(*value[:3]))

    def rgb_to_hex(self, r, g, b):
        return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

    def fps(self, value):
        if value:
            self.monitor = FpsMonitor(anchor="top")
            self.monitor.start()
            Window.add_widget(self.monitor)
        else:
            Window.remove_widget(self.monitor)

    def dark(self, value):
        style = "Dark" if value else "Light"
        self.theme_cls.theme_style = style
        save_config("settings", "dark", style, self.env)

    def stream(self, value):
        MDApp.get_running_app().stream = value
        save_config("settings", "stream", str(value), self.env)

    def mean(self, value):
        MDApp.get_running_app().mean = value
        save_config("settings", "meaning", str(value), self.env)

    def hide(self, value):
        MDApp.get_running_app().hide = value
        save_config("settings", "hide", str(value), self.env)

    def temperature(self, value):
        MDApp.get_running_app().temperature = value
        save_config("settings", "temperature", str(value), self.env)

    def environment(self):
        info = f"Версия приложения: {__version__}\n"
        info += f"{__versionkv__}, {__versionkvmd__}, {version}"

        view = Info()
        view.ids.info.text = f"{info}\n"
        view.open()
