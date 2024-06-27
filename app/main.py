"""Launching the application"""

__version__ = "1.0.0"

import os
import kivy
from kivy.core.window import Window

Window.set_icon(os.path.join(os.path.dirname(__file__), "arc/img", "ico.png"))
Window.set_title("Kynvi: Загрузка...")
Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
Window.softinput_mode = "below_target"
kivy.require("2.3.0")

from arc.kynvi import Kynvi
from arc.overmain import OverMain
from arc.screens import *
from arc.widgets.adaptive_layout import AdaptiveLayout
from arc.widgets.boxstencil import BoxStencil
from arc.widgets.copy_label import CopyLabel
from arc.widgets.custom_slider import CustomSlider
from arc.widgets.smartrv import SmartRV
from arc.widgets.tabtextinput import TabTextInput
from kivy.app import runTouchApp
from kivy.utils import platform
import asyncio
import kivymd.icon_definitions
import kivymd.uix.snackbar
import traceback

# from jnius import autoclass

api = "https://kivy-chatgpt.onrender.com"
proxies = None


def main():
    try:
        if platform in ["win", "macosx", "linux"]:
            os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"
            env = os.path.join(os.path.expanduser("~"), ".kynvi")
            if not os.path.exists(env):
                os.makedirs(env)

            if platform == "win":
                http = os.environ.get("HTTP_PROXY")
                https = os.environ.get("HTTPS_PROXY")

                if not proxies:
                    if http:
                        proxies["http"] = http
                    if https:
                        proxies["https"] = https
        else:
            # from android.permissions import request_permissions, Permission
            from android.storage import app_storage_path

            # request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

            # Environment = autoclass("android.os.Environment")
            # env = Environment.getExternalStorageDirectory().getAbsolutePath()
            env = app_storage_path()

        asyncio.run(Kynvi(env, api, proxies).async_run())
    except Exception:
        error_message = traceback.format_exc()
        runTouchApp(OverMain(error_message, api, proxies))


if __name__ == "__main__":
    main()
