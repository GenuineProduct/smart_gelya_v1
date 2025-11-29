"""
Пакет голосового движка Gelya
"""

from .Gelya_Speach import GelyaSpeach

# Создаем алиас для обратной совместимости
AngelinaVoice = GelyaSpeach

__all__ = ['GelyaSpeach', 'AngelinaVoice']