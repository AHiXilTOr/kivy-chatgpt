"""Profile screen"""

import os
import ast
import json
from asyncio import ensure_future
from arc.screens.base_screen import Base
from arc.widgets.confirm import Confirm
from httpx import ConnectError, AsyncClient, HTTPStatusError
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp


Builder.load_file(os.path.join(os.path.dirname(__file__), "profile_screen.kv"))


class ProfileScreen(Base):
    username = StringProperty("Имя: Загрузка...")
    email = StringProperty("Почта: Загрузка...")
    balance = StringProperty("Баланс: Загрузка...")

    def logout(self):
        def confirm(*args):
            app = MDApp.get_running_app()
            app.username = ""
            app.email = ""
            app.balance = 0

            path = os.path.join(self.env, "token.json")
            if os.path.exists(path):
                os.remove(path)

            view.dismiss()
            self.set_screen("login_screen", "right")

        view = Confirm(text="Выйти из аккаунта?")
        view.no = view.dismiss
        view.yes = confirm
        view.open()

    def save(self):
        try:
            with open(
                os.path.join(self.env, "data.json"), "r", encoding="utf-8"
            ) as file:
                data = json.load(file)
            ensure_future(self.response(data))
        except FileNotFoundError:
            self.ids.error.text = "[color=e01c37]Нет данных для сохранения[/color]"

    def load(self):
        ensure_future(self.response())

    async def response(self, data=None):
        self.ids.spinner.active = True
        self.ids.load.disabled = True
        self.ids.save.disabled = True
        bearer = MDApp.get_running_app().bearer

        try:
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as client:
                if data:
                    response = await client.post(
                        url=f"{self.api}/accounts/save/",
                        json={"content": str(data)},
                        headers={"Authorization": bearer},
                    )
                else:
                    response = await client.get(
                        url=f"{self.api}/accounts/load/",
                        headers={"Authorization": bearer},
                    )
                response.raise_for_status()
                if response.status_code == 200:
                    if data:
                        error = "[b]Сохранено![/b]"
                    else:
                        with open(
                            os.path.join(self.env, "data.json"),
                            "w",
                            encoding="utf-8",
                        ) as file:
                            data = ast.literal_eval(response.json()["content"])
                            data = json.dumps(data)
                            data = json.loads(data)
                            json.dump(data, file, ensure_ascii=False)

                            main = self.manager.get_screen("main_screen")
                            ensure_future(main.init_data())

                        error = "[b]Загружено![/b]"

                    self.ids.error.text = error

        except ConnectError:
            self.ids.error.text = "[color=e01c37]Попробуйте позже[/color]"

        except HTTPStatusError as e:
            try:
                self.ids.error.text = (
                    f'[color=e01c37]{e.response.json()["detail"]}[/color]'
                )
            except Exception:
                self.ids.error.text = f"[color=e01c37]{e.response}[/color]"

        except Exception as e:
            print(e)
            self.ids.error.text = "[color=e01c37]Что-то пошло не так[/color]"

        finally:
            self.ids.spinner.active = False
            self.ids.load.disabled = False
            self.ids.save.disabled = False

            Clock.schedule_once(lambda dt: setattr(self.ids.error, "text", ""), 10)
