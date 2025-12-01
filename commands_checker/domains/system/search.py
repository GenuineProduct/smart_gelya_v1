# commands_checker/domains/system/search.py
import webbrowser
import json
from Gelya_voice import GelyaSpeach


gelya = GelyaSpeach()

class SystemSearch:
    def __init__(self):
        try:
            with open('responses.json', 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
        except FileNotFoundError:
            self.responses = {"positive_responses": ["хорошо", "сделано"]}

    def search(self, query):
        webbrowser.open(f"https://www.google.com/search?q={query}")
