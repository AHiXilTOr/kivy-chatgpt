"""Register screen"""

import os
from asyncio import ensure_future
from arc.screens.base_screen import Base
from httpx import ConnectError, AsyncClient, HTTPStatusError
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp

Builder.load_file(os.path.join(os.path.dirname(__file__), "register_screen.kv"))


class RegisterScreen(Base):
    def register(self, *args):
        self.ids.spinner.active = True
        self.ids.error.text = ""
        username = self.ids.username.text
        email = self.ids.email.text
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text

        if len(username) < 4:
            self.ids.spinner.active = False
            self.ids.error.text = "[color=e01c37]Имя пользователя должно содержать не менее 4 символов[/color]"
            return

        if not self.validate_username(username):
            self.ids.spinner.active = False
            self.ids.error.text = "[color=e01c37]Некорректное имя пользователя[/color]"
            return

        if len(password) < 6:
            self.ids.spinner.active = False
            self.ids.error.text = (
                "[color=e01c37]Пароль должен содержать не менее 6 символов[/color]"
            )
            return

        if len(email) > 0:
            if not self.validate_email(email):
                self.ids.spinner.active = False
                self.ids.error.text = (
                    "[color=e01c37]Некорректный адрес электронной почты[/color]"
                )
                return

        if password == confirm_password:
            params = {
                "username": username,
                "email": email if email else None,
                "password": password,
            }

            ensure_future(self.response(params))

        else:
            self.ids.spinner.active = False
            self.ids.error.text = "[color=e01c37]Пароли не совпадают[/color]"

    async def response(self, params):
        self.ids.username.disabled = True
        self.ids.email.disabled = True
        self.ids.password.disabled = True
        self.ids.confirm_password.disabled = True
        self.ids.register_button.disabled = True
        self.ids.screen_button.disabled = True

        app = MDApp.get_running_app()

        try:
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as client:
                response = await client.post(
                    url=f"{self.api}/accounts/signup/", json=params
                )
                response.raise_for_status()
                if response.status_code == 200:
                    data = response.json()["access_token"].encode("utf-8")
                    with open(
                        os.path.join(self.env, "token.json"),
                        "wb",
                    ) as f:
                        encrypted_token = app.sha.encrypt(data)
                        f.write(encrypted_token)

                    self.set_screen("login_screen")
                elif response.status_code == 204:
                    app.email = params["email"]
                    self.set_screen("verification_screen")

        except ConnectError:
            self.ids.error.text = "[color=e01c37]Подключение отсутствует[/color]"

        except HTTPStatusError as e:
            try:
                self.ids.error.text = (
                    f'[color=e01c37]{e.response.json()["detail"]}[/color]'
                )
            except Exception:
                self.ids.error.text = "[color=e01c37]{e.response}[/color]"

        except Exception as e:
            print(e)
            self.ids.error.text = "[color=e01c37]Что-то пошло не так[/color]"

        finally:
            self.ids.spinner.active = False
            self.ids.username.disabled = False
            self.ids.email.disabled = False
            self.ids.password.disabled = False
            self.ids.confirm_password.disabled = False
            self.ids.register_button.disabled = False
            self.ids.screen_button.disabled = False

            Clock.schedule_once(lambda dt: setattr(self.ids.error, "text", ""), 10)
