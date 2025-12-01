# commands_checker/utils/ollama_client.py
import requests
import json

class OllamaClient:
    """Универсальный клиент для работы с Ollama API"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate_response(self, model, system_prompt, user_input, temperature=0.1, format="json"):
        """Генерация ответа через Ollama"""
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "stream": False,
                "format": format,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"]
            
        except requests.exceptions.ConnectionError:
            print("[OLLAMA] Сервер недоступен")
            return None
        except Exception as e:
            print(f"[OLLAMA CLIENT ERROR] {e}")
            return None
    
    def is_server_running(self):
        """Проверка доступности сервера Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Получение списка доступных моделей"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return []