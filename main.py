__version__ = "1.0"

if __name__ == '__main__':
        
    try:
        from app.body import ChatBotApp
        import asyncio, httpx
        from env import API, PROXY

        '''
        Синхронный запуск
        ChatBotApp().run()
        '''
        
        '''Асинхронный запуск'''
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ChatBotApp().async_run())
        loop.close()

    except: 
        '''Запуск второго экрана'''
        import traceback
        from kivy.app import runTouchApp
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.scrollview import ScrollView
        from kivy.metrics import sp

        '''Запись ошибки остановившей работу приложения'''
        async def log(error_message, traceback):
            payload = {"error_message": error_message, "traceback": traceback}
            
            async with httpx.AsyncClient(timeout=120, verify=False, proxy=PROXY) as session:
                r = await session.post(f"{API}/log/", json=payload)
                r.raise_for_status()

        error = traceback.format_exc()
        error_message = error.splitlines()[-1]
        trace = traceback.format_exc().splitlines()[:-1]

        asyncio.run(log(error_message, "".join(trace)))
        
        scrollview = ScrollView()

        boxlayout = BoxLayout(size_hint_y=None)
        boxlayout.bind(minimum_height=boxlayout.setter('height'))

        def update(instance, value):
            instance.text_size[0] = boxlayout.size[0]
            instance.texture_update()
            instance.size = instance.texture_size
            
        label = Label(text=error, font_size=sp(14), size_hint=(None, None))
        label.bind(pos=update)
        
        boxlayout.add_widget(label)
        scrollview.add_widget(boxlayout)
        
        runTouchApp(scrollview)