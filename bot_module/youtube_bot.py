import os
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

from .handlers.start import start_router
from .handlers.playlist import playlist_router
from .handlers.download import download_router

class YouTubeBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Регистрация всех роутеров
        self.dp.include_router(start_router)
        self.dp.include_router(playlist_router)
        self.dp.include_router(download_router)
    
    async def start(self):
        await self.dp.start_polling(self.bot)