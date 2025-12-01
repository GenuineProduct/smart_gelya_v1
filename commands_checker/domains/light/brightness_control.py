# commands_checker/domains/light/brightness_control.py
import json
import re
from Gelya_voice import GelyaSpeach
from commands_checker.utils.voice_response import with_gelya_response
from . import get_light_controller

gelya = GelyaSpeach()

class LightBrightnessControl:
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

    def turn_on_light(self):
        """Включить свет"""
        self.light_controller.turn_on()
    
    def turn_off_light(self):
        """Выключить свет"""
        self.light_controller.turn_off()

    def increase_brightness(self, value=None):
        """Увеличить яркость"""
        self.light_controller.increase_brightness()
    
    def decrease_brightness(self):
        """Уменьшить яркость"""
        self.light_controller.decrease_brightness()
    
    def set_brightness_with_value(self, value):
        """Установить яркость с числовым значением"""
        if value is not None:
            # Ограничиваем диапазон
            brightness = max(0, min(100, value))
            self.light_controller.set_brightness(brightness)
        else:
            # Fallback на старый метод
            self.set_brightness_answer("")
    
    def set_brightness_answer(self, text):
        """Совместимость со старым кодом"""
        self._extract_brightness_from_text(text)
    
    def _extract_brightness_from_text(self, text):
        """Извлечение значения яркости из текста"""
        try:
            digits = re.findall(r'\d+', text)
            if digits:
                brightness = int(digits[0])
            else:
                brightness = self._word_to_number(text)
            
            # Ограничиваем диапазон
            if brightness is not None:
                brightness = max(0, min(100, brightness))
            
            return brightness
        except Exception as e:
            print(f"[ОШИБКА] Установка яркости: {e}")
            return None
    
    def _word_to_number(self, text):
        """Преобразование текста в число"""
        words = {
            "ноль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
            "шесть": 6, "семь": 7, "восемь": 8, "девять": 9,
            "десять": 10, "одиннадцать": 11, "двенадцать": 12,
            "тринадцать": 13, "четырнадцать": 14, "пятнадцать": 15,
            "шестнадцать": 16, "семнадцать": 17, "восемнадцать": 18,
            "девятнадцать": 19, "двадцать": 20, "тридцать": 30,
            "сорок": 40, "пятьдесят": 50, "шестьдесят": 60,
            "семьдесят": 70, "восемьдесят": 80, "девяносто": 90, "сто": 100
        }
        parts = text.lower().split()
        total = 0
        for word in parts:
            if word in words:
                total += words[word]
        return total if total > 0 else None
    
