import webbrowser
import os
import json
from Gelya_voice import GelyaSpeach
from .voice_response import with_gelya_response

gelya = GelyaSpeach()


class SystemCommands:
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

    def open_browser(self):
        with_gelya_response(lambda: gelya.speach(self._get_random_response()))()
        webbrowser.open("https://google.com")

    def shutdown_computer(self):
        with_gelya_response(lambda: gelya.speach("до завершения работы 5 секунд"))()
        if os.name == 'nt':
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")

    def search(self, query):
        if query.strip():
            with_gelya_response(lambda: gelya.speach(f"вот что удалось найти по запросу: {query}"))()
            webbrowser.open(f"https://www.google.com/search?q={query}")