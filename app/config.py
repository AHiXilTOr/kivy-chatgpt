from configparser import ConfigParser

config = ConfigParser()

def read_config(section, key):
    try:
        config.read('config.ini')
        
        if not config.has_section(section) or not config.has_option(section, key):
            save_config(section, key, "")
            return False
        
        value = config.get(section, key)
        return value
    
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}")
        return None

def save_config(section, key, value):
    try:
        config.read('config.ini')
        
        if not config.has_section(section):
            config.add_section(section)
        
        config.set(section, key, value)
        
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")
