import cv2
import numpy as np
import easyocr
from rapidfuzz import fuzz
import time

# CAPTCHA şablonu
TEMPLATE_PATH = "captcha_template.png"
reader = easyocr.Reader(['en'])  # OCR motoru

def find_captcha_region(full_screenshot):
    """Ekran görüntüsünde CAPTCHA alanını bulur ve koordinatlarını döndürür."""
    full_screenshot_cv = np.array(full_screenshot)
    full_screenshot_cv = cv2.cvtColor(full_screenshot_cv, cv2.COLOR_RGB2BGR)
    
    captcha_template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_COLOR)
    
    if captcha_template is None:
        print("⚠ CAPTCHA şablonu bulunamadı!")
        return None
    
    result = cv2.matchTemplate(full_screenshot_cv, captcha_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    threshold = 0.4
    if max_val >= threshold:
        captcha_x, captcha_y = max_loc
        captcha_w, captcha_h = captcha_template.shape[1], captcha_template.shape[0]
        print("✅ CAPTCHA ekranı bulundu!")
        return (captcha_x, captcha_y, captcha_w, captcha_h)
    
    print("❌ CAPTCHA bulunamadı!")
    return None

def perform_ocr_and_click(captcha_region, full_screenshot, move_mouse, click_mouse):
    """OCR işlemi yapar ve doğru kutuyu bulup mouse ile tıklar."""
    captcha_x, captcha_y, captcha_w, captcha_h = captcha_region

    captcha_screenshot = np.array(full_screenshot)[captcha_y:captcha_y+captcha_h, captcha_x:captcha_x+captcha_w]
    
    results = reader.readtext(captcha_screenshot)
    detected_texts = []
    target_text = None

    for (bbox, text, prob) in results:
        detected_texts.append((text, bbox))

        if "pictures" in text and "Select" in text:
            words = text.split()
            try:
                start_index = words.index("pictures") + 1
                end_index = words.index("Select")
                if start_index < end_index:
                    target_text = " ".join(words[start_index:end_index]).strip()
            except ValueError:
                pass

    if not target_text:
        print("⚠ Hedef metin bulunamadı!")
        return
    
    print(f"🎯 Hedef Metin: {target_text}")

    max_similarity = 0
    best_match_coords = None

    for text, bbox in detected_texts:
        similarity = fuzz.ratio(text.upper().replace(" ", ""), target_text.upper().replace(" ", ""))

        if similarity > max_similarity:
            max_similarity = similarity
            best_match_coords = bbox

    if best_match_coords:
        (top_left, _, bottom_right, _) = best_match_coords
        center_x = (top_left[0] + bottom_right[0]) // 2
        center_y = (top_left[1] + bottom_right[1]) // 2

        absolute_x = captcha_x + center_x
        absolute_y = captcha_y + center_y

        # Mouse'u hareket ettir ve tıkla
        move_mouse(absolute_x, absolute_y)
        time.sleep(0.2)
        click_mouse()
        print(f"✅ '{target_text}' bulundu ve tıklandı!")
    else:
        print("❌ Hedef metin eşleşen bir kutu bulunamadı!")

def capture_captcha_and_solve(app_name, get_app_screenshot, move_mouse, click_mouse):
    """Hedef uygulama içinde CAPTCHA ekranını bulur, OCR yapar ve tıklar."""
    full_screenshot = get_app_screenshot(app_name)
    
    if full_screenshot is None:
        return
    
    captcha_region = find_captcha_region(full_screenshot)
    
    if captcha_region:
        print("📷 CAPTCHA görüntüsü alındı, OCR işlemi başlatılıyor...")
        perform_ocr_and_click(captcha_region, full_screenshot, move_mouse, click_mouse)
    else:
        print("🚫 CAPTCHA bulunamadı, tekrar deniyor...")