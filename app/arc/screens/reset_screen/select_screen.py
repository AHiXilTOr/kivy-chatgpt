"""Select screen"""

import os
from asyncio import ensure_future
from arc.screens.base_screen import Base
from httpx import ConnectError, AsyncClient, HTTPStatusError
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp


Builder.load_file(os.path.join(os.path.dirname(__file__), "select_screen.kv"))


class SelectScreen(Base):
    def select(self):
        app = MDApp.get_running_app()
        self.ids.spinner.active = True
        email = app.email

        if len(email) > 0:
            self.ids.email.text = email

        else:
            email = self.ids.email.text

            if len(email) >= 0:
                if not self.validate_email(email):
                    self.ids.spinner.active = False
                    self.ids.error.text = (
                        "[color=e01c37]Некорректный адрес электронной почты[/color]"
                    )
                    return

            app.email = email

        params = {"email": app.email}

        ensure_future(self.response(params))

    async def response(self, params):
        self.ids.email.disabled = True
        self.ids.select_button.disabled = True
        self.ids.back_button.disabled = True

        try:
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as client:
                response = await client.post(
                    url=f"{self.api}/accounts/select-password/", json=params
                )
                response.raise_for_status()
                if response.status_code == 200:
                    self.set_screen("change_screen")

        except ConnectError:
            self.ids.error.text = "[color=e01c37]Подключение отсутствует[/color]"

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
            self.ids.email.disabled = False
            self.ids.select_button.disabled = False
            self.ids.back_button.disabled = False

            Clock.schedule_once(lambda dt: setattr(self.ids.error, "text", ""), 10)
