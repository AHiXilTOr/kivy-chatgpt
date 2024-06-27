"""Change screen"""

import os
from asyncio import ensure_future
from arc.screens.base_screen import Base
from httpx import ConnectError, AsyncClient, HTTPStatusError
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp


Builder.load_file(os.path.join(os.path.dirname(__file__), "change_screen.kv"))


class ChangeScreen(Base):
    def change(self):
        self.ids.spinner.active = True
        code = self.ids.code.text
        new_password = self.ids.new_password.text
        confirm_password = self.ids.confirm_password.text

        if len(new_password) < 6:
            self.ids.spinner.active = False
            self.ids.error.text = (
                "[color=e01c37]Пароль должен содержать не менее 6 символов[/color]"
            )
            return

        if new_password == confirm_password:
            params = {
                "email": MDApp.get_running_app().email,
                "new_password": new_password,
                "code": code,
                "reset": True,
            }

            ensure_future(self.response(params))

        else:
            self.ids.spinner.active = False
            self.ids.error.text = "[color=e01c37]Пароли не совпадают[/color]"

    async def response(self, params):
        self.ids.code.disabled = True
        self.ids.new_password.disabled = True
        self.ids.confirm_password.disabled = True
        self.ids.change_button.disabled = True

        app = MDApp.get_running_app()

        try:
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as client:
                response = await client.post(
                    url=f"{self.api}/accounts/verify-code/", json=params
                )
                response.raise_for_status()
                if response.status_code == 200:
                    data = response.json()["access_token"].encode("utf-8")
                    with open(os.path.join(self.env, "token.json"), "wb") as f:
                        encrypted_token = app.sha.encrypt(data)
                        f.write(encrypted_token)

                    self.set_screen("login_screen")

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
            self.ids.code.disabled = False
            self.ids.new_password.disabled = False
            self.ids.confirm_password.disabled = False
            self.ids.change_button.disabled = False

            Clock.schedule_once(lambda dt: setattr(self.ids.error, "text", ""), 10)
