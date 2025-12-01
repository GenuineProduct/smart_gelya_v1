# commands_checker/domains/music/playback.py
import json
from Gelya_voice import GelyaSpeach
from player import MusicPlayer

gelya = GelyaSpeach()

class MusicPlayback:
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
        player = MusicPlayer.get_instance()
        if player.paused:
            player.resume()
        else:
            player.play()

    def pause_music(self):
        player = MusicPlayer.get_instance()
        player.pause()

    def resume_music(self):
        player = MusicPlayer.get_instance()
        player.resume()

    def next_track(self):
        player = MusicPlayer.get_instance()
        player.next_track()

    def prev_track(self):
        player = MusicPlayer.get_instance()
        player.prev_track()

    def toggle_repeat(self):
        player = MusicPlayer.get_instance()
        state = player.toggle_repeat()
        # Без озвучки - нейросеть сама сгенерирует ответ
        print(f"[MUSIC] Режим повтора: {'ВКЛ' if state else 'ВЫКЛ'}")