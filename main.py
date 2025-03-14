from capture_screen import capture_window
from yolo_detection import detect_objects, draw_detections, get_closest_detection_center, load_model
from mouse_events import move_mouse, click_mouse
from metinstones_break import text_break
from rotate_screen import rotate_screen, rotate_screen_periodically, check_and_rotate_screen
from activate_skill import activate_skills, activate_skills_periodically
from captcha_solver import capture_captcha_and_solve
from auto_pickup import auto_pickup
import threading
import time

def main():
    window_title = "Asgard"  # Buraya ekran görüntüsünü almak istediğiniz uygulamanın başlığını yazın
    text_break_time = 6  # Metin kırma süresi (saniye olarak)
    skill_activation_interval = 300  # Skilleri aktif hale getirme süresi (saniye olarak)
    captcha_check_interval = 0.1  # CAPTCHA kontrol süresi (saniye olarak)

    # YOLO modelini yükle
    model = load_model()

    pause_event = threading.Event()
    text_break_event = threading.Event()
    text_break_event.set()  # Başlangıçta metin kırma işlemi olmadığını belirtmek için set

    # Bot başlatıldığında ilk olarak skilleri aktif hale getir ve binekten inip tekrar bin
    activate_skills(pause_event, text_break_event)

    # Skillerin periyodik olarak aktif hale getirilmesi için bir thread oluştur ve hemen çalıştır
    threading.Thread(target=activate_skills_periodically, args=(skill_activation_interval, pause_event, text_break_event), daemon=True).start()

    # Periyodik ekran döndürme işlemi için bir thread oluştur
    threading.Thread(target=rotate_screen_periodically, daemon=True).start()
    
    while True:
        try:
            if not pause_event.is_set():
                print("Ekran görüntüsü alınıyor...")
                # Ekran görüntüsünü al
                image = capture_window(window_title)
                
                print("Nesne tespiti yapılıyor...")
                # Nesne tespiti yap
                results = detect_objects(image, model)
                
                num_detections = sum(1 for result in results for box in result.boxes if model.names[int(box.cls[0])] != 'none')
                print(f"{num_detections} nesne tespit edildi.")
                
                if num_detections > 0:
                    print("Tespit edilen nesneler çiziliyor...")
                    # Tespit edilen nesneleri çiz
                    image_with_detections = draw_detections(image, results, model)
                    
                    print("Ekranın ortasına en yakın nesne bulunuyor...")
                    # Ekranın ortasına en yakın tespit edilen nesnenin merkezini al
                    closest_center = get_closest_detection_center(image, results, model)
                    
                    if closest_center:
                        print(f"Fare {closest_center} koordinatlarına hareket ettiriliyor...")
                        # Fareyi nesnenin merkezine hareket ettir
                        move_mouse(closest_center[0], closest_center[1])
                        
                        print("Fare tıklanıyor...")
                        # Fareyi tıklama işlemi
                        click_mouse()
                        
                        # Metin kırma süresi sırasında skill açılmasını engelle
                        text_break_event.clear()  # Metin kırma işleminin başladığını belirt
                        text_break(text_break_time)
                        text_break_event.set()  # Metin kırma işleminin bittiğini belirt
                        
                        # Metin kırma süresinin sonunda otomatik eşya toplama fonksiyonunu çağır
                        auto_pickup()
                    else:
                        print("Ekranın ortasına yakın nesne bulunamadı.")
                
                # Tespit edilen nesnelere göre ekranı döndürme işlemini kontrol et
                check_and_rotate_screen(results, model)
                
        except Exception as e:
            print(f"Hata: {e}")

        # CAPTCHA çözme işlemini periyodik olarak çalıştır
        capture_captcha_and_solve(window_title, capture_window, move_mouse, click_mouse)
        time.sleep(captcha_check_interval)  # CAPTCHA kontrol süresi

if __name__ == "__main__":
    main()