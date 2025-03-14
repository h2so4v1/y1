import time

def text_break(wait_time):
    """
    Metin kırma süresi için belirtilen süre kadar bekler.
    """
    print(f"Metin kırma süresi olarak {wait_time} saniye bekleniyor...")
    time.sleep(wait_time)