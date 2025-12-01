from light.light_controller import LightController

# Создаем единый экземпляр контроллера света
_light_controller = None

def get_light_controller():
    """Получить глобальный экземпляр контроллера света"""
    global _light_controller
    if _light_controller is None:
        _light_controller = LightController()
        print("[LIGHT] Контроллер инициализирован (единый экземпляр)")
    return _light_controller

from .color_control import LightColorControl
from .brightness_control import LightBrightnessControl
from .effect_control import LightEffectControl
from .palette_control import LightPaletteControl

__all__ = [
    'LightColorControl', 'LightBrightnessControl', 
    'LightEffectControl', 'LightPaletteControl',
    'get_light_controller'
]