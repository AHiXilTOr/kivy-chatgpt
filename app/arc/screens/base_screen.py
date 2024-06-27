"""Base screen"""

import re
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.transition import MDSlideTransition, MDSharedAxisTransition


class Base(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.manager = None
        self.proxies = app.proxies
        self.api = app.api
        self.env = app.env

    def set_screen(self, screen_name, direction=None):
        screen_manager = self.manager
        if direction:
            screen_manager.transition = MDSlideTransition(direction=direction)
        else:
            screen_manager.transition = MDSharedAxisTransition()
        screen_manager.current = screen_name

    def validate_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email)

    def validate_username(self, username):
        pattern = r"^[a-zA-Z0-9_-]+$"
        return re.match(pattern, username)
