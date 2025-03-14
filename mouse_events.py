import ctypes
import time

# Mouse event constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# Screen resolution
SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)

def move_mouse(x, y):
    """
    Fareyi belirtilen koordinatlara hareket ettirir.
    """
    # Koordinatları ekran ölçeğine göre ayarla
    x = int(x * 65535 / SCREEN_WIDTH)
    y = int(y * 65535 / SCREEN_HEIGHT)
    
    # Fareyi hareket ettir
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)

def click_mouse():
    """
    Sol tıklama yapar.
    """
    time.sleep(1)  # 1 saniye bekle
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)