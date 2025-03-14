from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

def auto_pickup():
    """
    Otomatik eşya toplama işlemini gerçekleştirir.
    """
    print("Eşyalar toplanıyor...")
    
    keyboard.press('"')
    time.sleep(0.1)
    keyboard.release('"')
    time.sleep(0.1)  # Kısa bir bekleme süresi
    
    keyboard.press('"')
    time.sleep(0.1)
    keyboard.release('"')
    time.sleep(0.1)  # Kısa bir bekleme süresi
    
    keyboard.press('"')
    time.sleep(0.1)
    keyboard.release('"')
    time.sleep(0.1)  # Kısa bir bekleme süresi
    
    print("Eşyalar toplandı.")