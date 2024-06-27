"""Crit screen"""

from asyncio import run
from httpx import AsyncClient
from kivy.metrics import sp, dp
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color


class OverMain(ScrollView):
    def __init__(self, error, api, proxies, **kwargs):
        super(OverMain, self).__init__(**kwargs)
        self.api = api
        self.proxies = proxies

        print(error)

        with self.canvas.before:
            self.bg_color = Color(0, 0, 0, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        error_message = error.splitlines()[-1]
        trace = error.splitlines()[:-1]

        boxlayout = BoxLayout(size_hint_y=None)
        boxlayout.bind(minimum_height=boxlayout.setter("height"))

        label = Label(
            text="Произошла критическая ошибка. Перезапустите приложение. Разработчик исправит это в следующей версии, а пока что - sorry not sorry.\nПо всем вопросам обращаться на: [b]kynvi.staff@gmail.com[/b]",
            font_size=sp(16),
            size_hint_y=None,
            markup=True,
            padding=[dp(5), dp(5)],
        )

        label.bind(
            width=lambda *x: label.setter("text_size")(label, (label.width, None)),
            texture_size=lambda *x: label.setter("height")(
                label, label.texture_size[1]
            ),
        )

        boxlayout.add_widget(label)
        self.add_widget(boxlayout)

        run(self.log(error_message=error_message, traceback="".join(trace)))

    def _update_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    async def log(self, error_message, traceback):
        params = {"error_message": error_message, "traceback": traceback}
        async with AsyncClient(
            timeout=120, verify=False, proxies=self.proxies
        ) as session:
            await session.post(f"{self.api}/log/", json=params)
