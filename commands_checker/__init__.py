# commands_checker/__init__.py
from player.player import MusicPlayer
from config.config import PLAYLISTS_PATH
# Единый глобальный player для всего пакета
player = MusicPlayer(f"{PLAYLISTS_PATH}/всякое")

from .command_handler import CommandHandler
from .music_commands import MusicCommands
from .system_commands import SystemCommands
from .light_commands import LightCommands
from .voice_response import with_gelya_response

__all__ = [
    'CommandHandler', 'MusicCommands', 'SystemCommands', 'LightCommands',
    'with_gelya_response', 'player'
           ]