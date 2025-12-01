# commands_checker/domains/light/effect_control.py
from commands_checker.utils.voice_response import with_gelya_response
from Gelya_voice import GelyaSpeach
from . import get_light_controller

gelya = GelyaSpeach()

class LightEffectControl:
    def __init__(self):
        self.light_controller = get_light_controller()
    
    @with_gelya_response
    def start_music_mode(self):
        """Запустить светомузыку"""
        self.light_controller.start_music_mode()
        
    @with_gelya_response
    def start_wave_effect(self):
        """Запустить эффект волны"""
        self.light_controller.start_wave_effect()
        
    @with_gelya_response
    def start_breathing_effect(self):
        """Запустить эффект дыхания"""
        self.light_controller.start_breathing_effect()
        
    @with_gelya_response
    def start_monitor_mode(self):
        """Запустить умную подсветку"""
        self.light_controller.start_monitor_checker()
        
    @with_gelya_response
    def set_static_mode(self):
        """Вернуться к статичному свету"""
        self.light_controller.stop_music_mode()
        self.light_controller.stop_monitor_checker()
        self.light_controller.current_mode = "static"