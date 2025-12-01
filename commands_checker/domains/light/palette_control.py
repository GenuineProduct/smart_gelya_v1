# commands_checker/domains/light/palette_control.py
import json
from Gelya_voice import GelyaSpeach
from . import get_light_controller

gelya = GelyaSpeach()

class LightPaletteControl:
    def __init__(self):
        self.light_controller = get_light_controller()  # Используем единый экземпляр
        try:
            with open('responses.json', 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
        except FileNotFoundError:
            self.responses = {"positive_responses": ["хорошо", "сделано"]}
    
    def _get_random_response(self):
        import random
        responses = self.responses.get("positive_responses", ["хорошо"])
        return random.choice(responses)

    def set_palette_direct(self, palette_name):
        """Прямая установка палитры"""
        self.light_controller.set_palette(palette_name)

    def set_palette_from_text(self, text):
        """Установка палитры из текста (для совместимости)"""
        try:
            with open("commands_checker/config/commands_dict.json", encoding="utf-8") as f:
                data = json.load(f)
                palettes = data.get('palettes', {})
        except:
            palettes = {}
        
        for palette_ru, palette_en in palettes.items():
            if palette_ru in text.lower():
                if self.light_controller.set_palette(palette_ru):
                    return True
        return False