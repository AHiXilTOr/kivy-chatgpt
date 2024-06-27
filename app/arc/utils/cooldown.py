from kivy.clock import Clock

def with_cooldown(cooldown_duration):
    last_called = 0

    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal last_called
            current_time = Clock.get_time()
            if current_time - last_called < cooldown_duration:
                return
            last_called = current_time
            return func(*args, **kwargs)
        return wrapper
    return decorator