import pyautogui
import serial
import time
import numpy as np

def get_stable_color():
    try:
        screenshot = pyautogui.screenshot()
        pixels = np.array(screenshot)
        
        # Берем только центральную область
        h, w = pixels.shape[:2]
        center = pixels[h//3:2*h//3, w//3:2*w//3]
        
        # Усредняем цвет
        avg_color = center.mean(axis=(0, 1))
        r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
        
        # Ограничиваем значения
        r = max(10, min(200, r))
        g = max(10, min(200, g))
        b = max(10, min(200, b))
        
        return r, g, b
        
    except Exception as e:
        print(f"[MONITOR] Ошибка получения цвета: {e}")
        # Возвращаем нейтральный цвет в случае ошибки
        return 128, 128, 128

# УБРАТЬ весь код, который выполняется сразу!
# Оставить только функции

# Если нужно оставить старую функциональность для самостоятельного запуска,
# можно добавить проверку:
if __name__ == "__main__":
    # Этот код выполнится только если запустить файл напрямую
    # python monitor_checker.py
    arduino = serial.Serial('COM11', 115200, timeout=0.1)
    time.sleep(2)

    last_r, last_g, last_b = 50, 50, 50

    try:
        while True:
            r, g, b = get_stable_color()
            
            # Плавный переход
            smooth = 0.4
            r = int(last_r * (1-smooth) + r * smooth)
            g = int(last_g * (1-smooth) + g * smooth)
            b = int(last_b * (1-smooth) + b * smooth)
            
            last_r, last_g, last_b = r, g, b
            
            command = f"{r},{g},{b}\n"
            arduino.write(command.encode())
            time.sleep(0.08)
            
    except KeyboardInterrupt:
        for i in range(10):
            fade = 1.0 - (i / 10.0)
            arduino.write(f"{int(last_r*fade)},{int(last_g*fade)},{int(last_b*fade)}\n".encode())
            time.sleep(0.05)
        arduino.close()