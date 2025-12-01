from tts_with_rvc import TTS_RVC
import sounddevice as sd
import soundfile as sf
import time
class GelyaSpeach():
    def __init__(self):
        self.tts = TTS_RVC(
                    model_path="models/gelya_voice_1.pth",
                    index_path="logs/added_IVF2611_Flat_nprobe_1_gelya_voice_1_v1.index",
                    device="cuda:0"
                )
    def speach(self, message, max_retries=3):
        for attempt in range(max_retries):
            try:
                path = self.tts(text=message, pitch=12, index_rate=1.4)
                print("▶️ Воспроизведение...")
                data, samplerate = sf.read(path)
                sd.play(data, samplerate)
                sd.wait()
                return True
            except Exception as e:
                print(f"❌ Ошибка (попытка {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        return False
        
# while True:
    
#      message = str(input("Ввод:"))
          
#      gelya = GelyaSpeach()
#      if message == "стоп".lower():
#          break
    
#      else:gelya.speach(message)

