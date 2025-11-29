import serial
import time
import threading
import json
import numpy as np
import pyaudio
from collections import deque
import math

class LightController:
    def __init__(self, port='COM11', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.arduino = None
        self.current_mode = "static"
        self.current_color = (255, 255, 255)
        self.brightness = 100
        self.palette = "white"
        self.is_on = False
        
        # Флаги для управления потоками эффектов
        self._wave_thread = None
        self._wave_running = False
        self._breathing_thread = None
        self._breathing_running = False
        self._monitor_thread = None
        self._monitor_running = False
        
        # Для светомузыки
        self.audio_interface = None
        self.audio_stream = None
        self.is_music_mode = False
        self.audio_data = deque(maxlen=100)
        
        # Параметры ленты
        self.NUM_LEDS = 60  # Количество светодиодов
        
        # Палитры цветов
        self.palettes = {
            "холодная": [(200, 230, 255), (170, 210, 255), (140, 190, 255)],
            "ламповая": [(255, 200, 150), (255, 180, 120), (255, 160, 100)],
            "теплые": [(255, 220, 180), (255, 200, 150), (255, 180, 120)],
            "мятная": [(200, 255, 230), (180, 240, 220), (160, 230, 210)],
            "бархатная": [(150, 100, 200), (130, 80, 180), (110, 60, 160)]
        }
        
        # Цвета по названиям
        self.colors = {
            "белый": (255, 255, 255),
            "красный": (255, 0, 0),
            "зеленый": (0, 255, 0),
            "синий": (0, 0, 255),
            "желтый": (255, 255, 0),
            "фиолетовый": (255, 0, 255),
            "голубой": (0, 255, 255),
            "оранжевый": (255, 165, 0),
            "розовый": (255, 192, 203),
            "мятный": (170, 240, 210),
            "бирюзовый": (64, 224, 208),
            "лавандовый": (230, 230, 250)
        }
        
        # СРАЗУ ПОДКЛЮЧАЕМСЯ И ВЫКЛЮЧАЕМ СВЕТ ПРИ ЗАПУСКЕ
        self._force_turn_off()
        
        print("[LIGHT] Контроллер инициализирован (свет выключен)")
    
    def _force_turn_off(self):
        """Принудительно выключает свет при инициализации"""
        try:
            print("[LIGHT] Принудительно выключаю свет...")
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=0.1)
            time.sleep(2)
            
            # Отправляем команду выключения несколько раз для надежности
            for _ in range(3):
                self.arduino.write(b"0,0,0\n")
                time.sleep(0.1)
            
            self.is_on = False
            print("[LIGHT] Свет принудительно выключен")
            
            # Закрываем соединение - подключимся позже при командах
            self.arduino.close()
            self.arduino = None
            
        except Exception as e:
            print(f"[LIGHT] Ошибка принудительного выключения: {e}")
            self.arduino = None
    
    def __del__(self):
        """Деструктор - закрывает соединение при удалении объекта"""
        self.close_connection()
    
    def close_connection(self):
        """Закрывает соединение с Arduino"""
        if self.arduino:
            try:
                # Выключаем свет перед закрытием
                self.arduino.write(b"0,0,0\n")
                time.sleep(0.1)
                self.arduino.close()
                print("[LIGHT] Соединение с Arduino закрыто, свет выключен")
            except Exception as e:
                print(f"[LIGHT] Ошибка закрытия соединения: {e}")
            self.arduino = None
    
    def _connect_arduino(self):
        """Подключение к Arduino"""
        if self.arduino:
            return True
            
        try:
            print(f"[LIGHT] Подключаюсь к Arduino на {self.port}...")
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=0.1)
            time.sleep(2)
            
            # Убеждаемся, что свет выключен при подключении
            self.arduino.write(b"0,0,0\n")
            time.sleep(0.1)
            
            print(f"[LIGHT] Успешно подключено к Arduino на {self.port}")
            return True
        except Exception as e:
            print(f"[LIGHT] Ошибка подключения к Arduino: {e}")
            self.arduino = None
            return False

    def _stop_all_effects(self):
        """Останавливает все эффекты"""
        print("[LIGHT] Останавливаю все эффекты...")
        
        # Останавливаем волну
        self._wave_running = False
        if self._wave_thread and self._wave_thread.is_alive():
            self._wave_thread.join(timeout=1.0)
        
        # Останавливаем дыхание
        self._breathing_running = False
        if self._breathing_thread and self._breathing_thread.is_alive():
            self._breathing_thread.join(timeout=1.0)
        
        # Останавливаем монитор
        self._monitor_running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        
        # Останавливаем светомузыку (с проверкой атрибутов)
        self.stop_music_mode()

    def _apply_brightness(self, color):
        """Применяет яркость к цвету"""
        r, g, b = color
        brightness_factor = self.brightness / 100.0
        return (
            int(r * brightness_factor),
            int(g * brightness_factor), 
            int(b * brightness_factor)
        )
    
    def send_color(self, r, g, b):
        """Отправка одного цвета на всю ленту"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        if not self.is_on:
            return
        
        try:
            # Применяем яркость
            r, g, b = self._apply_brightness((r, g, b))
            
            # Ограничиваем значения
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            command = f"{r},{g},{b}\n"
            self.arduino.write(command.encode())
            
        except Exception as e:
            print(f"[LIGHT] Ошибка отправки цвета: {e}")
            self.arduino = None

    def send_led_strip_data(self, led_colors):
        """Отправляет данные для каждого светодиода отдельно"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        if not self.is_on:
            return
        
        try:
            # Формируем команду для всех светодиодов
            # Формат: "LED:r1,g1,b1;r2,g2,b2;...;rN,gN,bN\n"
            command_parts = []
            for r, g, b in led_colors:
                # Применяем яркость к каждому светодиоду
                r_adj, g_adj, b_adj = self._apply_brightness((r, g, b))
                r_adj = max(0, min(255, r_adj))
                g_adj = max(0, min(255, g_adj))
                b_adj = max(0, min(255, b_adj))
                command_parts.append(f"{r_adj},{g_adj},{b_adj}")
            
            command = "LED:" + ";".join(command_parts) + "\n"
            self.arduino.write(command.encode())
            
        except Exception as e:
            print(f"[LIGHT] Ошибка отправки данных ленты: {e}")
            self.arduino = None
    
    def turn_on(self):
        """Включить свет"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        self.is_on = True
        self.send_color(*self.current_color)
        print("[LIGHT] Свет включен")
    
    def turn_off(self):
        """Выключить свет"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        self.is_on = False
        # Отправляем черный цвет для выключения
        try:
            self.arduino.write(b"0,0,0\n")
            time.sleep(0.1)
        except Exception as e:
            print(f"[LIGHT] Ошибка выключения света: {e}")
        print("[LIGHT] Свет выключен")
    
    def set_brightness(self, percent):
        """Установить яркость"""
        self.brightness = max(0, min(100, percent))
        if self.is_on and self.arduino:
            self.send_color(*self.current_color)
        print(f"[LIGHT] Яркость установлена: {self.brightness}%")
    
    def increase_brightness(self, step=10):
        """Увеличить яркость"""
        self.set_brightness(self.brightness + step)
    
    def decrease_brightness(self, step=10):
        """Уменьшить яркость"""
        self.set_brightness(self.brightness - step)
    
    def set_color(self, color_name):
        """Установить цвет по имени (работает даже в режимах эффектов)"""
        if not self.arduino:
            if not self._connect_arduino():
                return False
                
        color_name = color_name.lower()
        print(f"[LIGHT] Пытаюсь установить цвет: {color_name}")
        
        # Поиск в базовых цветах
        if color_name in self.colors:
            new_color = self.colors[color_name]
            self.current_color = new_color
            self.palette = color_name
            
            # Если свет включен, сразу применяем новый цвет
            if self.is_on:
                if self.current_mode == "static":
                    # Просто устанавливаем цвет
                    self.send_color(*new_color)
                else:
                    # В режимах эффектов цвет применится в следующем цикле эффекта
                    print(f"[LIGHT] Цвет изменен на {color_name} (активен режим: {self.current_mode})")
            
            print(f"[LIGHT] Установлен цвет: {color_name}")
            return True
        
        # Поиск в палитрах
        if color_name in self.palettes:
            new_color = self.palettes[color_name][0]
            self.current_color = new_color
            self.palette = color_name
            
            if self.is_on:
                if self.current_mode == "static":
                    self.send_color(*new_color)
                else:
                    print(f"[LIGHT] Палитра изменена на {color_name} (активен режим: {self.current_mode})")
            
            print(f"[LIGHT] Установлена палитра: {color_name}")
            return True
        
        print(f"[LIGHT] Цвет не найден: {color_name}")
        return False
    
    def set_palette(self, palette_name):
        """Установить палитру (работает даже в режимах эффектов)"""
        if palette_name in self.palettes:
            new_color = self.palettes[palette_name][0]
            self.current_color = new_color
            self.palette = palette_name
            
            if self.is_on:
                if self.current_mode == "static":
                    self.send_color(*new_color)
                else:
                    print(f"[LIGHT] Палитра изменена на {palette_name} (активен режим: {self.current_mode})")
            
            print(f"[LIGHT] Установлена палитра: {palette_name}")
            return True
        return False
    
    
    #эффекты
import serial
import time
import threading
import json
import numpy as np
import pyaudio
from collections import deque
import math

class LightController:
    def __init__(self, port='COM11', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.arduino = None
        self.current_mode = "static"
        self.current_color = (255, 255, 255)
        self.brightness = 100
        self.palette = "white"
        self.is_on = False
        
        # Флаги для управления потоками эффектов
        self._wave_thread = None
        self._wave_running = False
        self._breathing_thread = None
        self._breathing_running = False
        self._monitor_thread = None
        self._monitor_running = False
        
        # Для светомузыки
        self.audio_interface = None
        self.audio_stream = None
        self.is_music_mode = False
        self.audio_data = deque(maxlen=100)
        
        # Параметры ленты
        self.NUM_LEDS = 60  # Количество светодиодов
        
        # Палитры цветов
        self.palettes = {
            "холодная": [(200, 230, 255), (170, 210, 255), (140, 190, 255)],
            "ламповая": [(255, 200, 150), (255, 180, 120), (255, 160, 100)],
            "теплые": [(255, 220, 180), (255, 200, 150), (255, 180, 120)],
            "мятная": [(200, 255, 230), (180, 240, 220), (160, 230, 210)],
            "бархатная": [(150, 100, 200), (130, 80, 180), (110, 60, 160)]
        }
        
        # Цвета по названиям
        self.colors = {
            "белый": (255, 255, 255),
            "красный": (255, 0, 0),
            "зеленый": (0, 255, 0),
            "синий": (0, 0, 255),
            "желтый": (255, 255, 0),
            "фиолетовый": (255, 0, 255),
            "голубой": (0, 255, 255),
            "оранжевый": (255, 165, 0),
            "розовый": (255, 192, 203),
            "мятный": (170, 240, 210),
            "бирюзовый": (64, 224, 208),
            "лавандовый": (230, 230, 250)
        }
        
        # СРАЗУ ПОДКЛЮЧАЕМСЯ И ВЫКЛЮЧАЕМ СВЕТ ПРИ ЗАПУСКЕ
        self._force_turn_off()
        
        print("[LIGHT] Контроллер инициализирован (свет выключен)")
    
    def _force_turn_off(self):
        """Принудительно выключает свет при инициализации"""
        try:
            print("[LIGHT] Принудительно выключаю свет...")
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=0.1)
            time.sleep(2)
            
            # Отправляем команду выключения несколько раз для надежности
            for _ in range(3):
                self.arduino.write(b"0,0,0\n")
                time.sleep(0.1)
            
            self.is_on = False
            print("[LIGHT] Свет принудительно выключен")
            
            # Закрываем соединение - подключимся позже при командах
            self.arduino.close()
            self.arduino = None
            
        except Exception as e:
            print(f"[LIGHT] Ошибка принудительного выключения: {e}")
            self.arduino = None
    
    def __del__(self):
        """Деструктор - закрывает соединение при удалении объекта"""
        self.close_connection()
    
    def close_connection(self):
        """Закрывает соединение с Arduino"""
        if self.arduino:
            try:
                # Выключаем свет перед закрытием
                self.arduino.write(b"0,0,0\n")
                time.sleep(0.1)
                self.arduino.close()
                print("[LIGHT] Соединение с Arduino закрыто, свет выключен")
            except Exception as e:
                print(f"[LIGHT] Ошибка закрытия соединения: {e}")
            self.arduino = None
    
    def _connect_arduino(self):
        """Подключение к Arduino"""
        if self.arduino:
            return True
            
        try:
            print(f"[LIGHT] Подключаюсь к Arduino на {self.port}...")
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=0.1)
            time.sleep(2)
            
            # Убеждаемся, что свет выключен при подключении
            self.arduino.write(b"0,0,0\n")
            time.sleep(0.1)
            
            print(f"[LIGHT] Успешно подключено к Arduino на {self.port}")
            return True
        except Exception as e:
            print(f"[LIGHT] Ошибка подключения к Arduino: {e}")
            self.arduino = None
            return False

    def _stop_all_effects(self):
        """Останавливает все эффекты"""
        print("[LIGHT] Останавливаю все эффекты...")
        
        # Останавливаем волну
        self._wave_running = False
        if self._wave_thread and self._wave_thread.is_alive():
            self._wave_thread.join(timeout=1.0)
        
        # Останавливаем дыхание
        self._breathing_running = False
        if self._breathing_thread and self._breathing_thread.is_alive():
            self._breathing_thread.join(timeout=1.0)
        
        # Останавливаем монитор
        self._monitor_running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        
        # Останавливаем светомузыку (с проверкой атрибутов)
        self.stop_music_mode()

    def _apply_brightness(self, color):
        """Применяет яркость к цвету"""
        r, g, b = color
        brightness_factor = self.brightness / 100.0
        return (
            int(r * brightness_factor),
            int(g * brightness_factor), 
            int(b * brightness_factor)
        )
    
    def send_color(self, r, g, b):
        """Отправка одного цвета на всю ленту"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        if not self.is_on:
            return
        
        try:
            # Применяем яркость
            r, g, b = self._apply_brightness((r, g, b))
            
            # Ограничиваем значения
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            command = f"{r},{g},{b}\n"
            self.arduino.write(command.encode())
            
        except Exception as e:
            print(f"[LIGHT] Ошибка отправки цвета: {e}")
            self.arduino = None

    def send_wave_command(self, base_r, base_g, base_b, t, speed, length):
        """Отправляет команду для волны на Arduino"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        if not self.is_on:
            return
        
        try:
            # Применяем яркость к базовому цвету
            base_r, base_g, base_b = self._apply_brightness((base_r, base_g, base_b))
            
            # Формируем команду для волны
            command = f"WAVE:{base_r},{base_g},{base_b},{t},{speed},{length}\n"
            self.arduino.write(command.encode())
            
        except Exception as e:
            print(f"[LIGHT] Ошибка отправки волны: {e}")
            self.arduino = None
    
    def turn_on(self):
        """Включить свет"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        self.is_on = True
        self.send_color(*self.current_color)
        print("[LIGHT] Свет включен")
    
    def turn_off(self):
        """Выключить свет"""
        if not self.arduino:
            if not self._connect_arduino():
                return
                
        self.is_on = False
        # Отправляем черный цвет для выключения
        try:
            self.arduino.write(b"0,0,0\n")
            time.sleep(0.1)
        except Exception as e:
            print(f"[LIGHT] Ошибка выключения света: {e}")
        print("[LIGHT] Свет выключен")
    
    def set_brightness(self, percent):
        """Установить яркость"""
        self.brightness = max(0, min(100, percent))
        if self.is_on and self.arduino:
            self.send_color(*self.current_color)
        print(f"[LIGHT] Яркость установлена: {self.brightness}%")
    
    def increase_brightness(self, step=10):
        """Увеличить яркость"""
        self.set_brightness(self.brightness + step)
    
    def decrease_brightness(self, step=10):
        """Уменьшить яркость"""
        self.set_brightness(self.brightness - step)
    
    def set_color(self, color_name):
        """Установить цвет по имени (работает даже в режимах эффектов)"""
        if not self.arduino:
            if not self._connect_arduino():
                return False
                
        color_name = color_name.lower()
        print(f"[LIGHT] Пытаюсь установить цвет: {color_name}")
        
        # Поиск в базовых цветах
        if color_name in self.colors:
            new_color = self.colors[color_name]
            self.current_color = new_color
            self.palette = color_name
            
            # Если свет включен, сразу применяем новый цвет
            if self.is_on:
                if self.current_mode == "static":
                    # Просто устанавливаем цвет
                    self.send_color(*new_color)
                else:
                    # В режимах эффектов цвет применится в следующем цикле эффекта
                    print(f"[LIGHT] Цвет изменен на {color_name} (активен режим: {self.current_mode})")
            
            print(f"[LIGHT] Установлен цвет: {color_name}")
            return True
        
        # Поиск в палитрах
        if color_name in self.palettes:
            new_color = self.palettes[color_name][0]
            self.current_color = new_color
            self.palette = color_name
            
            if self.is_on:
                if self.current_mode == "static":
                    self.send_color(*new_color)
                else:
                    print(f"[LIGHT] Палитра изменена на {color_name} (активен режим: {self.current_mode})")
            
            print(f"[LIGHT] Установлена палитра: {color_name}")
            return True
        
        print(f"[LIGHT] Цвет не найден: {color_name}")
        return False
    
    def set_palette(self, palette_name):
        """Установить палитру (работает даже в режимах эффектов)"""
        if palette_name in self.palettes:
            new_color = self.palettes[palette_name][0]
            self.current_color = new_color
            self.palette = palette_name
            
            if self.is_on:
                if self.current_mode == "static":
                    self.send_color(*new_color)
                else:
                    print(f"[LIGHT] Палитра изменена на {palette_name} (активен режим: {self.current_mode})")
            
            print(f"[LIGHT] Установлена палитра: {palette_name}")
            return True
        return False

    # Режимы эффектов
    def start_wave_effect(self):
        """Запуск эффекта бегущей волны"""
        if self.current_mode == "wave":
            return
        
        self._stop_all_effects()
        self.current_mode = "wave"
        self._wave_running = True
        self._wave_thread = threading.Thread(target=self._running_wave_effect, daemon=True)
        self._wave_thread.start()
        print("[LIGHT] Бегущая волна запущена")

    def _running_wave_effect(self):
        """Волна, бегущая по ленте (точный аналог Arduino кода)"""
        t = 0
        WAVE_SPEED = 5
        WAVE_LENGTH = 15
        last_color = self.current_color
        
        print(f"[WAVE] Бегущая волна по {self.NUM_LEDS} светодиодам")
        
        while self._wave_running and self.is_on and self.current_mode == "wave":
            try:
                # Проверяем, не изменился ли цвет
                if self.current_color != last_color:
                    last_color = self.current_color
                    print(f"[WAVE] Базовый цвет изменен на: {last_color}")
                
                # Отправляем команду волны на Arduino
                base_r, base_g, base_b = last_color
                self.send_wave_command(base_r, base_g, base_b, t, WAVE_SPEED, WAVE_LENGTH)
                
                t += WAVE_SPEED
                time.sleep(0.03)  # Задержка 30ms как в Arduino
                
            except Exception as e:
                print(f"[WAVE] Ошибка в бегущей волне: {e}")
                break
        
        print("[LIGHT] Бегущая волна остановлена")

    # Остальные методы остаются без изменений...

    def _sin8(self, x):
        """Аналог sin8 из FastLED - возвращает значение 0-255"""
        import math
        # Нормализуем входное значение
        normalized = (x % 256) / 255.0 * 2 * math.pi
        # Синус от -1 до 1 преобразуем в 0-255
        return int((math.sin(normalized) + 1) * 127.5)

    def _send_led_strip_data(self, led_colors):
        """Отправляет данные для всей ленты светодиодов"""
        if not self.arduino:
            if not self._connect_arduino():
                return
        
        try:
            # Формируем команду для всех светодиодов
            # Формат: "r1,g1,b1;r2,g2,b2;...;rN,gN,bN\n"
            command_parts = []
            for r, g, b in led_colors:
                command_parts.append(f"{r},{g},{b}")
            
            command = ";".join(command_parts) + "\n"
            self.arduino.write(command.encode())
            
        except Exception as e:
            print(f"[LIGHT] Ошибка отправки данных ленты: {e}")

    def start_breathing_effect(self):
        """Запуск эффекта дыхания"""
        if self.current_mode == "breathing":
            return
        
        self._stop_all_effects()
        self.current_mode = "breathing"
        self._breathing_running = True
        self._breathing_thread = threading.Thread(target=self._breathing_effect, daemon=True)
        self._breathing_thread.start()
        print("[LIGHT] Эффект дыхания запущен")

    def _breathing_effect(self):
        """Эффект дыхания"""
        base_color = self.palettes.get(self.palette, [self.current_color])[0]
        step = 0
        last_color = self.current_color
        
        print(f"[BREATHING] Эффект дыхания с базовым цветом: {last_color}")
        
        while self._breathing_running and self.is_on and self.current_mode == "breathing":
            try:
                # Проверяем, не изменился ли цвет
                if self.current_color != last_color:
                    last_color = self.current_color
                    base_color = self.palettes.get(self.palette, [self.current_color])[0]
                    print(f"[BREATHING] Базовый цвет изменен на: {last_color}")
                
                # Синусоидальное изменение яркости
                brightness_factor = (math.sin(step) + 1) / 2  # от 0 до 1
                
                r = int(base_color[0] * brightness_factor)
                g = int(base_color[1] * brightness_factor)
                b = int(base_color[2] * brightness_factor)
                
                self.send_color(r, g, b)
                
                step += 0.1
                time.sleep(0.05)
            except Exception as e:
                print(f"[BREATHING] Ошибка в эффекте дыхания: {e}")
                break
        
        print("[LIGHT] Эффект дыхания остановлен")

    # Остальные методы остаются без изменений...

    def start_music_mode(self):
        """Запуск светомузыки"""
        if self.current_mode == "music":
            return
        
        self._stop_all_effects()
        self.current_mode = "music"
        self.is_music_mode = True
        
        # Инициализируем атрибуты если их нет
        if not hasattr(self, 'audio_interface'):
            self.audio_interface = None
        if not hasattr(self, 'audio_stream'):
            self.audio_stream = None
            
        self._start_audio_processing()
        print("[LIGHT] Режим светомузыки запущен")

    def stop_music_mode(self):
        """Остановка светомузыки"""
        self.is_music_mode = False
        
        # Проверяем существование атрибутов перед использованием
        if hasattr(self, 'audio_stream') and self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            except Exception as e:
                print(f"[LIGHT] Ошибка остановки audio stream: {e}")
        
        if hasattr(self, 'audio_interface') and self.audio_interface:
            try:
                self.audio_interface.terminate()
                self.audio_interface = None
            except Exception as e:
                print(f"[LIGHT] Ошибка остановки audio interface: {e}")
        
        print("[LIGHT] Режим светомузыки остановлен")

    def _start_audio_processing(self):
        """Запуск обработки аудио для светомузыки"""
        try:
            self.audio_interface = pyaudio.PyAudio()
            
            def audio_callback(in_data, frame_count, time_info, status):
                if self.is_music_mode:
                    # Конвертируем аудиоданные в numpy array
                    audio_data = np.frombuffer(in_data, dtype=np.int16)
                    self.audio_data.append(np.mean(np.abs(audio_data)))
                    
                    # Анализ громкости и частот
                    if len(self.audio_data) > 10:
                        volume = np.mean(list(self.audio_data)[-10:])
                        self._process_music_volume(volume)
                
                return (in_data, pyaudio.paContinue)
            
            self.audio_stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                stream_callback=audio_callback
            )
            
            self.audio_stream.start_stream()
            
        except Exception as e:
            print(f"[LIGHT] Ошибка инициализации аудио: {e}")

    def _process_music_volume(self, volume):
        """Обработка громкости для светомузыки"""
        # Нормализуем громкость
        normalized_vol = min(1.0, volume / 10000.0)
        
        # Гамма-коррекция
        gamma = 2.2
        corrected_vol = normalized_vol ** (1/gamma)
        
        # Преобразуем в RGB на основе громкости и текущего цвета
        base_r, base_g, base_b = self.current_color
        
        r = int(base_r * corrected_vol)
        g = int(base_g * corrected_vol)
        b = int(base_b * corrected_vol)
        
        self.send_color(r, g, b)

    def start_monitor_checker(self):
        """Запуск умной подсветки на основе монитора"""
        if self.current_mode == "monitor":
            return
        
        self._stop_all_effects()
        self.current_mode = "monitor"
        self._monitor_running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("[LIGHT] Умная подсветка запущена")

    def _monitor_loop(self):
        """Цикл умной подсветки"""
        try:
            from .monitor_checker import get_stable_color
            
            last_r, last_g, last_b = 50, 50, 50
            
            while self._monitor_running and self.is_on and self.current_mode == "monitor":
                try:
                    r, g, b = get_stable_color()
                    
                    # Плавный переход
                    smooth = 0.4
                    r = int(last_r * (1-smooth) + r * smooth)
                    g = int(last_g * (1-smooth) + g * smooth)
                    b = int(last_b * (1-smooth) + b * smooth)
                    
                    last_r, last_g, last_b = r, g, b
                    self.send_color(r, g, b)
                    
                    time.sleep(0.08)
                    
                except Exception as e:
                    print(f"[MONITOR] Ошибка: {e}")
                    time.sleep(1)
            
            print("[LIGHT] Умная подсветка остановлена")
            
        except ImportError:
            print("[LIGHT] Модуль monitor_checker не найден")

    def stop_monitor_checker(self):
        """Остановка умной подсветки"""
        self._monitor_running = False
        if self.current_mode == "monitor":
            self.current_mode = "static"
            print("[LIGHT] Умная подсветка остановлена")

    def set_static_mode(self):
        """Вернуться к статичному свету"""
        self._stop_all_effects()
        self.current_mode = "static"
        if self.is_on:
            self.send_color(*self.current_color)
        print("[LIGHT] Переключен в статичный режим")