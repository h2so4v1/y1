import sys
from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt, QTimer, QPoint)
from PySide6.QtGui import QIntValidator, QIcon, QFont, QCursor
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox, QLabel, QLineEdit, QPushButton, QWidget, QDialog, QToolTip)
from capture_screen import capture_window
from yolo_detection import detect_objects, draw_detections, get_closest_detection_center, load_model
from mouse_events import move_mouse, click_mouse
from metinstones_break import text_break
from rotate_screen import rotate_screen, rotate_screen_periodically, check_and_rotate_screen
from activate_skill import activate_skills, activate_skills_periodically
from captcha_solver import capture_captcha_and_solve
from auto_pickup import auto_pickup
import os
import threading
import time
import pygetwindow as gw
from pywinauto import Application


class AutoSkillDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Skill Settings")
        self.setFixedSize(200, 160)
        self.setStyleSheet("background-color: #333; color: #fff;")

        self.label_7 = QLabel("Auto Skill", self)
        self.label_7.setGeometry(QRect(50, 0, 101, 31))
        font = self.label_7.font()
        font.setFamily("Iceland")
        font.setPointSize(20)
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Interval time:", self)
        self.label.setGeometry(QRect(10, 40, 91, 31))
        font.setPointSize(12)
        self.label.setFont(font)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(QRect(110, 43, 51, 24))
        self.lineEdit.setValidator(QIntValidator(0, 3600))
        self.lineEdit.setStyleSheet("background-color: #555; color: #fff;")

        self.label_2 = QLabel("Skill Keys:", self)
        self.label_2.setGeometry(QRect(10, 80, 71, 21))
        self.label_2.setFont(font)
        self.label_2.setToolTip("Only the keys in the range of 1 to 4.")
        QToolTip.setFont(QFont('SansSerif', 10))

        skill_key_validator = QIntValidator(1, 4, self)

        self.lineEdit_2 = QLineEdit(self)
        self.lineEdit_2.setGeometry(QRect(90, 82, 21, 21))
        self.lineEdit_2.setValidator(skill_key_validator)
        self.lineEdit_2.setStyleSheet("background-color: #555; color: #fff;")

        self.lineEdit_3 = QLineEdit(self)
        self.lineEdit_3.setGeometry(QRect(120, 82, 21, 21))
        self.lineEdit_3.setValidator(skill_key_validator)
        self.lineEdit_3.setStyleSheet("background-color: #555; color: #fff;")

        self.lineEdit_4 = QLineEdit(self)
        self.lineEdit_4.setGeometry(QRect(150, 82, 21, 21))
        self.lineEdit_4.setValidator(skill_key_validator)
        self.lineEdit_4.setStyleSheet("background-color: #555; color: #fff;")

        self.pushButton = QPushButton("ACCEPT", self)
        self.pushButton.setGeometry(QRect(60, 120, 80, 24))
        self.pushButton.setStyleSheet("background-color: #555; color: #fff;")
        self.pushButton.clicked.connect(self.accept)
        


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = None

        self.window_title = None
        self.selected_model_path = None  # Seçilen model yolunu saklamak için değişken

        # Kapatma butonu (❌)
        self.close_button = QPushButton("❌", self)
        self.close_button.setGeometry(self.width() - 40, 0, 30, 30)
        self.close_button.setStyleSheet("background-color: #555; color: #fff;")
        self.close_button.clicked.connect(self.close)

        # Küçültme butonu (➖)
        self.minimize_button = QPushButton("➖", self)
        self.minimize_button.setGeometry(self.width() - 80, 0, 30, 30)
        self.minimize_button.setStyleSheet("background-color: #555; color: #fff;")
        self.minimize_button.clicked.connect(self.showMinimized)

        # Başlat butonu
        self.start_button = self.pushButton
        self.start_button.setStyleSheet("background-color: #555; color: #fff;")
        self.start_button.clicked.connect(self.start_main_functionality)

        # Durdurma butonu
        self.stop_button = self.pushButton_2
        self.stop_button.setStyleSheet("background-color: #555; color: #fff;")
        self.stop_button.clicked.connect(self.stop_main_functionality)

        # PID ComboBox
        self.pid_combobox = self.comboBox
        self.pid_combobox.addItem("Select PID")
        self.pid_combobox.setStyleSheet("background-color: #555; color: #fff;")
        self.pid_combobox.currentIndexChanged.connect(self.update_window_title)

        # ACCEPT butonu
        self.accept_button = self.pushButton_5
        self.accept_button.setStyleSheet("background-color: #555; color: #fff;")
        self.accept_button.clicked.connect(self.focus_and_move_window)

        # Metin kırma süresi için LineEdit
        self.text_break_time_edit = self.lineEdit
        self.text_break_time_edit.setValidator(QIntValidator(0, 999))
        self.text_break_time_edit.setStyleSheet("background-color: #555; color: #fff;")

        self.pause_event = threading.Event()
        self.text_break_event = threading.Event()
        self.text_break_event.set()

        self.skill_activation_interval = 300  # Varsayılan değer
        self.skill_keys = ['1', '2']  # Varsayılan skill tuşları

        # Uygulamaları listeleyen ve PID combobox'ı güncelleyen bir timer oluştur
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pid_list)
        self.timer.start(5000)




    def list_model_folders(self):
        models_path = "models"
        try:
            folders = [f.name for f in os.scandir(models_path) if f.is_dir()]
            return folders
        except FileNotFoundError:
            print(f"'{models_path}' klasörü bulunamadı.")
            return []

    def on_folder_selected(self):
        selected_folder = self.comboBox_2.currentText()
        if selected_folder and selected_folder != "Select Map":
            files = self.list_files_in_folder(selected_folder)
            self.create_or_update_file_combobox(files)

    def list_files_in_folder(self, folder):
        folder_path = os.path.join("models", folder)
        try:
            files = [os.path.splitext(f.name)[0] for f in os.scandir(folder_path) if f.is_file()]
            return files
        except FileNotFoundError:
            print(f"'{folder_path}' directory not found.")
            return []

    def create_or_update_file_combobox(self, files):
        if hasattr(self, 'file_combobox'):
            self.file_combobox.clear()
            self.file_combobox.addItems(files)
        else:
            self.file_combobox = QComboBox(self.groupBox_Farm_3)
            self.file_combobox.setGeometry(QRect(10, 60, 221, 21))
            self.file_combobox.setStyleSheet("background-color: #555; color: #fff;")
            self.file_combobox.addItems(files)
            self.file_combobox.show()

        self.file_combobox.currentIndexChanged.connect(self.on_file_selected)    

    def on_file_selected(self):
        selected_folder = self.comboBox_2.currentText()
        selected_file = self.file_combobox.currentText()
        if selected_folder and selected_file:
            self.selected_model_path = os.path.join("models", selected_folder, selected_file + ".pt")            
            

    def setupUi(self, Widget):
        Widget.setObjectName("MysTBot")
        Widget.setStyleSheet("background-color: #333; color: #fff;")
        Widget.resize(530, 330)  # Yüksekliği artırıldı
        Widget.setMinimumSize(QSize(530, 330))  # Yüksekliği artırıldı
        Widget.setMaximumSize(QSize(530, 330))  # Yüksekliği artırıldı
        Widget.setAutoFillBackground(False)

        self.groupBox_Farm = QGroupBox(Widget)
        self.groupBox_Farm.setObjectName("groupBox_Farm")
        self.groupBox_Farm.setGeometry(QRect(20, 40, 240, 121))

        self.pushButton = QPushButton(self.groupBox_Farm)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(10, 20, 80, 24))
        self.pushButton.setStyleSheet("background-color: #555; color: #fff;")

        self.pushButton_2 = QPushButton(self.groupBox_Farm)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(100, 20, 80, 24))
        self.pushButton_2.setStyleSheet("background-color: #555; color: #fff;")

        self.label = QLabel(self.groupBox_Farm)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 55, 60, 15))

        self.lineEdit = QLineEdit(self.groupBox_Farm)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(QRect(70, 55, 31, 21))
        self.lineEdit.setReadOnly(False)
        self.lineEdit.setValidator(QIntValidator(0, 999))
        self.lineEdit.setStyleSheet("background-color: #555; color: #fff;")

        self.label_2 = QLabel(self.groupBox_Farm)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(130, 100, 71, 16))

        self.groupBox_Features = QGroupBox(Widget)
        self.groupBox_Features.setObjectName("groupBox_Features")
        self.groupBox_Features.setGeometry(QRect(20, 160, 240, 121))

        self.checkBox = QCheckBox(self.groupBox_Features)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setGeometry(QRect(10, 30, 91, 22))

        self.checkBox_2 = QCheckBox(self.groupBox_Features)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_2.setGeometry(QRect(10, 50, 91, 22))

        self.auto_skill_button = QPushButton(self.groupBox_Features)
        self.auto_skill_button.setObjectName("auto_skill_button")
        self.auto_skill_button.setGeometry(QRect(150, 50, 80, 24))
        self.auto_skill_button.setStyleSheet("background-color: #555; color: #fff;")
        self.auto_skill_button.setText("A-S Settings")
        self.auto_skill_button.clicked.connect(self.open_auto_skill_dialog)

        self.checkBox_3 = QCheckBox(self.groupBox_Features)
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_3.setGeometry(QRect(10, 70, 101, 22))

        self.groupBox_Farm_2 = QGroupBox(Widget)
        self.groupBox_Farm_2.setObjectName("groupBox_Farm_2")
        self.groupBox_Farm_2.setGeometry(QRect(270, 40, 240, 121))

        self.pushButton_5 = QPushButton(self.groupBox_Farm_2)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(QRect(10, 55, 71, 21))
        self.pushButton_5.setStyleSheet("background-color: #555; color: #fff;")

        self.comboBox = QComboBox(self.groupBox_Farm_2)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QRect(90, 55, 141, 21))
        self.comboBox.setStyleSheet("background-color: #555; color: #fff;")

        self.label_5 = QLabel(self.groupBox_Farm_2)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(90, 35, 141, 16))

        self.label_6 = QLabel(self.groupBox_Farm_2)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(90, 80, 141, 16))

        self.groupBox_Farm_3 = QGroupBox(Widget)
        self.groupBox_Farm_3.setObjectName("groupBox_Farm_3")
        self.groupBox_Farm_3.setGeometry(QRect(270, 160, 240, 121))

        self.comboBox_2 = QComboBox(self.groupBox_Farm_3)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.setGeometry(QRect(10, 30, 221, 21))
        self.comboBox_2.setEditable(False)
        self.comboBox_2.setDuplicatesEnabled(False)
        self.comboBox_2.setStyleSheet("background-color: #555; color: #fff;")

        self.label_7 = QLabel(Widget)
        self.label_7.setObjectName("label_7")
        self.label_7.setGeometry(QRect(20, 0, 101, 31))
        font = self.label_7.font()
        font.setFamily("Iceland")
        font.setPointSize(20)
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Widget)
        QMetaObject.connectSlotsByName(Widget)

        self.comboBox_2.currentIndexChanged.connect(self.on_folder_selected)

        self.update_model_combobox()

    def update_model_combobox(self):
        folders = self.list_model_folders()
        self.comboBox_2.clear()
        self.comboBox_2.addItem("Select Map")
        self.comboBox_2.addItems(folders)
        self.comboBox_2.setCurrentIndex(0)    

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", "MysTBot", None))
        Widget.setWindowIcon(QIcon("acs.ico"))
        self.groupBox_Farm.setTitle(QCoreApplication.translate("Widget", "Farm", None))
        self.pushButton.setText(QCoreApplication.translate("Widget", "START", None))
        self.pushButton_2.setText(QCoreApplication.translate("Widget", "STOP", None))
        self.label.setText(QCoreApplication.translate("Widget", "Metin sec:", None))
        self.lineEdit.setText("")
        self.label_2.setText(QCoreApplication.translate("Widget", "Killed Stones:", None))
        self.groupBox_Features.setTitle(QCoreApplication.translate("Widget", "Features", None))
        self.checkBox.setText(QCoreApplication.translate("Widget", "Auto Pickup", None))
        self.checkBox_2.setText(QCoreApplication.translate("Widget", "Auto Skill", None))
        self.checkBox_3.setText(QCoreApplication.translate("Widget", "Captcha Solver", None))
        self.groupBox_Farm_2.setTitle(QCoreApplication.translate("Widget", "Client 1024x768", None))
        self.pushButton_5.setText(QCoreApplication.translate("Widget", "ACCEPT", None))
        self.label_5.setText(QCoreApplication.translate("Widget", "Refreshes every 5 seconds", None))
        self.label_6.setText(QCoreApplication.translate("Widget", "1024x768 Client PID input", None))
        self.groupBox_Farm_3.setTitle(QCoreApplication.translate("Widget", "Select Metinstones", None))
        self.label_7.setText(QCoreApplication.translate("Widget", "MysTBot", None))

    def open_auto_skill_dialog(self):
        dialog = AutoSkillDialog()
        if dialog.exec():
            try:
                self.skill_activation_interval = int(dialog.lineEdit.text())
                print("Interval time set to:", self.skill_activation_interval)
            except ValueError:
                print("Geçerli bir interval süresi girin.")
            self.skill_keys = [dialog.lineEdit_2.text(), dialog.lineEdit_3.text(), dialog.lineEdit_4.text()]
            print("Skill keys:", self.skill_keys)

    def update_pid_list(self):
        current_pid = self.pid_combobox.currentText()
        self.pid_combobox.clear()
        self.pid_combobox.addItem("Select PID")
        windows = gw.getWindowsWithTitle('')
        for window in windows:
            if window.title:
                self.pid_combobox.addItem(f"{window.title} ({window._hWnd})", window._hWnd)

        index = self.pid_combobox.findText(current_pid)
        if index != -1:
            self.pid_combobox.setCurrentIndex(index)

    def update_window_title(self):
        selected_pid = self.pid_combobox.currentData()
        if selected_pid:
            self.window_title = selected_pid

    def focus_and_move_window(self):
        if self.window_title and self.window_title != "Select PID":
            try:
                app = Application().connect(handle=self.window_title)
                window = app.window(handle=self.window_title)
                window.set_focus()
                window.move_window(0, 0)
            except Exception as e:
                print(f"Pencere taşınamadı: {e}")
        else:
            print("Lütfen bir pencere seçin.")

    def start_main_functionality(self):
        if self.selected_model_path is None:
            print("Model path is not selected.")
            return

        self.model = load_model(self.selected_model_path)        
        
        if not self.window_title or self.window_title == "Select PID":
            print("Lütfen bir pencere seçin.")
            return

        try:
            self.text_break_time = int(self.text_break_time_edit.text())
        except ValueError:
            print("Geçerli bir metin kırma süresi girin.")
            return
        

        self.captcha_check_interval = 0.1



        if self.checkBox_2.isChecked():
            threading.Thread(
                target=activate_skills_periodically,
                args=(self.skill_activation_interval, self.pause_event, self.text_break_event, self.skill_keys),
                daemon=True
            ).start()

        if self.checkBox_3.isChecked():
            threading.Thread(target=capture_captcha_and_solve, args=(self.window_title, capture_window, move_mouse, click_mouse), daemon=True).start()

        threading.Thread(target=rotate_screen_periodically, daemon=True).start()

        self.main_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.main_thread.start()

    def stop_main_functionality(self):
        self.pause_event.set()

    def main_loop(self):
        while not self.pause_event.is_set():
            try:
                print("Ekran görüntüsü alınıyor...")
                image = capture_window(self.window_title)

                print("Nesne tespiti yapılıyor...")
                results = detect_objects(image, self.model)

                num_detections = sum(1 for result in results for box in result.boxes if self.model.names[int(box.cls[0])] != 'none')
                print(f"{num_detections} nesne tespit edildi.")

                if num_detections > 0:
                    print("Tespit edilen nesneler çiziliyor...")
                    image_with_detections = draw_detections(image, results, self.model)

                    print("Ekranın ortasına en yakın nesne bulunuyor...")
                    closest_center = get_closest_detection_center(image, results, self.model)

                    if closest_center:
                        print(f"Fare {closest_center} koordinatlarına hareket ettiriliyor...")
                        move_mouse(closest_center[0], closest_center[1])

                        print("Fare tıklanıyor...")
                        click_mouse()

                        self.text_break_event.clear()
                        text_break(self.text_break_time)
                        self.text_break_event.set()

                        if self.checkBox.isChecked():
                            auto_pickup()
                    else:
                        print("Ekranın ortasına yakın nesne bulunamadı.")

                check_and_rotate_screen(results, self.model)

            except Exception as e:
                print(f"Hata: {e}")

            if self.checkBox_3.isChecked():
                capture_captcha_and_solve(self.window_title, capture_window, move_mouse, click_mouse)

            time.sleep(self.captcha_check_interval)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.oldPos is not None:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()


    def mouseReleaseEvent(self, event):
        self.oldPos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())