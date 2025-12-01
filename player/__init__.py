# player/__init__.py (исправленная версия)
from .player import MusicPlayer

# Глобальный экземпляр плеера
_player_instance = None

def get_player_instance():
    """Получить глобальный экземпляр плеера"""
    global _player_instance
    return _player_instance

def set_player_instance(instance):
    """Установить глобальный экземпляр плеера"""
    global _player_instance
    _player_instance = instance

# Для обратной совместимости - создаем алиас
def get_player():
    """Алиас для get_player_instance для обратной совместимости"""
    return get_player_instance()

player = None

__all__ = ['MusicPlayer', 'get_player_instance', 'set_player_instance', 'get_player', 'player']