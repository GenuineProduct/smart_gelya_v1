# player.py
import pygame
import os
import random
import time
import traceback
import threading


class MusicPlayer:
    def __init__(self, music_folder):
        pygame.mixer.init()
        self.music_folder = music_folder
        self.tracklist = self.load_tracks()
        self.track_index = 0
        self.playing = False
        self.paused = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        self._update_thread = None
        self._stop_thread = False
        self.repeat_mode = False
        self.shuffle_mode = True
        

    def load_tracks(self):
        tracks = [file for file in os.listdir(self.music_folder) if file.endswith(".mp3")]
        random.shuffle(tracks)
        return tracks

    def play(self):
        if not self.tracklist:
            print("[ОШИБКА] Нет треков в папке.")
            return
        if self.paused:
            self.resume()
        else:
            track_path = os.path.join(self.music_folder, self.tracklist[self.track_index])
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.playing = True
            self.paused = False
            print(f"[INFO] Воспроизведение: {self.tracklist[self.track_index]}")
            self.start_update_loop()

    def start_update_loop(self):
        """Запускает фоновый поток для мониторинга окончания треков"""
        if self._update_thread and self._update_thread.is_alive():
            return
            
        self._stop_thread = False
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()

    def _update_loop(self):
        """Непрерывно проверяет окончание трека"""
        while not self._stop_thread:
            time.sleep(1)
            if not pygame.mixer.music.get_busy() and self.playing and not self.paused:
                if self.repeat_mode:
                    print("Повтор текущего трека...")
                    track_path =  os.path.join(self.music_folder, self.tracklist[self.track_index])
                    pygame.mixer.music.load(track_path)
                    pygame.mixer.music.play()
                else:
                    print("[INFO] Трек завершился, переходим к следующему...")
                    self.next_track()
            elif self._stop_thread:
                break
            
    def stop_update_loop(self):
        """Останавливает фоновый поток мониторинга"""
        self._stop_thread = True
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1.0)
        
        
    def stop(self):
        self._stop_thread = True
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.paused = True
            print("[INFO] Музыка на паузе.")

    def resume(self):
        if self.paused:
            pygame.mixer.music.unpause()
            pygame.mixer.music.set_volume(self.volume)
            self.paused = False
            self.playing = True
            print("[INFO] Возобновлено воспроизведение.")

    def next_track(self):
        try:
            self.track_index = (self.track_index + 1) % len(self.tracklist)
            track_path = os.path.join(self.music_folder, self.tracklist[self.track_index])
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            print(f"[INFO] Следующий трек: {self.tracklist[self.track_index]}")
        except Exception as e:
            print(f"[ERROR] Ошибка при переходе к следующему треку: {e}")
            traceback.print_exc()

    def prev_track(self):
        try:
            self.track_index = (self.track_index - 1) % len(self.tracklist)
            track_path = os.path.join(self.music_folder, self.tracklist[self.track_index])
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            print(f"[INFO] Предыдущий трек: {self.tracklist[self.track_index]}")
        except Exception as e:
            print(f"[ERROR] Ошибка при переходе к предыдущему треку: {e}")
            traceback.print_exc()
            
    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def increase_volume(self):
        self.volume = min(self.volume + 0.1, 1.0)
        pygame.mixer.music.set_volume(self.volume)
        print(f"[INFO] Громкость: {int(self.volume * 100)}%")

    def decrease_volume(self):
        self.volume = max(self.volume - 0.1, 0.0)
        pygame.mixer.music.set_volume(self.volume)
        print(f"[INFO] Громкость: {int(self.volume * 100)}%")

    def set_volume(self, value):
        self.volume = max(0.0, min(value / 100, 1.0))
        pygame.mixer.music.set_volume(self.volume)
        print(f"[INFO] Громкость установлена: {int(self.volume * 100)}%")

    def get_volume(self):
        return self.volume
    
    def toggle_repeat(self):
        self.repeat_mode = not self.repeat_mode
        if self.repeat_mode:
            status = "ВКЛ"
            print (f"[INFO] Режим повтора: {status}")
        else:
            status =  "ВЫКЛ"
            print (f"[INFO] Режим повтора: {status}")
        return self.repeat_mode
    
    def set_repeat(self, state: bool):
        self.repeat_mode = state
        if self.repeat_mode:
            status = "ВКЛ"
            print (f"[INFO] Режим повтора: {status}")
        else:
            status = "ВЫКЛ"
            print (f"[INFO] Режим повтора: {status}")
        return self.repeat_mode
    
    def is_repeating(self):
        return self.repeat_mode
    
    def load_playlist(self, music_folder):
        """Загружает новый плейлист"""
        try:
            self.stop_update_loop()
            self.stop()
            
            self.music_folder = music_folder
            self.tracklist = self.load_tracks()
            self.track_index = 0
            
            print(f"[INFO] Загружен плейлист: {music_folder}")
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка загрузки плейлиста: {e}")
            return False
    
    @classmethod
    def get_instance(cls):
        """Получить глобальный экземпляр плеера"""
        from . import get_player_instance
        return get_player_instance()