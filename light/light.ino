#include <FastLED.h>

#define LED_PIN     5
#define NUM_LEDS    60
#define BRIGHTNESS  255

CRGB leds[NUM_LEDS];

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  
  // Инициализация черным цветом
  fill_solid(leds, NUM_LEDS, CRGB::Black);
  FastLED.show();
  
  Serial.println("Arduino Ready for LED strip commands");
}

void processWaveCommand(String command) {
  // Команда для волны: "WAVE:base_r,base_g,base_b,t,speed,length"
  if (command.startsWith("WAVE:")) {
    command = command.substring(5); // Убираем "WAVE:"
    
    int params[6];
    int paramIndex = 0;
    int startIndex = 0;
    
    while (paramIndex < 6 && startIndex < command.length()) {
      int endIndex = command.indexOf(',', startIndex);
      if (endIndex == -1) endIndex = command.length();
      
      params[paramIndex] = command.substring(startIndex, endIndex).toInt();
      startIndex = endIndex + 1;
      paramIndex++;
    }
    
    if (paramIndex == 6) {
      int base_r = params[0];
      int base_g = params[1];
      int base_b = params[2];
      int t = params[3];
      int speed = params[4];
      int length = params[5];
      
      // Создаем волну как в оригинальном коде
      for(int i = 0; i < NUM_LEDS; i++) {
        // Создаем волну с помощью синуса
        uint8_t wave = sin8(t + i * length);
        
        // Применяем волну к базовому цвету
        uint8_t r = (base_r * wave) / 255;
        uint8_t g = (base_g * wave) / 255;
        uint8_t b = (base_b * wave) / 255;
        
        leds[i] = CRGB(r, g, b);
      }
      
      FastLED.show();
    }
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("WAVE:")) {
      // Команда для волны
      processWaveCommand(command);
    } else {
      // Старая команда для одного цвета на всю ленту
      int firstComma = command.indexOf(',');
      int secondComma = command.indexOf(',', firstComma + 1);
      
      if (firstComma != -1 && secondComma != -1) {
        int r = command.substring(0, firstComma).toInt();
        int g = command.substring(firstComma + 1, secondComma).toInt();
        int b = command.substring(secondComma + 1).toInt();
        
        fill_solid(leds, NUM_LEDS, CRGB(r, g, b));
        FastLED.show();
      }
    }
  }
  
  delay(10);
}
