"""Help screen"""

import os
from arc.screens.base_screen import Base
from kivy.lang import Builder


Builder.load_file(os.path.join(os.path.dirname(__file__), "help_screen.kv"))


class HelpScreen(Base):
    pass
