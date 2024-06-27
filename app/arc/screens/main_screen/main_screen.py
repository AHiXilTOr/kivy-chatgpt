"""Main screen"""

from typing import Dict, Any
from uuid import uuid4
import os
import random
import string
from arc.screens.base_screen import Base
from arc.utils.config import save_config
from arc.widgets.confirm import Confirm
from asyncio import ensure_future, CancelledError, sleep, create_task, Future
from datetime import datetime
from functools import partial
from httpx import AsyncClient
from json import load, dump, dumps, JSONDecodeError
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ListProperty, DictProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText


Builder.load_file(os.path.join(os.path.dirname(__file__), "main_screen.kv"))


class RenameChat(ModalView):
    def open(self, *largs):
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self)
        super().open(*largs)


class SelectableRecycleBoxLayout(
    FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    pass


class ModelLayout(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def on_parent(self, widget, parent):
        if parent:
            self.main = self.get_main()

    def get_main(self):
        parent = self.parent
        while parent:
            if isinstance(parent, MainScreen):
                return parent
            parent = parent.parent
        return None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            self.main.active_model = self.text
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected


class ProviderLayout(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def on_parent(self, widget, parent):
        if parent:
            self.main = self.get_main()

    def get_main(self):
        parent = self.parent
        while parent:
            if isinstance(parent, MainScreen):
                return parent
            parent = parent.parent
        return None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            self.main.active_provider = self.text
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected


class MessageLayout(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()
    time = StringProperty()
    sender = StringProperty()
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def on_parent(self, widget, parent):
        if parent:
            self.main = self.get_main()

    def get_main(self):
        parent = self.parent
        while parent:
            if isinstance(parent, MainScreen):
                return parent
            parent = parent.parent
        return None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if touch.is_double_tap and self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
        return super().on_touch_down(touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected


class ChatLayout(RecycleDataViewBehavior, MDBoxLayout):
    uuid = StringProperty()
    name = StringProperty()
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = MDDropdownMenu(
            show_duration=0.3,
            hide_duration=0.1,
            show_transition="out_elastic",
            ver_growth="down",
            hor_growth="left",
            items=[],
        )

    def on_parent(self, widget, parent):
        if parent:
            self.main = self.get_main()

    def get_main(self):
        parent = self.parent
        while parent:
            if isinstance(parent, MainScreen):
                return parent
            parent = parent.parent
        return None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.ids.chat.collide_point(*touch.pos) and self.selectable:
            Clock.schedule_once(
                lambda dt: self.main.switch_chat({"uuid": self.uuid, "name": self.name})
            )
            return self.parent.select_with_touch(self.index, touch)
        elif self.ids.chat_button.collide_point(*touch.pos) and self.selectable:
            self.open_menu()

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

    def open_menu(self):
        self.menu.caller = self.ids.chat_button
        self.menu.items = [
            {
                "text": f'Удалить "{self.name}"',
                "on_release": lambda text=f'"{self.name}" удалён': self.delete_chat(
                    self.index, text
                ),
                "ripple_effect": False,
            },
            {
                "text": "Переименовать",
                "on_release": lambda: self.rename_chat(self.index),
                "ripple_effect": False,
            },
        ]
        self.menu.open()

    def rename_chat(self, index):
        self.menu.dismiss()
        Clock.schedule_once(lambda dt: self.main.rename_chat(index))

    def delete_chat(self, index, text):
        rv = self.parent.parent
        del rv.data[index]
        del self.main.chats[index]
        length = len(rv.data)
        if rv.data:
            if length < 6:
                rv.scroll_y = 1
            if length <= index:
                index = length - 1
            uuid, name = rv.data[index]["uuid"], rv.data[index]["name"]
            self.main.switch_chat({"uuid": uuid, "name": name})
            rv.layout_manager.selected_nodes = [index]
        else:
            self.main.new_chat()
        self.menu.dismiss()
        MDSnackbar(
            MDSnackbarSupportingText(text=text, bold=True),
            duration=0.5,
            radius=[dp(8), dp(8), 0, 0],
        ).open()


class MainScreen(Base):
    active_chat = DictProperty()
    chats = ListProperty()
    messages = DictProperty()
    active_messages = ListProperty()
    models = ListProperty()
    providers = ListProperty()
    active_model = StringProperty()
    active_provider = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init = False
        self.chatbot_task = Future()
        self.chatbot_task.set_result(None)
        self.bind(active_chat=self.switch_active_messages)
        self.bind(active_messages=self.save_messages)
        self.bind(active_model=self.save_model)
        self.bind(active_provider=self.save_provider)

    def on_enter(self):
        if not self.init:
            ensure_future(self.init_data())
            self.init = True

    def switch_active_messages(self, *args):
        self.active_messages = self.messages[self.active_chat.get("uuid")]
        if self.active_messages:
            self.hide_help_text()
        else:
            self.show_help_text()

    def save_messages(self, *args):
        self.messages[self.active_chat.get("uuid")] = self.active_messages
        self.save_data()

    def save_model(self, *args):
        save_config("settings", "model", self.active_model, self.env)

    def save_provider(self, *args):
        save_config("settings", "provider", self.active_provider, self.env)
        ensure_future(self.fetch_models())

    def add_message(self, text, entry=True, key="text", bot=True):
        if bot and self.chatbot_task.done():
            return
        if entry:
            now = datetime.now()
            self.active_messages.append(
                {
                    "sender": "Бот" if bot else "Вы",
                    "text": text.strip(),
                    "time": f'{now.strftime("%H:%M:%S")}  {now.strftime("%d.%m.%Y")}',
                }
            )
            self.scroll_y(self.ids.message_list, 0)
        else:
            self.active_messages[-1][key] += text
            self.scroll_y(self.ids.message_list, 0)
            self.ids.message_list.refresh_from_data()
        self.hide_help_text()

    async def init_data(self):
        app = MDApp.get_running_app()
        self.active_provider = app.provider
        self.active_model = app.model
        self.ids.system_prompt.text = app.system
        data = await self.load_data()
        self.messages, self.chats, self.active_chat = data
        await self.fetch_providers()
        await self.load_messages()
        await self.load_chats()

    async def load_messages(self):
        if self.active_chat:
            self.switch_chat(self.active_chat)
        else:
            self.new_chat()

    async def load_chats(self):
        selected_index = next(
            (
                index
                for index, chat in enumerate(self.chats)
                if chat.get("uuid") == self.active_chat.get("uuid")
            ),
            None,
        )
        rv = self.ids.chat_list
        rv.layout_manager.selected_nodes = [selected_index]
        rv.refresh_from_data()
        if selected_index is not None and selected_index > 5:
            if selected_index < len(self.chats) - 4:
                rv.scroll_to_item(selected_index)
            else:
                rv.scroll_y = 0

    def message_body(self):
        messages = [
            {
                "role": "user" if message["sender"] == "Вы" else "assistant",
                "content": message["text"],
            }
            for message in (
                self.active_messages[-10:]
                if MDApp.get_running_app().mean
                else [self.active_messages[-1]]
            )
        ]
        system_prompt = self.ids.system_prompt.text
        if len(system_prompt) != 0:
            messages.insert(0, {"role": "system", "content": system_prompt})
        return messages

    def send(self, instance):
        message = instance.text.strip()
        if 8192 >= len(message) != 0 and self.chatbot_task.done():
            self.add_message(message, bot=False)
            instance.text = ""
            self.chatbot_task = ensure_future(self.response(self.message_body()))

    def delete_selected_items(self, rv):
        for idx in sorted(rv.layout_manager.selected_nodes, reverse=True):
            del self.active_messages[idx]
        rv.layout_manager.clear_selection()
        if not self.active_messages:
            self.show_help_text()
        if rv.height < rv.layout_manager.height:
            rv.scroll_y = 1

    def restart_request_from_selected(self, rv):
        if self.chatbot_task.done():
            index = rv.layout_manager.selected_nodes[0] + 1
            self.active_messages = self.active_messages[:index]
            self.active_messages[-1]["sender"] = "Вы"
            rv.layout_manager.clear_selection()
            rv.refresh_from_data()
            self.chatbot_task = ensure_future(self.response(self.message_body()))

    def generate_chat(self):
        uuid = str(uuid4())
        name = f"Чат {len(self.chats) + 1}"
        chat = {"uuid": uuid, "name": name}
        return chat

    def new_chat(self, vertical_behavior="scroll_to_center"):
        chat = self.generate_chat()
        chat_list = self.ids.chat_list
        self.chats.append(chat)
        chat_list.layout_manager.selected_nodes = [len(self.chats) - 1]
        self.messages[chat.get("uuid")] = []
        self.switch_chat(chat)
        chat_list.vertical_behavior = vertical_behavior
        chat_list.scroll_to_last_item()

    def delete_all(self):
        def confirm(*args):
            self.messages = {}
            self.chats = []
            self.ids.message_list.scroll_to_last_item()
            self.new_chat("scroll_to_top")
            view.dismiss()

        view = Confirm(text="Удалить всё?")
        view.no = view.dismiss
        view.yes = confirm
        view.open()

    def switch_chat(self, chat):
        message_list = self.ids.message_list
        message_list.layout_manager.clear_selection()
        self.stop_response(message=False)
        self.active_chat = chat
        message_list.scroll_y = 1

    def rename_chat(self, index=None):
        if index is None:
            index = self.chats.index(self.active_chat)

        def confirm(*args):
            view.dismiss()
            new = self.active_chat if index is None else self.chats[index].copy()
            old_name = new.get("name")
            new["name"] = new_name.text
            if new.get("uuid") == self.active_chat.get("uuid"):
                self.active_chat = new
            self.chats[index] = new
            self.save_data()
            MDSnackbar(
                MDSnackbarSupportingText(
                    text=f'"{old_name}" переименован на "{new.get("name")}"', bold=True
                ),
                duration=0.5,
                radius=[dp(8), dp(8), 0, 0],
            ).open()

        view = RenameChat()
        new_name = MDTextField(
            MDTextFieldHintText(
                text=(
                    self.active_chat.get("name")
                    if index is None
                    else self.chats[index].get("name")
                )
            ),
            mode="filled",
        )
        view.ids.rename_content.add_widget(new_name)
        boxlayout = BoxLayout(spacing="10dp")
        boxlayout.add_widget(Widget())
        boxlayout.add_widget(
            MDButton(MDButtonText(text="Отмена"), on_release=view.dismiss)
        )
        boxlayout.add_widget(
            MDButton(MDButtonText(text="Подтвердить"), on_release=confirm)
        )
        view.ids.rename_content.add_widget(boxlayout)
        view.open()

    def stop_response(self, message=True):
        if not self.chatbot_task.done():
            self.chatbot_task.cancel()
            if message:
                ensure_future(
                    self.update_ui(
                        partial(
                            self.add_message,
                            " [color=e01c37](Прерван)[/color]",
                            entry=False,
                            key="sender",
                        )
                    )
                )

    def generate_random_string(self):
        length = random.randint(1, 20)
        random_string = "".join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )
        positions = random.sample(
            range(length - 1), random.randint(0, min(5, length - 1))
        )
        for pos in sorted(positions, reverse=True):
            random_string = random_string[:pos] + "\n" + random_string[pos:]
        return random_string

    async def response(self, messages):
        app = MDApp.get_running_app()
        self.ids.loader.active = True
        self.ids.text_button.icon = "stop"
        entry = True
        headers = {"Authorization": app.bearer}
        if not self.active_provider and not self.active_model:
            return
        data = {
            "q": messages,
            "m": self.active_model,
            "p": self.active_provider,
            "t": app.temperature / 100,
        }
        try:
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as client:
                print("Начало генерации")
                if app.stream:
                    async with client.stream(
                        method="POST",
                        url=f"{self.api}/gpt/stream/",
                        data=dumps(data),
                        headers=headers,
                    ) as response:
                        async for chunk in response.aiter_text():
                            await self.update_ui(
                                partial(self.add_message, chunk, entry)
                            )
                            entry = False
                else:
                    response = await client.post(
                        url=f"{self.api}/gpt/default/",
                        data=dumps(data),
                        headers=headers,
                    )
                    completion = response.json()
                    await self.update_ui(
                        partial(self.add_message, completion["response"], entry)
                    )

        except CancelledError:
            print("Прерывание генерации")

        finally:
            print("Конец генерации")
            self.ids.text_button.icon = "send"
            self.ids.loader.active = False

    async def load_data(self):
        try:
            with open(
                os.path.join(self.env, "data.json"), "r", encoding="utf-8"
            ) as file:
                data = load(file)
                messages = data.get("messages", {})
                chats = data.get("chats", [])
                active_chat = data.get("active_chat", {})
                return messages, chats, active_chat

        except FileNotFoundError:
            return {}, [], {}

        except (FileNotFoundError, JSONDecodeError):
            with open(os.path.join(os.path.dirname(__file__), "data.json"), "w") as f:
                dump({"messages": {}, "chats": [], "active_chat": {}}, f)
            return {}, [], {}

    def save_data(self):
        data = {
            "messages": self.messages,
            "chats": self.chats,
            "active_chat": self.active_chat,
        }
        with open(os.path.join(self.env, "data.json"), "w", encoding="utf-8") as file:
            dump(data, file, ensure_ascii=False)

    def scroll_y(self, widget, y: float, animation=False):
        if widget.height < widget.layout_manager.height:
            if animation:
                Animation(scroll_y=y, d=0.5, t="linear").start(widget)
            else:
                widget.scroll_y = y

    async def update_ui(self, callback):
        await sleep(0)
        callback()

    def show_help_text(self, text="Как я могу помочь вам сегодня?"):
        if not hasattr(self, "help_label"):
            self.help_label = MDLabel(
                halign="center",
                text=text,
                font_style="Title",
                bold=True,
                padding=(dp(10), 0, dp(10), 0),
            )
            self.ids.screen.add_widget(self.help_label)

    def hide_help_text(self):
        if hasattr(self, "help_label"):
            self.ids.screen.remove_widget(self.help_label)
            del self.help_label

    async def fetch_providers(self):
        self.providers = []
        self.ids.spinner_provider.active = True
        try:
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as session:
                r = await session.get(url=f"{self.api}/gpt/providers/")
                r.raise_for_status()
                providers = r.json()
                provider_list = providers.get("providers")
                self.providers = [
                    {"text": text, "active": (text == self.active_provider)}
                    for text in provider_list
                ]
                selected_index = next(
                    (
                        index
                        for index, provider in enumerate(self.providers)
                        if provider["active"]
                    ),
                    None,
                )
                rv = self.ids.provider_list
                rv.layout_manager.selected_nodes = [selected_index]
                rv.refresh_from_data()

        except Exception as e:
            print(e)
            Clock.schedule_once(lambda dt: create_task(self.fetch_providers()), 10)

        finally:
            self.ids.spinner_provider.active = False

    async def fetch_models(self):
        self.models = []
        self.ids.spinner_provider.active = True
        try:
            params: Dict[str, Any] = {"provider": self.active_provider}
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as session:
                r = await session.get(url=f"{self.api}/gpt/models/", params=params)
                r.raise_for_status()
                models = r.json()
                model_list = models.get("models")
                default_model = models.get("default")
                if self.active_model not in model_list:
                    self.active_model = str(default_model)
                self.models = [
                    {"text": text, "selected": (text == self.active_model)}
                    for text in model_list
                ]
                selected_index = next(
                    (
                        index
                        for index, model in enumerate(self.models)
                        if model["selected"]
                    ),
                    None,
                )
                rv = self.ids.model_list
                rv.layout_manager.selected_nodes = [selected_index]
                rv.refresh_from_data()

        except Exception as e:
            print(e)
            Clock.schedule_once(lambda dt: create_task(self.fetch_models()), 10)

        finally:
            self.ids.spinner_provider.active = False

    def save_system_prompt(self):
        save_config("settings", "system", self.ids.system_prompt.text, self.env)
