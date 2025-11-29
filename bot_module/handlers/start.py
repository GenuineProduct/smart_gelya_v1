from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

start_router = Router()

@start_router.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎵 Создать плейлист", callback_data="create_playlist")],
            [InlineKeyboardButton(text="📥 Загрузить музыку", callback_data="download_music")]
        ]
    )
    
    await message.answer(
        "🎵 Добро пожаловать в музыкального бота!\n\n"
        "Возможности:\n"
        "• Создать плейлист\n"
        "• Загрузить музыку с YouTube",
        reply_markup=keyboard
    )

@start_router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎵 Создать плейлист", callback_data="create_playlist")],
            [InlineKeyboardButton(text="📥 Загрузить музыку", callback_data="download_music")]
        ]
    )
    
    await callback.message.edit_text(
        "🎵 Добро пожаловать в музыкального бота!\n\n"
        "Возможности:\n"
        "• Создать плейлист\n"
        "• Загрузить музыку с YouTube",
        reply_markup=keyboard
    )