# commands_checker/domains/music/volume.py
import json
import re
from Gelya_voice import GelyaSpeach
from player import MusicPlayer

gelya = GelyaSpeach()

class MusicVolume:
    def __init__(self):
        try:
            with open('responses.json', 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
        except FileNotFoundError:
            self.responses = {"positive_responses": ["хорошо", "сделано"]}
    
    def _get_random_response(self):
        import random
        responses = self.responses.get("positive_responses", ["хорошо"])
        return random.choice(responses)

    def increase_volume(self, value=None):
        """Увеличить громкость на значение или по умолчанию"""
        if value is not None:
            # Увеличить на конкретное значение
            player = MusicPlayer.get_instance()
            current_volume = player.get_volume() * 100
            new_volume = min(current_volume + value, 100)
            player.set_volume(new_volume)
            response_text = f"Громкость увеличена на {value}%"
        else:
            # Стандартное увеличение на 10%
            player = MusicPlayer.get_instance()
            player.increase_volume()
        
        
    def decrease_volume(self, value=None):
        """Уменьшить громкость на значение или по умолчанию"""
        if value is not None:
            # Уменьшить на конкретное значение
            player = MusicPlayer.get_instance()
            current_volume = player.get_volume() * 100
            new_volume = max(current_volume - value, 0)
            player.set_volume(new_volume)
            response_text = f"Громкость уменьшена на {value}%"
        else:
            # Стандартное уменьшение на 10%
            player = MusicPlayer.get_instance()
            player.decrease_volume()
        

    def set_volume_with_value(self, value):
        """Установка громкости с числовым значением"""
        if value is not None:
            player = MusicPlayer.get_instance()
            player.set_volume(value)
        else:
            # Fallback на старый метод если значение не передано
            self.set_volume_answer("")

    def set_volume_answer(self, text):
        """Совместимость со старым кодом"""
        volume = self._extract_volume_from_text(text)
        player = MusicPlayer.get_instance()
        player.set_volume(volume)
    
    def _extract_volume_from_text(self, text):
        """Извлечение значения громкости из текста"""
        try:
            digits = re.findall(r'\d+', text)
            if digits:
                volume = int(digits[0])
            else:
                volume = self._word_to_number(text)
            return volume 
        except Exception as e:
            print(f"[ОШИБКА] Установка громкости: {e}")
            return 50
    
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
        return total if total > 0 else 50