# commands_checker/domains/music/playlists.py
import json
import os
from fuzzywuzzy import fuzz
from Gelya_voice import GelyaSpeach
from player import MusicPlayer
from config.config import PLAYLISTS_PATH

gelya = GelyaSpeach()

class MusicPlaylists:
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

    def switch_playlist(self, playlist_name):
        if not playlist_name:
            print("[ОШИБКА] Не указано название плейлиста")
            return False
            
        if playlist_name.lower() == "всякое":
            return self._switch_to_main_music()
        
        best_playlist = self._find_best_playlist_match(playlist_name)
        
        if not best_playlist:
            print(f"[ОШИБКА] Не удалось найти подходящий плейлист для: {playlist_name}")
            return False
            
        playlist_path = f"{PLAYLISTS_PATH}/{best_playlist}"
        
        # Переключаем плейлист
        player = MusicPlayer.get_instance()
        current_volume = player.get_volume()
        player.stop_update_loop()
        player.stop()
        
        new_player = MusicPlayer(playlist_path)
        new_player.set_volume(current_volume * 100)
        
        new_player.play()
        return True

    def create_playlist(self, playlist_name):
        try:
            folder_path = f"{PLAYLISTS_PATH}/{playlist_name}"
            os.makedirs(folder_path, exist_ok=True)
            print(f"Создан плейлист: {playlist_name}")
            return True
        except Exception as e:
            print(f"Ошибка создания плейлиста: {e}")
            return False

    def _find_best_playlist_match(self, requested_name):
        """Продвинутый поиск плейлиста"""
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
        
        for playlist, score, strategy in strategies:
            print(f"[PLAYLIST] {strategy}: '{playlist}' ({score}%)")
        
        if strategies:
            best_playlist, best_score, strategy = strategies[0]
            print(f"[PLAYLIST] ✅ Выбран: '{best_playlist}' ({best_score}%, {strategy})")
            return best_playlist
        
        print(f"[PLAYLIST] ❌ Не найдено подходящих плейлистов для: {requested_name}")
        return None
    
    def _switch_to_main_music(self):
        player = MusicPlayer.get_instance()
        current_volume = player.get_volume()
        player.stop_update_loop()
        player.stop()
        
        try:
            new_player = MusicPlayer(f"{PLAYLISTS_PATH}/всякое")
            new_player.set_volume(current_volume * 100)
            new_player.play()
            return True
        except Exception as e:
            print(f"[DEBUG] Ошибка в switch_to_main_music: {e}")
            return False