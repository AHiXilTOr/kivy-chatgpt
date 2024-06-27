import os
from arc.utils.config import read_config, save_config
from cryptography.fernet import Fernet
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationItem
from kivymd.uix.transition import MDSlideTransition

# from kivy.core.text import LabelBase, DEFAULT_FONT
# LabelBase.register(DEFAULT_FONT, fn_regular=os.path.join(os.path.dirname(__file__), "font/arial-unicode-ms.ttf"), fn_bold="data/fonts/Roboto-Bold.ttf")


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    screen = StringProperty()
    direction = StringProperty()


class Kynvi(MDApp):
    username = StringProperty()
    email = StringProperty()
    balance = NumericProperty()

    def __init__(self, env, api, proxies, **kwargs):
        self.env = env
        self.proxies = proxies
        self.api = api
        self.dark = read_config("settings", "dark", "Dark", env)
        self.scheme = read_config("settings", "scheme", "Blue", env)
        self.scheme_type = read_config("settings", "scheme_type", "TONAL_SPOT", env)
        self.provider = read_config("settings", "provider", "Авто", env)
        self.model = read_config("settings", "model", "", env)
        self.system = read_config("settings", "system", "", env)
        self.stream = read_config("settings", "stream", "True", env).lower() == "true"
        self.mean = read_config("settings", "meaning", "True", env).lower() == "true"
        self.temperature = float(read_config("settings", "temperature", "50.0", env))

        sha_key = read_config("settings", "sha", "", env)
        if not sha_key:
            sha_key = Fernet.generate_key().decode("utf-8")
            save_config("settings", "sha", sha_key, env)
        self.sha = Fernet(sha_key.encode("utf-8"))

        super().__init__(**kwargs)
        self.theme_cls.theme_style = self.dark
        self.theme_cls.primary_palette = self.scheme
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.1

    def build(self):
        return Builder.load_file(os.path.join(os.path.dirname(__file__), "main.kv"))

    def on_switch_tabs(self, bar, item, item_icon, empty):
        sm = self.root.ids.screen_manager
        sm.transition = MDSlideTransition()
        sm.transition.direction = item.direction
        sm.current = item.screen
        return True

    def on_stop(self):
        if hasattr(self.root.ids, "main_screen") and hasattr(
            self.root.ids.main_screen, "save_data"
        ):
            self.root.ids.main_screen.save_data()
