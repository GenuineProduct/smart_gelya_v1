import json
import re
from Gelya_voice import GelyaSpeach
from .voice_response import with_gelya_response
from light.light_controller import LightController

gelya = GelyaSpeach()

class LightCommands:
    def __init__(self):
        self.light_controller = LightController()
        
        try:
            with open('responses.json', 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
        except FileNotFoundError:
            self.responses = {"positive_responses": ["хорошо", "сделано"]}
    
    def _get_random_response(self):
        import random
        responses = self.responses.get("positive_responses", ["хорошо"])
        return random.choice(responses)
    
    def word_to_number(self, text):
        """Парсит текстовое представление числа (аналогично music_commands)"""
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

    def turn_on_light(self):
        """Включить свет"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.turn_on()
    
    def turn_off_light(self):
        """Выключить свет"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.turn_off()
    
    def increase_brightness(self):
        """Увеличить яркость"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.increase_brightness()
    
    def decrease_brightness(self):
        """Уменьшить яркость"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.decrease_brightness()
    
    def set_brightness_answer(self, text):
        """Установить яркость с голосовым ответом (аналогично set_volume_answer)"""
        brightness = self.set_brightness_from_text(text)
        if brightness is not None:
            with_gelya_response(lambda: gelya.speach(f"Яркость {brightness} установлена"))()
            self.light_controller.set_brightness(brightness)
        else:
            with_gelya_response(lambda: gelya.speach("Не удалось установить яркость"))()
    
    def set_brightness_from_text(self, text):
        """Извлечь значение яркости из текста (аналогично set_volume_from_text)"""
        try:
            digits = re.findall(r'\d+', text)
            if digits:
                brightness = int(digits[0])
            else:
                brightness = self.word_to_number(text)
            
            # Ограничиваем диапазон
            if brightness is not None:
                brightness = max(0, min(100, brightness))
            
            return brightness
        except Exception as e:
            print(f"[ОШИБКА] Установка яркости: {e}")
            return None
    
    def set_color_from_text(self, text):
        """Установить цвет из текста"""
        # Загружаем словарь цветов
        try:
            with open(r"angelina\commands_checker\commands_dict.json", encoding="utf-8") as f:
                data = json.load(f)
                colors = data.get('light_colors', {})
        except:
            colors = {}
        
        # Ищем цвет в тексте
        for color_ru, color_en in colors.items():
            if color_ru in text.lower():
                if self.light_controller.set_color(color_ru):
                    with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
                    return True
        
        with_gelya_response(lambda: gelya.speach("не нашла такой цвет"))()
        return False
    
    def set_palette_from_text(self, text):
        """Установить палитру из текста"""
        # Загружаем словарь палитр
        try:
            with open(r"angelina\commands_checker\commands_dict.json", encoding="utf-8") as f:
                data = json.load(f)
                palettes = data.get('light_palettes', {})
        except:
            palettes = {}
        
        # Ищем палитру в тексте
        for palette_ru, palette_en in palettes.items():
            if palette_ru in text.lower():
                if self.light_controller.set_palette(palette_ru):
                    with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
                    return True
        
        with_gelya_response(lambda: gelya.speach("не нашла такую палитру"))()
        return False
    
    def start_music_mode(self):
        """Запустить светомузыку"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.start_music_mode()
    
    def start_wave_effect(self):
        """Запустить эффект волны"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.start_wave_effect()
    
    def start_breathing_effect(self):
        """Запустить эффект дыхания"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.start_breathing_effect()
    
    def start_monitor_mode(self):
        """Запустить умную подсветку"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.start_monitor_checker()
    
    def set_static_mode(self):
        """Вернуться к статичному свету"""
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        self.light_controller.stop_music_mode()
        self.light_controller.stop_monitor_checker()
        self.light_controller.current_mode = "static"
        
    def set_color_direct(self, color_name):
        """Прямая установка цвета (без поиска в тексте)"""
        if self.light_controller.set_color(color_name):
            with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
            return True
        else:
            with_gelya_response(lambda: gelya.speach("не нашла такой цвет"))()
            return False

    def set_palette_direct(self, palette_name):
        """Прямая установка палитры (без поиска в тексте)"""
        if self.light_controller.set_palette(palette_name):
            with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
            return True
        else:
            with_gelya_response(lambda: gelya.speach("не нашла такую палитру"))()
            return False