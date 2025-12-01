# commands_checker/core/command_handler.py
import threading
from .mixed_processor import MixedRequestProcessor
from ..domains.music.playback import MusicPlayback
from ..domains.music.volume import MusicVolume
from ..domains.music.playlists import MusicPlaylists
from ..domains.system.browser import SystemBrowser
from ..domains.system.search import SystemSearch
from ..domains.system.power import SystemPower
from ..domains.light.color_control import LightColorControl
from ..domains.light.brightness_control import LightBrightnessControl
from ..domains.light.effect_control import LightEffectControl
from ..domains.light.palette_control import LightPaletteControl
from ..utils.voice_response import with_gelya_response
from Gelya_voice import GelyaSpeach

gelya = GelyaSpeach()

class SmartCommandHandler:
    def __init__(self, ollama_model="llama3"):
        # Инициализация доменов
        self.music_playback = MusicPlayback()
        self.music_volume = MusicVolume()
        self.music_playlists = MusicPlaylists()
        self.system_browser = SystemBrowser()
        self.system_search = SystemSearch()
        self.system_power = SystemPower()
        self.light_color = LightColorControl()
        self.light_brightness = LightBrightnessControl()
        self.light_effects = LightEffectControl()
        self.light_palettes = LightPaletteControl()
        
        # Умный процессор
        self.mixed_processor = MixedRequestProcessor(ollama_model)
        
        self.last_processed = ""
        
    def process_command(self, my_say):
        """Обрабатывает любые фразы"""
        my_say = my_say.lower().strip()
        
        # Защита от повторов
        if my_say == self.last_processed:
            return
        self.last_processed = my_say
        
        print(f"[USER INPUT] '{my_say}'")
        
        try:
            # Анализируем запрос
            result = self.mixed_processor.process_mixed_request(my_say)
            print(f"[MIXED RESULT] {result}")
            
            # Выполняем команды если есть
            if result.get("commands"):
                for command in result["commands"]:
                    self._execute_simple_command(command, result.get("parameters", {}))
            
            # Озвучиваем ответ
            if result.get("response"):
                self._speak_with_gelya_response(result["response"])
                
        except Exception as e:
            print(f"[ОШИБКА] {e}")
    
    def _execute_simple_command(self, command_key, parameters=None):
        """Выполняет команду с параметрами"""
        if parameters is None:
            parameters = {}
        
        command_map = {
            # Музыка
            "play": self.music_playback.play_music,
            "pause": self.music_playback.pause_music,
            "resume": self.music_playback.resume_music,
            "next": self.music_playback.next_track,
            "previous": self.music_playback.prev_track,
            "repeat": self.music_playback.toggle_repeat,
            "volume_up": self.music_volume.increase_volume,
            "volume_down": self.music_volume.decrease_volume,
            "set_volume": lambda: self.music_volume.set_volume_with_value(parameters.get("value")),
            
            # Свет - основные
            "light_on": self.light_brightness.turn_on_light,
            "light_off": self.light_brightness.turn_off_light,
            "brightness_up": self.light_brightness.increase_brightness,
            "brightness_down": self.light_brightness.decrease_brightness,
            "set_brightness": lambda: self.light_brightness.set_brightness_with_value(parameters.get("value")),
            
            # Свет - эффекты
            "music_mode": self.light_effects.start_music_mode,
            "wave_effect": self.light_effects.start_wave_effect,
            "breathing_effect": self.light_effects.start_breathing_effect,
            "monitor_mode": self.light_effects.start_monitor_mode,
            "static_mode": self.light_effects.set_static_mode,
            
            # Свет - цвета
            "set_color_white": lambda: self.light_color.set_color_direct("белый"),
            "set_color_red": lambda: self.light_color.set_color_direct("красный"),
            "set_color_green": lambda: self.light_color.set_color_direct("зеленый"),
            "set_color_blue": lambda: self.light_color.set_color_direct("синий"),
            "set_color_yellow": lambda: self.light_color.set_color_direct("желтый"),
            "set_color_purple": lambda: self.light_color.set_color_direct("фиолетовый"),
            "set_color_cyan": lambda: self.light_color.set_color_direct("голубой"),
            "set_color_orange": lambda: self.light_color.set_color_direct("оранжевый"),
            "set_color_turquoise": lambda: self.light_color.set_color_direct("бирюзовый"),
            "set_color_pink": lambda: self.light_color.set_color_direct("розовый"),
            "set_color_mint": lambda: self.light_color.set_color_direct("мятный"),
            "set_color_lavender": lambda: self.light_color.set_color_direct("лавандовый"),
            
            # Свет - палитры
            "set_palette_cold": lambda: self.light_palettes.set_palette_direct("холодная"),
            "set_palette_lamp": lambda: self.light_palettes.set_palette_direct("ламповая"),
            "set_palette_warm": lambda: self.light_palettes.set_palette_direct("теплые"),
            "set_palette_minty": lambda: self.light_palettes.set_palette_direct("мятная"),
            "set_palette_velvet": lambda: self.light_palettes.set_palette_direct("бархатная"),
            
            # Система
            "browser": self.system_browser.open_browser,
            "search": lambda: self.system_search.search(parameters.get("search_query", "")),
            "shutdown": self.system_power.shutdown_computer,
            
            # Плейлисты
            "switch_playlist": lambda: self.music_playlists.switch_playlist(parameters.get("playlist_name", "")),
            "create_playlist": lambda: self.music_playlists.create_playlist(parameters.get("playlist_name", "")),
        }
        
        if command_key in command_map:
            print(f"[COMMAND] Выполняю: {command_key} с параметрами: {parameters}")
            threading.Thread(target=command_map[command_key]).start()
        else:
            print(f"[WARNING] Неизвестная команда: {command_key}")
    
    def _speak_with_gelya_response(self, response_text):
        """Озвучивает ответ через with_gelya_response"""
        from ..utils.voice_response import with_gelya_response
        
        def speak():
            try:
                gelya.speach(response_text)
            except Exception as e:
                print(f"❌ Ошибка TTS: {e}")
        
        with_gelya_response(speak)()