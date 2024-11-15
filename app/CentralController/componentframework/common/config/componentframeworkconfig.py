# config.py

class AppConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance.component_id = 'componentId'
        return cls._instance

    def set_component_id(self, component_id):
        self.component_id = component_id
