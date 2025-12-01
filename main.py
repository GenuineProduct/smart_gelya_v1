# main.py (исправленная версия)
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from fuzzywuzzy import fuzz
from Gelya_voice import GelyaSpeach
from commands_checker import SmartCommandHandler
import asyncio
from angelina.config.config import BOT_TOKEN
from bot_module import YouTubeBot
import threading
import time

# Импортируем и инициализируем плеер ДО создания ассистента
from player import set_player_instance
from config.config import PLAYLISTS_PATH
from player.player import MusicPlayer

class AngelinaAssistient:
    
    def __init__(self):
        self.gelya = GelyaSpeach()
        
        # Инициализируем плеер перед созданием command_handler
        self._initialize_player()
        
        # Используем новый SmartCommandHandler с Ollama
        self.command_handler = SmartCommandHandler(ollama_model="llama3")

        self.model = Model('vosk-model-small-ru-0.22')
        self.rec = KaldiRecognizer(self.model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        self.stream.start_stream()

    def _initialize_player(self):
        """Инициализирует глобальный экземпляр плеера"""
        try:
            from player import get_player_instance
            if get_player_instance() is None:
                player_instance = MusicPlayer(f"{PLAYLISTS_PATH}/всякое")
                set_player_instance(player_instance)
                print("[PLAYER] Глобальный плеер инициализирован")
            else:
                print("[PLAYER] Плеер уже инициализирован")
        except Exception as e:
            print(f"[ERROR] Ошибка инициализации плеера: {e}")

    def listen(self):
        try:
            while True:
                data = self.stream.read(4000, exception_on_overflow=False)  
                if self.rec.AcceptWaveform(data) and len(data) > 0:
                    answer = json.loads(self.rec.Result())
                    if answer['text']:
                        yield answer['text']
        except Exception as e:
            print(f"[CRITICAL] Ошибка в loop: {e}")

    def angelina(self):
        self.gelya.speach("Привет! Я ангелина, твой голосовой помошник")
        while True:
            for text in self.listen():
                print(f"You say: {text}")
                if fuzz.ratio(text.split()[0], "геля") > 45 or fuzz.ratio(text.split()[0], "ангелина") > 45:
                    my_text = text.split()[1:]
                    my_say = " ".join(my_text).strip()
                    print("log:", my_say)
                    self.command_handler.process_command(my_say)

async def start_bot():
    try:
        bot = YouTubeBot(BOT_TOKEN)
        print("Telegram bot starting...")
        await bot.start()
    except Exception as e:
        print(f"[BOT ERROR] {e}")

def run_bot():
    """Запуск бота в отдельном event loop"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_bot())
    except Exception as e:
        print(f"[BOT THREAD ERROR] {e}")

def main():
    assistant = AngelinaAssistient()
    
    if BOT_TOKEN:
        print("[INFO] Запускаю Telegram бота в отдельном потоке...")
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        time.sleep(2)
        print("[INFO] Telegram бот запущен")
    else:
        print("[INFO] Telegram бот не запущен (BOT_TOKEN не найден)")
        
    try:
        assistant.angelina()
    except KeyboardInterrupt:
        print("\n[INFO] Завершение работы...")
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")

if __name__ == "__main__":
    main()