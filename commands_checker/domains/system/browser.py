# commands_checker/domains/system/browser.py
import webbrowser
import json
from Gelya_voice import GelyaSpeach

gelya = GelyaSpeach()

class SystemBrowser:
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
        webbrowser.open("https://google.com")