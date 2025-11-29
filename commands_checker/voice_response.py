# voice_response.py
from . import player  # Импортируем общего player

def with_gelya_response(gelya_func, allow_volume_change=False):
    def wrapper(*args, **kwargs):
        was_playing = player.is_playing()
        original_volume = player.get_volume() * 100  # в процентах

        # print(f"[DEBUG] Было: playing={was_playing}, volume={original_volume}%")

        if was_playing:
            if original_volume <= 10:
                reduction = 0.2
                zat_volume = max(1, original_volume * reduction)
                player.set_volume(zat_volume)
                print(f"[INFO] затишье, {zat_volume}%")
            else:
                player.set_volume(10)
                print(f"[INFO] затишье 10 (было {original_volume}%)")
                
        gelya_func(*args, **kwargs)

        if was_playing and not allow_volume_change:
            player.set_volume(original_volume)
            print(f"[INFO] восстановлена громкость: {original_volume}%")
        else:
            print("[DEBUG] Громкость изменена пользователем — не откатываем.")

    return wrapper