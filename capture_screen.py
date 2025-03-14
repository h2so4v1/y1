import numpy as np
import cv2
import win32gui
import win32ui
import win32con
import win32api

def get_window_rect(window_title):
    """
    Belirtilen başlığa sahip pencerenin koordinatlarını döndürür.
    """
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        raise Exception(f"Pencere bulunamadı: {window_title}")
    rect = win32gui.GetWindowRect(hwnd)
    return rect

def capture_window(window_title):
    """
    Belirtilen başlığa sahip pencerenin ekran görüntüsünü alır.
    """
    left, top, right, bottom = get_window_rect(window_title)
    width = right - left
    height = bottom - top

    # Pencere cihaz bağlamını oluştur
    hwnd = win32gui.FindWindow(None, window_title)
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Görüntüyü kaydetmek için bir bitmap oluştur
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # BitBlt ile ekran görüntüsünü al
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Bitmap'i numpy array'e çevir
    signedIntsArray = saveBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    # Release DC
    win32gui.ReleaseDC(hwnd, hwndDC)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()

    # BGRA'dan BGR'ye çevir (OpenCV'nin kullandığı format)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    return img_bgr

# Test kodu (devre dışı bırakıldı)
if __name__ == "__main__":
    """
    window_title = "Uygulama Başlığı"  # Buraya ekran görüntüsünü almak istediğiniz uygulamanın başlığını yazın
    try:
        goruntu = capture_window(window_title)
        cv2.imshow("Pencere Goruntusu", goruntu)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(e)
    """