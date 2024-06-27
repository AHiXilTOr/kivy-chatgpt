"""Login screen"""

import os
from arc.screens.base_screen import Base
from asyncio import ensure_future
from httpx import ConnectError, AsyncClient, HTTPStatusError
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp


Builder.load_file(os.path.join(os.path.dirname(__file__), "login_screen.kv"))


class LoginScreen(Base):
    def check_token_file(self):
        return os.path.isfile(os.path.join(self.env, "token.json"))

    def get_token(self):
        with open(os.path.join(self.env, "token.json"), "rb") as f:
            data = f.read()
            try:
                token = MDApp.get_running_app().sha.decrypt(data).decode("utf-8")
            except Exception:
                return None
            return token

    def on_enter(self):
        if self.check_token_file():
            token = self.get_token()
            if token:
                ensure_future(self.response(token=token))

    def login(self, *args):
        self.ids.spinner.active = True
        username_or_email = self.ids.username_or_email.text
        password = self.ids.password.text

        if not username_or_email:
            self.ids.spinner.active = False
            self.ids.error.text = (
                "[color=e01c37]Введите имя или электронную почту[/color]"
            )
            return

        elif not password:
            self.ids.spinner.active = False
            self.ids.error.text = "[color=e01c37]Введите пароль[/color]"
            return

        elif not self.validate_username(username_or_email) and not self.validate_email(
            username_or_email
        ):
            self.ids.spinner.active = False
            self.ids.error.text = (
                "[color=e01c37]Некорректноея имя пользователя или почта[/color]"
            )
            return

        ensure_future(
            self.response(username_or_email=username_or_email, password=password)
        )

    async def response(self, token=None, username_or_email=None, password=None):
        self.ids.spinner.active = True
        self.ids.username_or_email.disabled = True
        self.ids.password.disabled = True
        self.ids.login_button.disabled = True
        self.ids.screen_button.disabled = True
        self.ids.reset_button.disabled = True

        app = MDApp.get_running_app()

        try:
            async with AsyncClient(
                timeout=120, verify=False, proxies=self.proxies
            ) as client:
                if token:
                    response = await client.post(
                        url=f"{self.api}/accounts/signin/", json={"token": token}
                    )
                else:
                    response = await client.post(
                        url=f"{self.api}/accounts/signin/",
                        json={
                            "username_or_email": username_or_email,
                            "password": password,
                        },
                    )
                response.raise_for_status()
                if response.status_code == 200:
                    data = response.json()

                    access_token = data["access_token"].encode("utf-8")
                    with open(
                        os.path.join(self.env, "token.json"),
                        "wb",
                    ) as f:
                        encrypted_token = app.sha.encrypt(access_token)
                        f.write(encrypted_token)

                    app.username = data["user"]["username"]
                    app.email = data["user"]["email"] if data["user"]["email"] else ""
                    app.balance = data["user"]["balance"]
                    app.bearer = access_token

                    self.set_screen("main_screen")

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
            self.ids.username_or_email.disabled = False
            self.ids.password.disabled = False
            self.ids.login_button.disabled = False
            self.ids.screen_button.disabled = False
            self.ids.reset_button.disabled = False

            self.ids.password.text = ""
            Clock.schedule_once(lambda dt: setattr(self.ids.error, "text", ""), 10)
