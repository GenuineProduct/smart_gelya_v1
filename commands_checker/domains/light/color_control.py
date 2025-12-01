# commands_checker/domains/light/color_control.py
from . import get_light_controller

class LightColorControl:
    def __init__(self):
        self.light_controller = get_light_controller()  # Используем общий экземпляр
    
    def set_color_direct(self, color_name):
        """Прямая установка цвета"""
        return self.light_controller.set_color(color_name)