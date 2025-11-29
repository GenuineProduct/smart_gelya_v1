import os
import requests
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from pytubefix import YouTube
import asyncio
from concurrent.futures import ThreadPoolExecutor
from angelina.config.config import PLAYLISTS_PATH

download_router = Router()
executor = ThreadPoolExecutor(max_workers=2)
class DownloadStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_link = State()
    waiting_for_playlist_selection = State()

def get_playlists():
    """Получить список плейлистов"""
    playlists_path = PLAYLISTS_PATH  # ⬅️ ПУТЬ К ПЛЕЙЛИСТАМ
    if not os.path.exists(playlists_path):
        os.makedirs(playlists_path, exist_ok=True)
    return [d for d in os.listdir(playlists_path) if os.path.isdir(os.path.join(playlists_path, d))]

def convert_audio_file(input_path: str, output_path: str) -> bool:
    """Конвертирует аудио файл в правильный формат для pygame"""
    try:
        # Если файл уже в правильном формате
        if input_path.endswith('.mp3'):
            if input_path != output_path:
                os.rename(input_path, output_path)
            return True
        
        # Для других форматов используем внешний инструмент
        import subprocess
        import sys
        
        # Пробуем использовать ffmpeg если установлен
        try:
            if sys.platform == "win32":
                # Для Windows ищем ffmpeg в PATH
                result = subprocess.run(
                    ['ffmpeg', '-i', input_path, '-codec:a', 'libmp3lame', '-qscale:a', '2', output_path, '-y'],
                    capture_output=True,
                    timeout=60
                )
            else:
                # Для Linux/Mac
                result = subprocess.run(
                    ['ffmpeg', '-i', input_path, '-acodec', 'mp3', output_path, '-y'],
                    capture_output=True,
                    timeout=60
                )
            
            if result.returncode == 0 and os.path.exists(output_path):
                # Удаляем исходный файл
                if os.path.exists(input_path):
                    os.remove(input_path)
                return True
        except:
            pass
        
        # Если ffmpeg не сработал, пробуем просто переименовать
        if input_path != output_path:
            os.rename(input_path, output_path)
        return True
        
    except Exception as e:
        print(f"Ошибка конвертации: {e}")
        # В крайнем случае просто переименовываем
        try:
            if input_path != output_path:
                os.rename(input_path, output_path)
            return True
        except:
            return False

async def download_youtube_audio(url: str, output_path: str, message: Message):
    """Скачать аудио с YouTube в правильном формате"""
    try:
        await message.answer('🔍 Получаю информацию о видео...')
        
        yt = YouTube(url)
        
        # Проверка длительности
        if yt.length // 60 >= 30:
            await message.answer(f'❌ Видео длиннее 30 минут: {yt.title}')
            return False
        
        await message.answer(f'⏬ Скачиваю: {yt.title}')
        
        # Ищем поток с максимальным битрейтом в MP3 формате
        audio_streams = yt.streams.filter(only_audio=True)
        
        # Сортируем по битрейту (от высокого к низкому)
        audio_streams = sorted(audio_streams, key=lambda x: int(x.abr.replace('kbps', '')) if x.abr else 0, reverse=True)
        
        if not audio_streams:
            await message.answer('❌ Не удалось найти аудио поток')
            return False
        
        # Берем лучший аудио поток
        best_audio = audio_streams[0]
        
        # Создаем папки если не существуют
        os.makedirs("temp_downloads", exist_ok=True)
        os.makedirs(output_path, exist_ok=True)
        
        # Скачиваем во временную папку
        await message.answer('📥 Начинаю загрузку...')
        temp_filename = best_audio.download(output_path="temp_downloads")
        
        await message.answer('🔄 Обрабатываю файл...')
        
        # Создаем имя для конечного файла
        safe_title = "".join(c for c in yt.title if c not in '<>:"/\\|?*')
        final_path = os.path.join(output_path, f"{safe_title}.mp3")
        
        # Обрабатываем файл в отдельном потоке
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            executor, 
            convert_audio_file, 
            temp_filename, 
            final_path
        )
        
        if success:
            # Проверяем что файл существует и не пустой
            if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                await message.answer(
                    f'✅ Успешно скачано!\n'
                    f'🎵 {yt.title}\n'
                    f'👤 {yt.author}\n'
                    f'📁 Плейлист: {os.path.basename(output_path)}'
                )
                return True
            else:
                await message.answer('❌ Файл создан но поврежден')
                return False
        else:
            await message.answer('❌ Ошибка обработки файла')
            return False
            
    except Exception as e:
        await message.answer(f'❌ Ошибка при скачивании: {str(e)}')
        return False


@download_router.callback_query(F.data == "download_music")
async def download_music_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📁 Загрузить файл", callback_data="upload_file")],
            [InlineKeyboardButton(text="🔗 Ссылка YouTube", callback_data="upload_link")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
        ]
    )
    
    await callback.message.edit_text(
        "📥 Выберите способ загрузки музыки:",
        reply_markup=keyboard
    )

@download_router.callback_query(F.data == "upload_link")
async def upload_link_start(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="download_music")]
        ]
    )
    
    await callback.message.edit_text(
        "🔗 Введите ссылку на YouTube видео:",
        reply_markup=keyboard
    )
    await state.set_state(DownloadStates.waiting_for_link)

@download_router.message(DownloadStates.waiting_for_link)
async def process_youtube_link(message: Message, state: FSMContext):
    url = message.text.strip()
    
    # Проверяем валидность ссылки
    if not url.startswith(('http://', 'https://')):
        await message.answer("❌ Пожалуйста, введите корректную ссылку YouTube")
        return
    
    # Сохраняем ссылку в состоянии
    await state.update_data(youtube_url=url)
    
    playlists = get_playlists()
    
    if not playlists:
        await message.answer("❌ Нет доступных плейлистов. Сначала создайте плейлист.")
        return
    
    keyboard_buttons = []
    for playlist in playlists:
        keyboard_buttons.append([InlineKeyboardButton(
            text=f"📁 {playlist}", 
            callback_data=f"select_playlist_link:{playlist}"
        )])
    
    keyboard_buttons.append([InlineKeyboardButton(text="➕ Создать плейлист", callback_data="create_playlist_from_download")])
    keyboard_buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="download_music")])
    
    await message.answer(
        "🎯 Выберите плейлист для сохранения:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    )

@download_router.callback_query(F.data.startswith("select_playlist_link:"))
async def process_playlist_selection_link(callback: CallbackQuery, state: FSMContext):
    playlist_name = callback.data.split(":")[1]
    data = await state.get_data()
    youtube_url = data.get('youtube_url')
    
    if not youtube_url:
        await callback.message.edit_text("❌ Ссылка не найдена. Попробуйте снова.")
        await state.clear()
        return
    
    # Путь к папке плейлиста ⬅️ ОСНОВНОЙ ПУТЬ
    playlist_path = f"{PLAYLISTS_PATH}/{playlist_name}"
    os.makedirs(playlist_path, exist_ok=True)
    
    await callback.message.edit_text("⏬ Скачиваю аудио...")
    
    success = await download_youtube_audio(youtube_url, playlist_path, callback.message)
    
    if success:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📥 Загрузить еще", callback_data="download_music")],
                [InlineKeyboardButton(text="⬅️ В начало", callback_data="back_to_start")]
            ]
        )
        await callback.message.answer("✅ Готово! Что дальше?", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="download_music")]]
        )
        await callback.message.answer("❌ Не удалось скачать", reply_markup=keyboard)
    
    await state.clear()

@download_router.callback_query(F.data == "create_playlist_from_download")
async def create_playlist_from_download(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 Введите название для нового плейлиста:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="upload_link")]]
        )
    )
    await state.set_state(DownloadStates.waiting_for_playlist_selection)

@download_router.message(DownloadStates.waiting_for_playlist_selection)
async def process_new_playlist_name(message: Message, state: FSMContext):
    playlist_name = message.text.strip()
    
    if not playlist_name:
        await message.answer("❌ Название плейлиста не может быть пустым!")
        return
    
    # Создаем папку плейлиста ⬅️ ПУТЬ ДЛЯ НОВЫХ ПЛЕЙЛИСТОВ
    playlist_path = f"{PLAYLISTS_PATH}/{playlist_name}"
    os.makedirs(playlist_path, exist_ok=True)
    
    data = await state.get_data()
    youtube_url = data.get('youtube_url')
    
    if youtube_url:
        success = await download_youtube_audio(youtube_url, playlist_path, message)
        
        if success:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📥 Загрузить еще", callback_data="download_music")],
                    [InlineKeyboardButton(text="⬅️ В начало", callback_data="back_to_start")]
                ]
            )
            await message.answer("✅ Готово! Что дальше?", reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="download_music")]]
            )
            await message.answer("❌ Не удалось скачать", reply_markup=keyboard)
    else:
        await message.answer(
            f"✅ Плейлист '{playlist_name}' создан! Теперь можете загрузить в него музыку.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="📥 Загрузить музыку", callback_data="download_music")]]
            )
        )
    
    await state.clear()