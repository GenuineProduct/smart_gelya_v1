import os
import re
import json
from player import MusicPlayer
from Gelya_voice import GelyaSpeach
from .voice_response import with_gelya_response
from fuzzywuzzy import fuzz
from . import player
from config.config import PLAYLISTS_PATH
# Глобальный плеер
gelya = GelyaSpeach()

class MusicCommands:
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

    def play_music(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        if player.paused:
            player.resume()
        else:
            player.play()

    def stop_music(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.stop()

    def pause_music(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.pause()

    def resume_music(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.resume()

    def next_track(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.next_track()

    def prev_track(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.prev_track()

    def increase_volume(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.increase_volume()

    def decrease_volume(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.decrease_volume()

    def toggle_repeat(self):
        state = player.toggle_repeat()
        if state:
            with_gelya_response(lambda: gelya.speach("включаю повтор"))()
        else:
            with_gelya_response(lambda: gelya.speach("выключаю повтор"))()

    def word_to_number(self, text):
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

    def increase_volume(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        player.increase_volume()
    
    def set_volume_answer(self, text):
        volume = self.set_volume_from_text(text)
        with_gelya_response(lambda:gelya.speach(f"Громкость {volume} установлена"))()
        player.set_volume(volume)
    
    def set_volume_from_text(self, text):
        try:
            digits = re.findall(r'\d+', text)
            if digits:
                volume = int(digits[0])
            else:
                volume = self.word_to_number(text)
            return volume 
        except Exception as e:
            print(f"[ОШИБКА] Установка громкости: {e}")
        

    def switch_playlist(self, playlist_name):
        global player
        
        if not playlist_name:
            print("[ОШИБКА] Не указано название плейлиста")
            with_gelya_response(lambda: gelya.speach("Не указано название плейлиста"))()
            return False
            
        if playlist_name.lower() == "всякое":
            return self.switch_to_main_music()
        
        best_playlist = self._find_best_playlist_match(playlist_name)
        
        if not best_playlist:
            print(f"[ОШИБКА] Не удалось найти подходящий плейлист для: {playlist_name}")
            with_gelya_response(lambda: gelya.speach(f"Плейлист {playlist_name} не найден"))()
            return False
            
        playlist_path = f"{PLAYLISTS_PATH}/{best_playlist}"
        
        # Переключаем плейлист
        current_volume = player.get_volume()
        player.stop_update_loop()
        player.stop()
        
        player = MusicPlayer(playlist_path)
        player.set_volume(current_volume * 100)
        
        with_gelya_response(lambda: gelya.speach(f"Включаю плейлист {best_playlist}"))()
        player.play()
        return True

    def _find_best_playlist_match(self, requested_name):
        """Продвинутый поиск плейлиста с детальным логированием"""
        playlists_path = PLAYLISTS_PATH
        
        if not os.path.exists(playlists_path):
            print("[PLAYLIST] ❌ Папка плейлистов не найдена")
            return None
            
        all_playlists = [d for d in os.listdir(playlists_path) 
                        if os.path.isdir(os.path.join(playlists_path, d))]
        
        print(f"[PLAYLIST] Доступные плейлисты: {all_playlists}")
        
        if not all_playlists:
            print("[PLAYLIST] ❌ Нет доступных плейлистов")
            return None
        
        requested_lower = requested_name.lower()
        strategies = []
        
        # Собираем все возможные совпадения с оценками
        for playlist in all_playlists:
            playlist_lower = playlist.lower()
            
            # Точное совпадение
            if playlist_lower == requested_lower:
                strategies.append((playlist, 100, "exact"))
            
            # Частичное вхождение
            elif requested_lower in playlist_lower:
                strategies.append((playlist, 90, "partial_in"))
            elif playlist_lower in requested_lower:
                strategies.append((playlist, 85, "partial_contains"))
            
            # Fuzzy совпадение
            else:
                score = fuzz.ratio(requested_lower, playlist_lower)
                if score >= 50:
                    strategies.append((playlist, score, "fuzzy"))
        
        # Сортируем по убыванию оценки
        strategies.sort(key=lambda x: x[1], reverse=True)
        
        # Логируем все варианты
        for playlist, score, strategy in strategies:
            print(f"[PLAYLIST] {strategy}: '{playlist}' ({score}%)")
        
        # Возвращаем лучший вариант
        if strategies:
            best_playlist, best_score, strategy = strategies[0]
            print(f"[PLAYLIST] ✅ Выбран: '{best_playlist}' ({best_score}%, {strategy})")
            return best_playlist
        
        print(f"[PLAYLIST] ❌ Не найдено подходящих плейлистов для: {requested_name}")
        return None
    
    def switch_to_main_music(self):
        global player
        
        current_volume = player.get_volume()
        player.stop_update_loop()
        player.stop()
        
        try:
            player = MusicPlayer(f"{PLAYLISTS_PATH}/всякое")
            player.set_volume(current_volume * 100)
            with_gelya_response(lambda: gelya.speach("включаю музыку"))()
            player.play()
            return True
        except Exception as e:
            print(f"[DEBUG] Ошибка в switch_to_main_music: {e}")
            return False

    def create_playlist(self, playlist_name):
        try:
            folder_path = f"{PLAYLISTS_PATH}/{playlist_name}"
            os.makedirs(folder_path, exist_ok=True)
            print(f"Создан плейлист: {playlist_name}")
            with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
            return True
        except Exception as e:
            print(f"Ошибка создания плейлиста: {e}")
            return False