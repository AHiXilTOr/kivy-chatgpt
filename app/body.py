from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.effects.scroll import ScrollEffect
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextFieldRect
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.slider import MDSlider
from kivymd.uix.screen import MDScreen
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelThreeLine
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import (
    MDNavigationLayout, 
    MDNavigationDrawer,
    MDNavigationDrawerDivider,
    MDNavigationDrawerMenu, 
    MDNavigationDrawerHeader, 
    MDNavigationDrawerItem
)

from .widgets.label import MyLabel
from .widgets.switch import PickSwitch
from .config import read_config, save_config
from .gpt import GPT
from .colors import colors

from env import API, PROXY

import asyncio, json, httpx, uuid, re, threading, time
from datetime import datetime
from threading import Thread

from kivy.clock import mainthread

class INFO(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class BarLabel(Label):
    def on_size(self, *args):
        self.text_size = self.size

class CustomSlider(MDSlider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = '50dp'
        self.hint_bg_color= "gray"
        self.hint_text_color = "white"
        self.show_off = False
        
class ChatBotApp(MDApp):
    data = StringProperty("")
    active_chat_button = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.messages = {}
        self.chats = []
        
        self.active_chat = None
        self.temperature = read_config("settings", "temperature")
        self.action = None
        self.is_updating = False
        
        self.load_data() 

        app = MDApp.get_running_app()
        app.platform = "desktop" if platform in ["win", "macosx", "linux"] else "mobile"

    def build(self):
        self.setup_ui()
        Clock.schedule_interval(self.updated, 1/60)
        return self.create_main_layout()
        
    def updated(self, *args):
        if not self.is_updating and self.data:
            self.is_updating = True
            Clock.schedule_once(self.update_interface, .5)
            
    def update_interface(self, *args):
        self.response_label.text += self.data
        added_length = len(self.data)
        self.data = self.data[:-added_length]
        self.is_updating = False
                
    def setup_ui(self):
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.5
        self.theme_cls.colors = colors
        self.theme_cls.theme_style = "Dark"
        self.icon = r'app\icon.png'
        Window.softinput_mode = 'pan'
    
    def create_main_layout(self):
        main = MDNavigationLayout()

        self.sm = ScreenManager()
        main.add_widget(self.sm)
        
        start_screen = MDScreen(name="main")
        self.sm.add_widget(start_screen)
        
        self.info_screen = INFO(name="information")
        self.sm.add_widget(self.info_screen)

        self.double = BoxLayout(orientation='vertical')
        start_screen.add_widget(self.double)

        self.create_header()
        self.create_layout()
        self.create_footer()
        self.create_navigation_drawer(main)
        return main
    
    def create_header(self):
        self.header = MDTopAppBar(title='Чат', elevation=0, 
            left_action_items=[['menu', lambda x: self.left.set_state("open")]], 
            right_action_items=[["lead-pencil", lambda x: self.show_rename_chat_popup()],
                                ["cog", lambda x: self.right.set_state("open")], 
                                ["information", lambda x: self.set_screen("information", "left")]])

        self.double.add_widget(self.header)
    
    def create_layout(self):
        self.layout = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(12))

        self.scroll_view = ScrollView(effect_cls=ScrollEffect)
        self.message_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        self.message_layout.bind(minimum_height=self.message_layout.setter('height'))

        self.pre_text(self.message_layout)

        self.scroll_view.add_widget(self.message_layout)
        self.layout.add_widget(self.scroll_view)
        self.double.add_widget(self.layout)

        self.message_layout.bind(size=self.update_scroll)  
            
    def create_footer(self):
        footer = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(6))
        
        self.input_box = MDTextFieldRect(background_color=self.theme_cls.bg_dark, hint_text='Напиши свой вопрос...', font_size=sp(15), size_hint_x=1, foreground_color="white", cursor_color="white")
        self.input_box.bind(on_text_validate=self.send_message)

        self.send_button = MDIconButton(ripple_color="#2196F3", ripple_scale=0.85, ripple_duration_in_fast=.1, ripple_duration_in_slow=.1,icon="application-import",on_release=self.send_message, size_hint=(None, 1), md_bg_color=self.theme_cls.bg_dark)
        self.send_button.icon_size = dp(24)
        self.send_button.rounded_button = False
        self.send_button._radius = dp(0.1)
        
        footer.add_widget(self.input_box)
        footer.add_widget(self.send_button)
        self.layout.add_widget(footer)
        
    def create_navigation_drawer(self, main):
        self.right = MDNavigationDrawer(enable_swiping=False, anchor="right", radius=0)
        
        right_menu = MDNavigationDrawerMenu(spacing=dp(5))
        right_menu.add_widget(MDNavigationDrawerHeader(title_color="white", text_color="white", title="Настройки", text="В автономном режиме", title_font_size='24sp', text_font_size='16sp'))
        right_menu.add_widget(MDNavigationDrawerDivider())
        
        settings1 = MDBoxLayout(adaptive_size=True)
        settings1.add_widget(MyLabel(text="Экспериментальный", anim=False))
        settings1.add_widget(PickSwitch(func=self.theme, size_hint_y=None))
        right_menu.add_widget(settings1)
        
        right_menu.add_widget(MDExpansionPanel(content=GPT(), panel_cls=MDExpansionPanelThreeLine(text="Выбор", secondary_text="Выберите подходящую", tertiary_text="модель для генерации текста", opposite_colors=False)))

        slider = MDBoxLayout(orientation='vertical', adaptive_height=True)
        temperature_slider = CustomSlider(min=0.0, max=5.0, step=0.1)

        temperature = read_config("settings", "temperature")
        
        if temperature:
            temperature_slider.value = round(float(temperature), 1)
        else:
            value = "0.5"
            temperature_slider.value = value
            save_config("settings", "temperature", value)

        label = MDLabel(text=f"Температура: {temperature_slider.value}", theme_text_color="Secondary")

        slider.add_widget(temperature_slider)
        slider.add_widget(label)

        def update_label_value(instance, value):
            value = round(value, 1)
            self.temperature = value
            temperature_slider.value = value
            label.text = f"Температура: {value}"
            save_config("settings", "temperature", f"{value}")

        temperature_slider.bind(value=update_label_value)
        
        right_menu.add_widget(slider)
        self.right.add_widget(right_menu)
        
        self.left = MDNavigationDrawer(enable_swiping=False, radius=0)

        self.left_menu = MDNavigationDrawerMenu(spacing=dp(5))
        self.left_menu.add_widget(MDNavigationDrawerDivider())
        self.left_menu.add_widget(MDNavigationDrawerItem(icon="playlist-plus", text_color="white", selected_color="white", text="Начать новый чат", radius=(dp(5), dp(5), dp(5), dp(5)), on_release=lambda x: Clock.schedule_once(self.restore, .6), icon_color="white"))
        self.left_menu.add_widget(MDNavigationDrawerDivider())
        
        self.left.add_widget(self.left_menu)
        
        main.add_widget(self.right)
        main.add_widget(self.left)
        
    def on_start(self):
        self.bind(active_chat_button=self.current_chat)
        
        self.double.bind(size=self.on_window_size, pos=self.on_window_size)
        self.on_window_size(self.double, None)

        self.info_double = self.info_screen.ids.double_layout
        self.info_double.bind(size=self.on_window_size, pos=self.on_window_size)

        if not self.active_chat:

            if self.chats:
                self.active_chat = self.chats[-1]

        self.container = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(10))
        self.left_menu.add_widget(self.container)

        self.load_active_chat()
        
        if not self.chats:
            self.create_default_chat()
    
    def on_stop(self):
        self.save_data()
            
    def load_active_chat(self):
        for chat_data in self.chats:
            chat_id, chat_info = next(iter(chat_data.items()))
            chat_name = chat_info["name"]
            
            chat = MDBoxLayout(adaptive_height=True)
            button = Button(text=chat_name, on_release=lambda x, chat_id=chat_id: self.load_chat_messages(chat_id, x), background_color="#bbdefb")
            chat.add_widget(button)

            if self.active_chat == chat_id:
                button.background_color = "#2196F3"
                self.load_chat_messages(self.active_chat, button)

            button = MDIconButton(icon="trash-can", icon_size=dp(20), theme_icon_color="Custom", icon_color="white", ripple_duration_in_fast=.1, ripple_duration_in_slow=.1, on_release=lambda x, chat_id=chat_id: self.delete_chat_history(chat_id, x))
            button.rounded_button = False
            button._radius = dp(0.1)
            
            chat.add_widget(button)
            self.container.add_widget(chat)

    def set_active_chat_button(self, button):
        if self.active_chat_button:
            self.active_chat_button.background_color = "#bbdefb"

        self.active_chat_button = button
        
    def create_default_chat(self):
        chat_id = str(uuid.uuid4())
        chat_name = f"Чат {len(self.chats) + 1}"
        self.chats.append({chat_id: {"name": chat_name}})
        self.active_chat = chat_id
        self.create_chat_widget(chat_id, "#2196F3", chat_name)
        
    def create_chat_widget(self, chat_id, background_color, chat_name):
        if len(self.chats) <= 10:
            chat = MDBoxLayout(adaptive_height=True)
            
            button = Button(text=chat_name, on_release=lambda x, chat_id=chat_id: self.load_chat_messages(chat_id, x), background_color=background_color)
            chat.add_widget(button)
            
            trash = MDIconButton(icon="trash-can", theme_icon_color="Custom", icon_color="white",icon_size=dp(20), ripple_duration_in_fast=.1, ripple_duration_in_slow=.1, on_release=lambda x, chat_id=chat_id: self.delete_chat_history(chat_id, x))
            trash.rounded_button = False
            trash._radius = dp(0.1)
            chat.add_widget(trash)
            self.container.add_widget(chat)

            self.load_chat_messages(chat_id, button)
        
    def load_data(self):    
        try:
            with open('chat_data.json', 'r') as file:
                data = json.load(file)
                self.messages = data.get('messages', {})
                self.chats = data.get('chats', [])
                self.active_chat = data.get('active_chat')

        except FileNotFoundError:
            with open('chat_data.json', 'w') as f:
                json.dump({}, f)

    def save_data(self):
        data = {'messages': self.messages, 'chats': self.chats, 'active_chat': self.active_chat}
        with open('chat_data.json', 'w') as file:
            json.dump(data, file)

    def restore(self, instance):
        chat_id = str(uuid.uuid4())
        chat_name = f"Чат {len(self.chats) + 1}"
        self.chats.append({chat_id: {"name": chat_name}})
        self.create_chat_widget(chat_id, "#2196F3", chat_name)
        
    def load_chat_messages(self, chat_id, instance, *args):
        if hasattr(self, 'chatbot_task') and not self.chatbot_task.done():
            self.chatbot_task.cancel()
            
        if instance == self.active_chat_button:
            return
        
        instance.background_color = "#2196F3"
        self.set_active_chat_button(instance)
        
        self.message_layout.clear_widgets()
        self.pre_text(self.message_layout)

        self.active_chat = chat_id

        if chat_id in self.messages:
            chat_messages = self.messages[chat_id]

            for message_data in chat_messages:
                sender = message_data['sender']
                content = self.format_text(message_data['content'])

                if sender == 'user':
                    self.display_user_message(content)

                elif sender == 'chatbot':
                    self.display_chatbot_message(content)

    def display_user_message(self, content):
        if hasattr(self, 'bt'):
            self.ubar.remove_widget(self.bt)
             
        self.ubar = BoxLayout()
        label = BarLabel(markup=True, text="[b][color=ffd966]Вы:  [/color][/b]", size_hint=(1, None), halign="left", pos_hint={'center_y': 0.5})
        label.texture_update()
        label.size = label.texture_size
        
        self.ubar.add_widget(label)
        
        self.user_label = MyLabel(widget=self.message_layout, text=f'{content}', font_size=sp(16),valign='top')
        
        self.bt = MDIconButton(icon="backup-restore", theme_icon_color="Custom", _no_ripple_effect = True, icon_color="white", on_release=lambda x, label=self.user_label: self.restart_generation(label, x), pos_hint={'center_y': 0.5})
        self.ubar.add_widget(self.bt)
        
        self.message_layout.add_widget(self.ubar)
        self.message_layout.add_widget(self.user_label)

    def display_chatbot_message(self, content):
        self.bar = BoxLayout()
        label = BarLabel(markup=True,text="[b][color=33cc33]GPT:  [/color][/b]", size_hint=(1, None), halign="left", pos_hint={'center_y': 0.5})
        label.texture_update()
        label.size = label.texture_size
        
        self.bar.add_widget(label)
        self.message_layout.add_widget(self.bar)

        self.response_label = MyLabel(widget=self.message_layout, text=f'{content}', font_size=sp(16), valign='top', markup=True)
        self.message_layout.add_widget(self.response_label)
        
    def send_message(self, instance):
        self.send_button.disabled = True
        self.send_button.icon = "application-export"

        if not self.action:
            self.action = True
            self.user_message = self.input_box.text
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_message_data = {'timestamp': timestamp,'sender': 'user','content': self.user_message}
            
            chat_id = self.active_chat if hasattr(self, 'active_chat') else None
            
            if chat_id:

                if chat_id not in self.messages:
                    self.messages[chat_id] = []

                self.messages[chat_id].append(user_message_data)

            if len(self.user_message) == 0:
                return 0

            self.display_user_message(self.user_message)
            
            self.input_box.text = ''
            
            model = read_config('settings', 'model')
            self.chatbot_task = asyncio.ensure_future(self.get_chatbot_response_async(self.user_message, model))

    def restart_generation(self, instance, x):
        x.disabled = True
        self.send_button.disabled = True

        if not self.action:
            self.action = True

            user_message = instance.text
            model = read_config('settings', 'model')
            
            before = instance.parent.children.index(instance)

            for widget in instance.parent.children[:before]:
                instance.parent.remove_widget(widget)
            
            after = instance.parent.children.index(instance)
            index = int((before - after) / 2)
            
            del self.messages[self.active_chat][-index:]

            self.chatbot_task = asyncio.ensure_future(self.get_chatbot_response_async(user_message, model, x))

    async def get_chatbot_response_async(self, user_message, model, x=None):
        self.bar = BoxLayout()
        label = BarLabel(markup=True, text="[b][color=33cc33]GPT:  [/color][/b]", size_hint=(None, None), halign="left", pos_hint={'center_y': 0.5})
        label.texture_update()
        label.size = label.texture_size
        
        self.bar.add_widget(label)
        loader = MDSpinner(size_hint=(None, None), size=(dp(10), dp(10)), color="white", pos_hint={'center_y': 0.5})
        self.bar.add_widget(loader)

        self.message_layout.add_widget(self.bar)

        self.response_label = MyLabel(widget=self.message_layout, font_size=sp(16), valign='top', markup=True)
        self.message_layout.add_widget(self.response_label)

        self.bt.disabled = True

        data = {"q": user_message, "m": model, "t": self.temperature}

        model_token = read_config("settings", f"{model}-token")
        if model_token:
            data["k"] = model_token

        model_role = read_config("settings", f"{model}-role")
        if model_role:
            data["r"] = model_role

        headers = {"content-type": "application/json"}

        try:
            self.response_label.text = self.data
            client = httpx.AsyncClient(timeout=120, verify=False, proxy=PROXY)
            async with client.stream(method='POST', url=f"{API}/gpt/stream", data=json.dumps(data), headers=headers) as r:
                
                async for chunk in r.aiter_text():
                    print(chunk)
                    chunk = "[color=e01b1b]Настройка:[/color] Выберите модель" if chunk == "Internal Server Error" else chunk
                    self.data += chunk

        except httpx.ConnectError:
            self.response_label.text = f'[color=AAFCFF]Ошибка:[/color] ' + str("Все попытки подключения не удались")

        except Exception as e:
            error_message = str(e)
            
            if "peer closed connection without sending complete message body" in error_message:
                error = "Попробуйте позже"
            else:
                error = error_message
                
            self.response_label.text = f'[color=AAFCFF]Ошибка:[/color] {error}'
            
        except asyncio.CancelledError:
            print("Прерывание генерации")
            self.message_layout.remove_widget(self.response_label)
            return

        finally:
            self.response_label.text = self.format_text(self.response_label.text)

            self.bt.disabled = False

            if x:
                x.disabled = False

            self.send_button.icon = "application-import"
            self.send_button.disabled = False
            self.action = False
            self.bar.remove_widget(loader)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            chatbot_response_data = {'timestamp': timestamp,'sender': 'chatbot','content': self.response_label.text}

            chat_id = self.active_chat if hasattr(self, 'active_chat') else None

            if chat_id:

                if chat_id not in self.messages:
                    self.messages[chat_id] = []

                self.messages[chat_id].append(chatbot_response_data)

    def theme(self, value):
        theme_style = 'Light' if value else 'Dark'
        self.theme_cls.theme_style = theme_style
        save_config('settings', 'theme', str(value))

    def set_screen(self, screen_name, direction=None, *args):
        if direction:
            self.sm.transition.direction = direction

        self.sm.current = screen_name
    
    def on_window_size(self, instance, value):
        if self.platform == 'desktop':

            if Window.width > dp(600):
                instance.size_hint_x = None
                instance.width = dp(600)
                instance.pos_hint = {"center_x": 0.5}
            else:
                instance.size_hint_x = 1
    
    def pre_text(self, widget):
        message_label = MyLabel(widget=self.message_layout, text='[color=FFFFFF][b]{[/color][color=33cc33]INFO[/color][color=FFFFFF]}[/b][/color] [color=FFFFFF]Эта модель была создана на основе технологии трансформеров, которая позволяет модели обрабатывать большие объемы текста и понимать связи между словами и предложениями.[/color]', font_size=sp(16), markup=True, valign='top', disabled=True)
        widget.add_widget(message_label)

    def delete_chat_history(self, chat_id, instance):
        instance.disabled = True

        if chat_id in self.messages:
            del self.messages[chat_id]

        for i, chat_data in enumerate(self.chats):
            if next(iter(chat_data)) == chat_id:
                del self.chats[i]
                break

        instance.parent.parent.clear_widgets()
        self.load_active_chat()

        print(self.chats)

        if instance.parent == self.active_chat_button.parent:

            try: 
                self.active_chat = str(self.chats[-1])
                self.load_chat_messages(self.active_chat, self.container.children[0].children[-1])
                
            except:
                self.create_default_chat()

    def current_chat(self, instance, value):
        self.header.title = self.active_chat_button.text

    def update_scroll(self, *args):
        self.scroll_view.scroll_y = 1

        if self.scroll_view.height < self.scroll_view.children[0].height:
            self.scroll_view.scroll_y = 0

    def format_text(self, text):
        matches = re.findall(r"```(.*?)```", text, re.DOTALL)
        for match in matches:
            formatted_match = f"[color=#33cc33]{match}[/color]"
            text = text.replace(f"```{match}```", formatted_match)
        return text

    def show_rename_chat_popup(self):
        current_chat_name = self.active_chat_button.text
        
        def rename_chat(instance):
            new_chat_name = text_input.text

            if len(new_chat_name) > 26:
                new_chat_name = f"{new_chat_name[:26]}..."

            for chat in self.chats:
                if self.active_chat in chat:
                    chat[self.active_chat]["name"] = new_chat_name
                    break
            
            self.header.title = new_chat_name
            self.active_chat_button.text = new_chat_name
            popup.dismiss()

        layout = GridLayout(cols=1)
        text_input = MDTextFieldRect(hint_text=current_chat_name, font_size=sp(15), size_hint_x=1)
        layout.add_widget(text_input)

        btn_layout = BoxLayout(size_hint=(1, None), height=dp(40))
        btn_layout.add_widget(Button(text="Отмена", on_release=lambda x: popup.dismiss()))
        btn_layout.add_widget(Button(text="Подтвердить", on_release=rename_chat))
        layout.add_widget(btn_layout)

        popup = Popup(title='Переименовать чат', content=layout)
        popup.size_hint=(None, None)
        popup.size=(dp(300), dp(150))
        popup.open()