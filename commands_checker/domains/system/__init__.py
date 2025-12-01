# commands_checker/domains/system/__init__.py
from .browser import SystemBrowser
from .search import SystemSearch
from .power import SystemPower

__all__ = ['SystemBrowser', 'SystemSearch', 'SystemPower']