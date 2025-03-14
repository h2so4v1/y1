from ultralytics import YOLO
import cv2

# YOLOv8 modelini yükle
def load_model(model_path):
    """
    YOLOv8 modelini yükler.
    """
    return YOLO(model_path)  # Eğittiğiniz model dosyasının ismini ve yolunu belirtin

# Belirli bir güven faktörünün altındaki tespitleri göz ardı etmek için kullanılan eşik değeri
CONFIDENCE_THRESHOLD = 0.5

def detect_objects(image, model):
    """
    Görüntü üzerinde nesne tespiti yapar.
    """
    results = model(image)
    return results

def draw_detections(image, results, model):
    """
    Tespit edilen nesneleri görüntü üzerinde çizer.
    """
    for result in results:
        boxes = result.boxes  # Detection bounding boxes
        for box in boxes:
            conf = box.conf[0]  # Güven skoru
            cls = box.cls[0]  # Sınıf etiketi
            label = f"{model.names[int(cls)]} {conf:.2f}"

            if conf < CONFIDENCE_THRESHOLD or model.names[int(cls)] == 'none':
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Koordinatları al

            # Dikdörtgen çiz
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return image

def get_closest_detection_center(image, results, model):
    """
    Ekranın ortasına en yakın tespit edilen nesnenin merkezini döndürür.
    """
    img_height, img_width, _ = image.shape
    screen_center = (img_width // 2, img_height // 2)

    closest_center = None
    min_distance = float('inf')

    for result in results:
        boxes = result.boxes  # Detection bounding boxes
        for box in boxes:
            conf = box.conf[0]  # Güven skoru
            cls = box.cls[0]  # Sınıf etiketi

            if conf < CONFIDENCE_THRESHOLD or model.names[int(cls)] == 'none':
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Koordinatları al
            center = ((x1 + x2) // 2, (y1 + y2) // 2)  # Nesnenin merkezi

            # Ekranın ortasına olan mesafeyi hesapla
            distance = ((center[0] - screen_center[0]) ** 2 + (center[1] - screen_center[1]) ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                closest_center = center

    return closest_center