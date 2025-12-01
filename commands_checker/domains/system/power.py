# commands_checker/domains/system/power.py
import os
import json
from Gelya_voice import GelyaSpeach

gelya = GelyaSpeach()

class SystemPower:
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

    def shutdown_computer(self):
        if os.name == 'nt':
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")
