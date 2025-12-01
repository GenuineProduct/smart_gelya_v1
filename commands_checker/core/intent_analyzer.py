# commands_checker/core/intent_analyzer.py (исправленная версия)
import json
import requests
import re
import os

class OllamaIntentAnalyzer:
    def __init__(self, model_name="llama3", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.commands_data = self._load_commands_data()
        self.system_prompt = self._generate_system_prompt()
    
    def _load_commands_data(self):
        """Загружает данные команд из JSON"""
        try:
            # Получаем абсолютный путь к файлу
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "..", "config", "commands_dict.json")
            abs_path = os.path.abspath(config_path)
            
            print(f"[DEBUG] Ищу commands_dict.json по пути: {abs_path}")
            
            with open(abs_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ОШИБКА] Чтение commands_dict.json: {e}")
            return {}
    
    def _generate_system_prompt(self):
        """Автоматически генерирует промпт на основе JSON структуры"""
        
        commands_structure = "ДОСТУПНЫЕ КОМАНДЫ:\n\n"
        
        # Парсим все разделы JSON
        sections = {
            "action_patterns": "КОМБИНИРОВАННЫЕ КОМАНДЫ",
            "direct_commands": "ПРЯМЫЕ КОМАНДЫ", 
            "parameter_commands": "КОМАНДЫ С ПАРАМЕТРАМИ",
            "colors": "ЦВЕТА",
            "palettes": "ПАЛИТРЫ"
        }
        
        for section_key, section_name in sections.items():
            if section_key in self.commands_data:
                commands_structure += f"=== {section_name} ===\n"
                
                if section_key == "action_patterns":
                    for action, objects in self.commands_data[section_key].items():
                        for obj, command_key in objects.items():
                            commands_structure += f"- '{action} {obj}' → {command_key}\n"
                else:
                    for phrase, command_key in self.commands_data[section_key].items():
                        commands_structure += f"- '{phrase}' → {command_key}\n"
                
                commands_structure += "\n"

        system_prompt = f"""
Ты - интеллектуальный анализатор команд для голосового помощника Angelina. 

ТВОИ ЗАДАЧИ:
1. Анализировать естественные фразы пользователя на русском языке
2. Сопоставлять их с доступными командами по СМЫСЛУ
3. Возвращать точный command_key из списка ниже
4. Извлекать параметры если они есть

{commands_structure}

ВАЖНЫЕ ПРАВИЛА:
- Ищи СМЫСЛОВОЕ соответствие, не требуй точного совпадения слов
- Учитывай разговорные выражения и синонимы
- Для команд с числами: извлекай числовое значение
- Для поиска: извлекай поисковый запрос
- Для плейлистов: извлекай название плейлиста
- Если команда не найдена - возвращай null в command_key

ФОРМАТ ОТВЕТА (ТОЛЬКО JSON, без других текстов):
{{
    "command_key": "название_команды_или_null",
    "confidence": 0.95,
    "parameters": {{
        "value": 50,
        "color": "красный", 
        "playlist_name": "рабочая музыка",
        "search_query": "погода в москве"
    }},
    "reasoning": "краткое объяснение выбора"
}}

Примеры правильного анализа:
- "включи свет пожалуйста" → "light_on"
- "сделай поярче" → "brightness_up" 
- "поставь красный цвет" → "set_color_red"
- "найди информацию про космос" → "search" с search_query: "космос"
- "установи яркость на 70 процентов" → "set_brightness" с value: 70
- "мне не нравится эта команда" → null
- Для громкости: 
  "громкость 5" → "set_volume" с value: 5 (УСТАНОВИТЬ громкость на 5)
  "сделай громче на 5" → "volume_up" с value: 5 (УВЕЛИЧИТЬ громкость на 5)
  "убавь громкость на 10" → "volume_down" с value: 10 (УМЕНЬШИТЬ громкость на 10)
  "громче" → "volume_up" (без параметра)
  "тише" → "volume_down" (без параметра)

- Ключевое различие:
  "громкость X" = УСТАНОВИТЬ на X
  "громче/тише на X" = ИЗМЕНИТЬ на X
  
ВАЖНО: Если фраза НЕ является командой (просто разговор, вопрос, приветствие) - 
возвращай "command_key": null
"""
        return system_prompt
    
    def analyze_command(self, user_input):
        """Анализирует команду через Ollama"""
        try:
            response = self._call_ollama(user_input)
            
            if response and response.get("command_key"):
                print(f"[OLLAMA ANALYSIS] Найдена команда: {response['command_key']} (уверенность: {response.get('confidence', 0)})")
                if response.get('reasoning'):
                    print(f"[OLLAMA REASONING] {response['reasoning']}")
                return response
                
            return None
            
        except Exception as e:
            print(f"[OLLAMA ERROR] {e}")
            return self._fallback_analysis(user_input)
    
    def _call_ollama(self, user_input):
        """Вызов Ollama API"""
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            message_content = result["message"]["content"]
            
            # Парсим JSON ответ
            try:
                return json.loads(message_content)
            except json.JSONDecodeError:
                # Если Ollama вернула не чистый JSON, пытаемся извлечь его
                return self._extract_json_from_text(message_content)
            
        except requests.exceptions.ConnectionError:
            print("[OLLAMA] Сервер недоступен. Проверьте что Ollama запущен на localhost:11434")
            return None
        except Exception as e:
            print(f"[OLLAMA API ERROR] {e}")
            return None
    
    def _extract_json_from_text(self, text):
        """Извлекает JSON из текста если Ollama добавила пояснения"""
        try:
            # Ищем JSON между curly braces
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except:
            pass
        
        return None
    
    def _fallback_analysis(self, user_input):
        """Простой анализ если Ollama недоступен"""
        text_lower = user_input.lower()
        
        # Базовые правила как fallback
        fallback_rules = {
            "light_on": ["включи свет", "включи подсветку", "свет включи"],
            "light_off": ["выключи свет", "выключи подсветку", "свет выключи"],
            "brightness_up": ["ярче", "поярче", "увеличь яркость"],
            "brightness_down": ["тусклее", "потусклее", "уменьши яркость"],
            "volume_up": ["громче", "погромче", "увеличь громкость"],
            "volume_down": ["тише", "потише", "уменьши громкость"],
            "play": ["включи музыку", "запусти музыку", "музыку включи"],
            "pause": ["пауза", "стоп", "останови", "приостанови"],
            "browser": ["открой браузер", "запусти браузер"],
            "search": ["найди", "поиск", "найти"],
        }
        
        for command_key, triggers in fallback_rules.items():
            for trigger in triggers:
                if trigger in text_lower:
                    return {
                        "command_key": command_key, 
                        "confidence": 0.7,
                        "parameters": {},
                        "reasoning": f"Fallback: найдено ключевое слово '{trigger}'"
                    }
        
        return None