from .widgets.label import MyLabel
from .widgets.switch import PickSwitch
from .config import read_config, save_config

from env import API, PROXY

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.toolbar import MDTopAppBar

import httpx, asyncio

class PropertySheet(MDBoxLayout):
    def __init__(self, setting, **kwargs):
        super().__init__(**kwargs)
        self.orientation="vertical" 
        self.size_hint_y=None 
        self.height='300dp'
        self.setting = setting

        self.add_widget(MDTopAppBar(title=setting, elevation=0))

        scroll = ScrollView()
        self.add_widget(scroll)

        property = MDBoxLayout(orientation="vertical", spacing="20dp", adaptive_height=True, padding=dp(15))
        scroll.add_widget(property)

        access = read_config('settings', f'{self.setting}-token')
        token = MDTextField(hint_text="Использовать свой токен", mode="rectangle", hint_text_color_normal="white", line_color_normal="white", text=access if access else "")
        property.add_widget(token)

        role = read_config('settings', f'{self.setting}-role')
        role = MDTextField(hint_text="Системная роль", mode="rectangle", hint_text_color_normal="silver", line_color_normal="white", multiline=True, text=role if role else "")
        property.add_widget(role)

        token.bind(text=self.access_update)
        role.bind(text=self.role_update)

    def access_update(self, instance, value):
        save_config('settings', f'{self.setting}-token', f"{instance.text}")
    
    def role_update(self, instance, value):
        save_config('settings', f'{self.setting}-role', f"{instance.text}")

class GPT(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_size = True
        self.orientation = 'vertical'

        self.switch_group = []

        self.loading = MDBoxLayout(adaptive_size=True, padding=(0, dp(10), 0, dp(10)))
        self.label = MyLabel(anim=False, size_hint_y=None, height=dp(30))
        self.loading.add_widget(self.label)
        self.add_widget(self.loading)

        asyncio.create_task(self.fetch_and_add_settings())

    async def fetch_and_add_settings(self):
        self.label.text = "Загрузка ..."
        
        try:
            self.settings = await self.fetch_settings()
            self.remove_widget(self.loading)

            model = read_config('settings', 'model')

            for setting in self.settings["models"]:
                self.create_settings_widget(setting, model)

        except:
            self.label.text = "Все попытки подключения не удались"
            Clock.schedule_once(lambda dt: asyncio.create_task(self.fetch_and_add_settings()), 5)
            
    async def fetch_settings(self):
        async with httpx.AsyncClient(timeout=120, verify=False, proxy=PROXY) as session:
            r = await session.get(url=f"{API}/gpt/models")
            r.raise_for_status()
            return r.json()

    def on_switch_active(self, instance, value, active_switch):
        for switch in self.switch_group:
            
            if switch != active_switch:
                switch.active = False
                switch.movement(False)   
                   
        active_switch.movement(True)
        active_index = self.switch_group.index(active_switch)

        selected_model = self.settings["models"][active_index]
        save_config('settings', 'model', str(selected_model))

    def create_settings_widget(self, setting, model):
        settings_layout = MDBoxLayout(adaptive_size=True, padding=(0, dp(1), 0, dp(1)), spacing=dp(5))
        label = MyLabel(text=setting, size_hint_y=None, height=dp(30), anim=False)
        switch = PickSwitch(size_hint_y=None, active=model == setting, bg=False)
        switch.bind(active=lambda instance, value, switch=switch: self.on_switch_active(instance, value, switch))      
        settings_layout.add_widget(label)
        settings_layout.add_widget(switch)

        if setting == "OpenAI":
            settings_layout.add_widget(MDIconButton(icon="lead-pencil", icon_size='17sp', ripple_scale=0.85, ripple_duration_in_fast=.1, ripple_duration_in_slow=.1, on_release=lambda x, setting=setting: self.show_list_bottom_sheet(x, setting), theme_icon_color="Custom", icon_color="white"))   

        self.switch_group.append(switch)
        self.add_widget(settings_layout)

    def show_list_bottom_sheet(self, x, setting):
        bottom_sheet_menu = MDCustomBottomSheet(screen=PropertySheet(setting))
        bottom_sheet_menu.open()
        