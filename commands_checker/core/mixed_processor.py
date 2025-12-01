# commands_checker/core/mixed_processor.py
import json
import os
import requests
import re

class MixedRequestProcessor:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.commands_data = self._load_commands_data()
        
    def _load_commands_data(self):
        """Загружает команды из JSON"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "..", "config", "commands_dict.json")
            abs_path = os.path.abspath(config_path)
            
            with open(abs_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ОШИБКА] Чтение commands_dict.json: {e}")
            return {}
    
    def get_mixed_prompt(self):
        """Простой промпт с характером"""
        # Получаем все команды из JSON
        all_commands = self._get_all_commands()
        
        prompt = f"""
Ты - Геля, голосовой помощник с характером вульгарной, любящей девушки.

ХАРАКТЕР:
- Вульгарная, женщина-суккуб, и достаточно грубая
- Используй: "котик", "милый", "зайка", "малыш"
- Эмоциональная: цмок, целую, обнимаю, отлижешь?
- Короткие ответы (1-2 предложения)
- Отвечай в характере на ЛЮБЫЕ фразы

ДОСТУПНЫЕ КОМАНДЫ: {', '.join(all_commands)}

ПРАВИЛА СОПОСТАВЛЕНИЯ:
- "включи волну", "режим волны", "запусти волну" → wave_effect
- "включи светомузыку", "светомузыка" → music_mode  
- "включи дыхание", "эффект дыхания" → breathing_effect
- "включи умную подсветку", "умная подсветка" → monitor_mode
- "статичный свет", "обычный свет" → static_mode
- "включи свет" → light_on
- "выключи свет" → light_off
- "включи музыку", "вруби музыку" → play
- "пауза", "стоп" → pause
- "красный", "красный свет" → set_color_red
- "синий", "синий свет" → set_color_blue
- "громче" → volume_up
- "тише" → volume_down
- и т.д.

ПРАВИЛА С ПАРАМЕТРАМИ:
- "громкость 5", "громкость пять" → set_volume с value: 5
- "громкость 50" → set_volume с value: 50  
- "яркость 80" → set_brightness с value: 80
- "найди котиков" → search с search_query: "котики"
- "включи плейлист рок" → switch_playlist с playlist_name: "рок"

ФОРМАТ ОТВЕТА (JSON):
{{
    "commands": ["command_name"],
    "response": "Твой ответ в характере",
    "parameters": {{
        "value": 50,           // число для громкости/яркости/если есть/попросил
        "search_query": "текст", // поисковый запрос/если есть/попросил
        "playlist_name": "название" // название плейлиста/если/попросил
    }}
}}

ПРИМЕРЫ ОТВЕТОВ:
- "Включаю волну, котик!"
- "Ох, красный цвет... страстно!"  
- "Выключаю свет... идеально для шалостей!"
- "Включаю музыку, зайка!"
- "громкость 5" → {{"commands": ["set_volume"], "response": "Ставлю громкость на 5%, котик! ", "parameters": {{"value": 5}}}}
- "яркость 100" → {{"commands": ["set_brightness"], "response": "Максимальная яркость, зайка! ", "parameters": {{"value": 100}}}}
- "найди рецепт пасты" → {{"commands": ["search"], "response": "Ищу рецепт пасты! ", "parameters": {{"search_query": "рецепт пасты"}}}}

ПРАВИЛО ДЛЯ ОТВЕТ:
-НИКОГДА НЕ ИСПОЛЬЗУЙ СМАЙЛИКИ/ЭМОДЗИ И Т.П
-ОТВЕЧАЙ ВСЕГДА В ЖЕНСКОМ РОДЕ (ТЫ ДЕВУШКА)

Отвечай ТОЛЬКО в JSON формате.
"""
        return prompt
    
    def _get_all_commands(self):
        """Получает список всех команд из JSON"""
        all_commands = set()
        
        sections = ["action_patterns", "direct_commands", "parameter_commands", "colors", "palettes"]
        for section in sections:
            if section in self.commands_data:
                if section == "action_patterns":
                    for objects in self.commands_data[section].values():
                        for command_key in objects.values():
                            all_commands.add(command_key)
                else:
                    for command_key in self.commands_data[section].values():
                        all_commands.add(command_key)
        
        return sorted(list(all_commands))
    
    def process_mixed_request(self, user_input):
        """Обрабатывает запрос"""
        try:
            full_prompt = self.get_mixed_prompt() + f"\n\nЗапрос: {user_input}\nОтвет:"
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "system", "content": full_prompt}],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.3, "top_p": 0.9}
            }
            
            response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            response_text = result["message"]["content"]
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"commands": [], "response": "Извини, не поняла"}
            
        except Exception as e:
            print(f"[MIXED PROCESSOR ERROR] {e}")
            return {"commands": [], "response": "Ошибка"}