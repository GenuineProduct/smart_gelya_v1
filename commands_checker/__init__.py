# commands_checker/__init__.py
from .core import SmartCommandHandler, OllamaIntentAnalyzer
from .domains.music import MusicPlayback, MusicVolume, MusicPlaylists
from .domains.system import SystemBrowser, SystemSearch, SystemPower
from .domains.light import LightColorControl, LightBrightnessControl, LightEffectControl, LightPaletteControl
from .utils import with_gelya_response

# Для обратной совместимости
CommandHandler = SmartCommandHandler

__all__ = [
    'SmartCommandHandler', 'CommandHandler', 'OllamaIntentAnalyzer',
    'MusicPlayback', 'MusicVolume', 'MusicPlaylists',
    'SystemBrowser', 'SystemSearch', 'SystemPower', 
    'LightColorControl', 'LightBrightnessControl', 'LightEffectControl', 'LightPaletteControl',
    'with_gelya_response'
]