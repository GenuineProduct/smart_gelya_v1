import threading
import json
import re
from fuzzywuzzy import fuzz
from .music_commands import MusicCommands
from .system_commands import SystemCommands
from .light_commands import LightCommands

class CommandHandler:
    def __init__(self):
        self.music_commands = MusicCommands()
        self.system_commands = SystemCommands()
        self.light_commands = LightCommands()
        
    def _load_commands_data(self):
        """Загружает данные команд из JSON"""
        try:
            with open(r"angelina\commands_checker\commands_dict.json", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ОШИБКА] Чтение commands_dict.json: {e}")
            return {}
    
    def _find_command_key(self, text):
        """Улучшенная логика с расширенным fuzzy поиском"""
        text_lower = text.lower().strip()
        print(f"[DEBUG] Ищем команду для: '{text_lower}'")
        
        if not text_lower:
            return None
            
        commands_data = self._load_commands_data()
        
        # 1. Проверяем action_patterns (включи свет, выключи свет и т.д.)
        if 'action_patterns' in commands_data:
            command_key = self._check_action_patterns(text_lower, commands_data['action_patterns'])
            if command_key:
                return command_key
        
        # 2. Проверяем parameter_commands (яркость 50, громкость 100)
        if 'parameter_commands' in commands_data:
            command_key = self._check_parameter_commands(text_lower, commands_data['parameter_commands'])
            if command_key:
                return command_key
        
        # 3. Проверяем direct_commands (ярче, громче, пауза и т.д.)
        if 'direct_commands' in commands_data:
            command_key = self._check_direct_commands(text_lower, commands_data['direct_commands'])
            if command_key:
                return command_key
        
        # 4. Проверяем цвета
        if 'colors' in commands_data:
            command_key = self._check_colors(text_lower, commands_data['colors'])
            if command_key:
                return command_key
        
        # 5. Проверяем палитры
        if 'palettes' in commands_data:
            command_key = self._check_palettes(text_lower, commands_data['palettes'])
            if command_key:
                return command_key
        
        # 6. Улучшенный fuzzy поиск
        return self._improved_fuzzy_search(text_lower, commands_data)

    def _check_action_patterns(self, text_lower, action_patterns):
        """Улучшенная проверка action_patterns"""
        for action, objects in action_patterns.items():
            if action in text_lower:
                print(f"[DEBUG] Найдено действие: '{action}'")
                for obj, command_key in objects.items():
                    # Более гибкая проверка объекта
                    if obj in text_lower:
                        print(f"[DEBUG] ✅ Action pattern: '{action} {obj}' -> '{command_key}'")
                        return command_key
                    # Fuzzy проверка для объекта
                    else:
                        obj_score = fuzz.partial_ratio(obj, text_lower)
                        if obj_score >= 80:
                            print(f"[DEBUG] ✅ Fuzzy action pattern: '{action} {obj}' -> '{command_key}' ({obj_score}%)")
                            return command_key
        return None

    def _check_parameter_commands(self, text_lower, param_commands):
        """Проверяет команды с параметрами: яркость 50, громкость 100"""
        for param_word, command_key in param_commands.items():
            if param_word in text_lower:
                print(f"[DEBUG] ✅ Parameter command: '{param_word}' -> '{command_key}'")
                return command_key
        return None

    def _check_direct_commands(self, text_lower, direct_commands):
        """Проверяет прямые команды: ярче, громче, пауза"""
        words = text_lower.split()
        for command_word, command_key in direct_commands.items():
            if command_word in words or text_lower == command_word:
                print(f"[DEBUG] ✅ Direct command: '{command_word}' -> '{command_key}'")
                return command_key
        return None

    def _check_colors(self, text_lower, colors):
        """Улучшенная проверка цветов"""
        for color_ru, command_key in colors.items():
            if color_ru in text_lower:
                print(f"[DEBUG] 🎨 Color: '{color_ru}' -> '{command_key}'")
                return command_key
            # Fuzzy проверка для цветов
            else:
                color_score = fuzz.partial_ratio(color_ru, text_lower)
                if color_score >= 75:
                    print(f"[DEBUG] 🎨 Fuzzy color: '{color_ru}' -> '{command_key}' ({color_score}%)")
                    return command_key
        return None

    def _check_palettes(self, text_lower, palettes):
        """Улучшенная проверка палитр"""
        for palette_ru, command_key in palettes.items():
            if palette_ru in text_lower:
                print(f"[DEBUG] 🎨 Palette: '{palette_ru}' -> '{command_key}'")
                return command_key
            # Fuzzy проверка для палитр
            else:
                palette_score = fuzz.partial_ratio(palette_ru, text_lower)
                if palette_score >= 75:
                    print(f"[DEBUG] 🎨 Fuzzy palette: '{palette_ru}' -> '{command_key}' ({palette_score}%)")
                    return command_key
        return None

    def _improved_fuzzy_search(self, text_lower, commands_data):
        """Улучшенный fuzzy поиск с частичными совпадениями"""
        best_match = None
        best_score = 0
        best_phrase = ""
        
        # Собираем ВСЕ возможные фразы и их command_key
        all_phrases_with_keys = []
        
        # Из action_patterns
        if 'action_patterns' in commands_data:
            for action, objects in commands_data['action_patterns'].items():
                for obj, command_key in objects.items():
                    full_phrase = f"{action} {obj}"
                    all_phrases_with_keys.append((full_phrase, command_key))
                    # Также добавляем частичные фразы
                    all_phrases_with_keys.append((obj, command_key))
        
        # Из direct_commands
        if 'direct_commands' in commands_data:
            for phrase, command_key in commands_data['direct_commands'].items():
                all_phrases_with_keys.append((phrase, command_key))
        
        # Из parameter_commands  
        if 'parameter_commands' in commands_data:
            for phrase, command_key in commands_data['parameter_commands'].items():
                all_phrases_with_keys.append((phrase, command_key))
        
        # Из colors (добавляем варианты с "включи" и без)
        if 'colors' in commands_data:
            for color_ru, command_key in commands_data['colors'].items():
                all_phrases_with_keys.append((f"включи {color_ru}", command_key))
                all_phrases_with_keys.append((f"сделай {color_ru}", command_key))
                all_phrases_with_keys.append((color_ru, command_key))
        
        # Из palettes (добавляем варианты с "палитра" и без)
        if 'palettes' in commands_data:
            for palette_ru, command_key in commands_data['palettes'].items():
                all_phrases_with_keys.append((f"палитра {palette_ru}", command_key))
                all_phrases_with_keys.append((f"включи палитру {palette_ru}", command_key))
                all_phrases_with_keys.append((palette_ru, command_key))
        
        # Fuzzy поиск по всем фразам
        for phrase, command_key in all_phrases_with_keys:
            # Используем partial_ratio для частичных совпадений
            score = fuzz.partial_ratio(phrase, text_lower)
            
            # Дополнительная проверка для коротких фраз
            if len(phrase.split()) <= 2 and len(text_lower.split()) <= 3:
                token_score = fuzz.token_set_ratio(phrase, text_lower)
                score = max(score, token_score)
            
            # Повышаем score если есть точное вхождение слов
            phrase_words = set(phrase.split())
            text_words = set(text_lower.split())
            common_words = phrase_words.intersection(text_words)
            if common_words:
                word_bonus = len(common_words) * 10
                score = min(100, score + word_bonus)
            
            if score > best_score and score >= 70:  # Понизил порог до 70%
                best_score = score
                best_match = command_key
                best_phrase = phrase
                print(f"[DEBUG] 🔍 Fuzzy: '{phrase}' -> '{command_key}' ({score}%)")
        
        if best_match and best_score >= 70:
            print(f"[DEBUG] ✅ Лучшее fuzzy совпадение: '{best_phrase}' -> '{best_match}' ({best_score}%)")
            return best_match
        
        # Дополнительная проверка для опечаток в одном слове
        if len(text_lower.split()) == 1:
            single_word_match = self._check_single_word_typos(text_lower, commands_data)
            if single_word_match:
                return single_word_match
        
        return None

    def _check_single_word_typos(self, text_lower, commands_data):
        """Проверяет опечатки в одном слове"""
        # Проверяем direct_commands
        if 'direct_commands' in commands_data:
            for word, command_key in commands_data['direct_commands'].items():
                if len(word.split()) == 1:  # Только однословные команды
                    score = fuzz.ratio(word, text_lower)
                    if score >= 80:  # Высокий порог для однословных
                        print(f"[DEBUG] 🔍 Single word fuzzy: '{word}' -> '{command_key}' ({score}%)")
                        return command_key
        
        # Проверяем colors
        if 'colors' in commands_data:
            for color, command_key in commands_data['colors'].items():
                if len(color.split()) == 1:
                    score = fuzz.ratio(color, text_lower)
                    if score >= 80:
                        print(f"[DEBUG] 🔍 Color fuzzy: '{color}' -> '{command_key}' ({score}%)")
                        return command_key
        
        # Проверяем palettes
        if 'palettes' in commands_data:
            for palette, command_key in commands_data['palettes'].items():
                if len(palette.split()) == 1:
                    score = fuzz.ratio(palette, text_lower)
                    if score >= 80:
                        print(f"[DEBUG] 🔍 Palette fuzzy: '{palette}' -> '{command_key}' ({score}%)")
                        return command_key
        
        return None

    def _has_number(self, text):
        """Проверяет наличие числа в тексте"""
        return bool(re.search(r'\d+', text))

    def _extract_after_keyword(self, text, keywords):
        """Извлекает текст после ключевого слова"""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                parts = text_lower.split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return None

    def _execute_by_key(self, command_key, my_say):
        """Выполняет команду по ключу"""
        command_map = {
            # Музыкальные команды
            "play": self.music_commands.play_music,
            "pause": self.music_commands.pause_music,
            "resume": self.music_commands.resume_music,
            "next": self.music_commands.next_track,
            "previous": self.music_commands.prev_track,
            "volume_up": self.music_commands.increase_volume,
            "volume_down": self.music_commands.decrease_volume,
            "set_volume": lambda: self.music_commands.set_volume_answer(my_say),
            "repeat": self.music_commands.toggle_repeat,
            
            # Системные команды
            "browser": self.system_commands.open_browser,
            "search": lambda: self.system_commands.search(
                self._extract_after_keyword(my_say, ["поиск", "найди"])
            ),
            "shutdown": self.system_commands.shutdown_computer,
            
            # Плейлисты
            "create_playlist": lambda: self.music_commands.create_playlist(
                self._extract_after_keyword(my_say, ["создай плейлист", "плейлист"])
            ),
            "switch_playlist": lambda: self.music_commands.switch_playlist(
                self._extract_after_keyword(my_say, ["включи плейлист", "плейлист"])
            ),
            
            # Команды света
            "light_on": self.light_commands.turn_on_light,
            "light_off": self.light_commands.turn_off_light,
            "brightness_up": self.light_commands.increase_brightness,
            "brightness_down": self.light_commands.decrease_brightness,
            "set_brightness": lambda: self.light_commands.set_brightness_answer(my_say),
            "music_mode": self.light_commands.start_music_mode,
            "wave_effect": self.light_commands.start_wave_effect,
            "breathing_effect": self.light_commands.start_breathing_effect,
            "monitor_mode": self.light_commands.start_monitor_mode,
            "static_mode": self.light_commands.set_static_mode,
            
            # Цвета
            "set_color_white": lambda: self.light_commands.set_color_direct("белый"),
            "set_color_red": lambda: self.light_commands.set_color_direct("красный"),
            "set_color_green": lambda: self.light_commands.set_color_direct("зеленый"),
            "set_color_blue": lambda: self.light_commands.set_color_direct("синий"),
            "set_color_yellow": lambda: self.light_commands.set_color_direct("желтый"),
            "set_color_purple": lambda: self.light_commands.set_color_direct("фиолетовый"),
            "set_color_cyan": lambda: self.light_commands.set_color_direct("голубой"),
            "set_color_orange": lambda: self.light_commands.set_color_direct("оранжевый"),
            "set_color_pink": lambda: self.light_commands.set_color_direct("розовый"),
            "set_color_mint": lambda: self.light_commands.set_color_direct("мятный"),
            "set_color_turquoise": lambda: self.light_commands.set_color_direct("бирюзовый"),
            "set_color_lavender": lambda: self.light_commands.set_color_direct("лавандовый"),
            
            # Палитры
            "set_palette_cold": lambda: self.light_commands.set_palette_direct("холодная"),
            "set_palette_lamp": lambda: self.light_commands.set_palette_direct("ламповая"),
            "set_palette_warm": lambda: self.light_commands.set_palette_direct("теплые"),
            "set_palette_minty": lambda: self.light_commands.set_palette_direct("мятная"),
            "set_palette_velvet": lambda: self.light_commands.set_palette_direct("бархатная"),
        }
        
        if command_key in command_map:
            print(f"[COMMAND] Выполняю: {command_key}")
            threading.Thread(target=command_map[command_key]).start()
        else:
            print(f"[ОШИБКА] Неизвестный ключ команды: {command_key}")

    def process_command(self, my_say):
        """Основной метод обработки команд"""
        my_say = my_say.lower().strip()
        try:
            command_key = self._find_command_key(my_say)
            if command_key:
                self._execute_by_key(command_key, my_say)
            else:
                print(f"[INFO] Команда не распознана: '{my_say}'")
        except Exception as e:
            print(f"[ОШИБКА] Обработка команды: {e}")
            
            
'''=============================================================================='''



# import threading
# from fuzzywuzzy import fuzz
# from .music_commands import MusicCommands
# from .system_commands import SystemCommands
# import json

# class CommandHandler:
#     def __init__(self):
#         self.music_commands = MusicCommands()
#         self.system_commands = SystemCommands()
    
    
    
#     def find_command_key(self, text):
#         with open(r"angelina\commands_checker\commands_dict.json", encoding="utf-8") as fraz:
#             data = json.load(fraz)
#         for keys in data:
#             for commands_key in data[keys]:
#                     for phrase in data[keys][commands_key]:
#                         if commands_key in text:
#                             return commands_key
        
#     def process_command(self, my_say):
#         my_say = my_say.lower()
#         try:
#             if fuzz.partial_ratio("открой браузер", my_say) > 80:
#                 threading.Thread(target=self.system_commands.open_browser).start()
#             elif fuzz.partial_ratio("выключи компьютер", my_say) > 90:
#                 threading.Thread(target=self.system_commands.shutdown_computer).start()
#             elif "поиск" in my_say:
#                 query = my_say.split("поиск", 1)[1].strip()
#                 threading.Thread(target=self.system_commands.search, args=(query,)).start()
#             elif "пауза" in my_say or "стоп" in my_say:
#                 threading.Thread(target=self.music_commands.pause_music).start()
#             elif "продолжи" in my_say or "возобнови" in my_say:
#                 threading.Thread(target=self.music_commands.resume_music).start()
#             elif "следующ" in my_say:
#                 threading.Thread(target=self.music_commands.next_track).start()
#             elif "предыдущий" in my_say:
#                 threading.Thread(target=self.music_commands.prev_track).start()
#             elif "громче" in my_say:
#                 threading.Thread(target=self.music_commands.increase_volume).start()
#             elif "тише" in my_say:
#                 threading.Thread(target=self.music_commands.decrease_volume).start()
#             elif "сделай громкость" in my_say or "громкость" in my_say:
#                 threading.Thread(target=self.music_commands.set_volume, args=(my_say,)).start()
#             elif "зацикли" in my_say or "повтор" in my_say or "повтори" in my_say:
#                 if "выключи" in my_say or "убери" in my_say or "сними" in my_say:
#                     threading.Thread(target=self.music_commands.disable_repeat).start()
#                 else:
#                     threading.Thread(target=self.music_commands.enable_repeat).start()
#             elif "создай плейлист" in my_say or "создай плэй лист" in my_say:
#                 if "создай плейлист" in my_say:
#                     playlist_name = my_say.split("создай плейлист", 1)[1].strip()
#                 else:
#                     playlist_name = my_say.split("создай плэй лист", 1)[1].strip()
#                 if playlist_name:
#                     threading.Thread(target=self.music_commands.create_playlist, args=(playlist_name,)).start()
#             elif "включи плейлист" in my_say or "включи плэй лист" in my_say:
#                 if "включи плейлист" in my_say:
#                     playlist_name = my_say.split("включи плейлист", 1)[1].strip()
#                 else:
#                     playlist_name = my_say.split("включи плэй лист", 1)[1].strip()
#                 if playlist_name:
#                     threading.Thread(target=self.music_commands.switch_playlist, args=(playlist_name,)).start()
#             elif "включи музыку" in my_say:
#                 threading.Thread(target=self.music_commands.switch_to_main_music).start()

#         except Exception as e:
#             print(f"[ОШИБКА] Обработка команды: {e}")