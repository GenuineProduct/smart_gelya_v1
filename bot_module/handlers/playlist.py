import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from angelina.config.config import PLAYLISTS_PATH

playlist_router = Router()

class CreatePlaylist(StatesGroup):
    waiting_for_name = State()

@playlist_router.callback_query(F.data == "create_playlist")
async def create_playlist_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 Введите название для нового плейлиста:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]]
        )
    )
    await state.set_state(CreatePlaylist.waiting_for_name)

@playlist_router.message(CreatePlaylist.waiting_for_name)
async def process_playlist_name(message: Message, state: FSMContext):
    playlist_name = message.text.strip()
    
    if not playlist_name:
        await message.answer("❌ Название плейлиста не может быть пустым!")
        return
    
    # Создаем папку плейлиста ⬅️ ТОТ ЖЕ ПУТЬ
    playlist_path = f"{PLAYLISTS_PATH}/{playlist_name}"
    os.makedirs(playlist_path, exist_ok=True)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 Загрузить музыку", callback_data="download_music")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
        ]
    )
    
    await message.answer(
        f"✅ Плейлист '{playlist_name}' успешно создан!",
        reply_markup=keyboard
    )
    await state.clear()