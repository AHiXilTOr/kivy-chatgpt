import os
from configparser import ConfigParser

config = ConfigParser()
path = os.path.dirname(__file__)


def read_config(section, key, default, path):
    try:
        config.read(os.path.join(path, "config.ini"))

        if not config.has_section(section) or not config.has_option(section, key):
            save_config(section, key, default, path)
            return default

        value = config.get(section, key)

        return value

    except Exception as e:
        print(f"Ошибка при чтении конфигурации {section} {key} {default}: {e}")
        return None


def save_config(section, key, value, path):
    try:
        config.read(os.path.join(path, "config.ini"))

        if not config.has_section(section):
            config.add_section(section)

        config.set(section, key, value)

        with open(os.path.join(path, "config.ini"), "w") as configfile:
            config.write(configfile)

    except Exception as e:
        print(f"Ошибка при сохранении конфигурации {section} {key} {value}: {e}")
