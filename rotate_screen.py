import random
import time
from pynput.keyboard import Key, Controller
import threading

keyboard = Controller()
lock = threading.Lock()

def press_key_random_duration():
    """
    Rastgele bir şekilde "e" veya "q" tuşlarına 1-2 saniye aralığında basılı tutar.
    """
    key = random.choice(['e', 'q'])  # Rastgele "e" veya "q" tuşu seçimi
    hold_time = random.uniform(1, 2)  # 1-2 saniye aralığında rastgele basılı tutma süresi
    time.sleep(1)
    print(f"'{key}' tuşuna {hold_time:.2f} saniye boyunca basılacak.")
    
    with lock:
        keyboard.press(key)
        time.sleep(hold_time)
        keyboard.release(key)
    
    print(f"'{key}' tuşu bırakıldı.")

def rotate_screen(detections_count):
    """
    Ekranda 2 taneden az algılama yapıldığında rastgele "e" veya "q" tuşlarına 1-2 saniye aralığında basılı tutar.
    """
    if detections_count < 2:
        press_key_random_duration()

def rotate_screen_periodically():
    """
    Her 4-6 dakika arasında rastgele "e" veya "q" tuşlarına 1-2 saniye aralığında basılı tutar.
    """
    while True:
        wait_time = random.uniform(240, 360)  # 4-6 dakika aralığında rastgele bekleme süresi
        print(f"{wait_time / 60:.2f} dakika sonra rastgele bir tuşa basılacak.")
        time.sleep(wait_time)  # Belirtilen süre kadar bekle
        press_key_random_duration()

def check_and_rotate_screen(results, model):
    """
    Tespit edilen nesnelerin etiketlerine göre ekranın döndürülüp döndürülmeyeceğini kontrol eder.
    """
    valid_detections_count = 0
    for result in results:
        boxes = result.boxes  # Detection bounding boxes
        for box in boxes:
            cls = box.cls[0]  # Sınıf etiketi
            if model.names[int(cls)] != 'none':  # 'none' etiketi dışındaki nesneleri say
                valid_detections_count += 1

    if valid_detections_count < 2:
        rotate_screen(valid_detections_count)