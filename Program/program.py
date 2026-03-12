import tkinter as tk
from tkinter import ttk
import cv2
import os
import csv
from datetime import datetime
import numpy as np

DB_PATH = "D:/Project/WSegImageProcess/Program/database.csv"
ORIGINAL_DIR = "D:/Project/WSegImageProcess/Program/Original"
PROCESSED_DIR = "D:/Project/WSegImageProcess/Program/Processed"

os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def init_database():
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        with open(DB_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "ip", "timestamp"])

class HeaderBar(tk.Frame):
    def __init__(self, master, on_ip_change):
        super().__init__(master, bg="#ddd")
        self.on_ip_change = on_ip_change

        tk.Label(self, text="DroidCam IP:").pack(side=tk.LEFT, padx=5)
        self.ip_combo = ttk.Combobox(self, values=self._load_ips())
        self.ip_combo.pack(side=tk.LEFT, padx=5)
        tk.Button(self, text="Connect", command=self._set_ip).pack(side=tk.LEFT, padx=5)

    def _load_ips(self):
        init_database()
        with open(DB_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ips = [row["ip"] for row in reader if "ip" in row]
        seen = set()
        unique_ips = []
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                unique_ips.append(ip)
        return unique_ips

    def _save_ip(self, ip):
        init_database()
        existing_ips = self._load_ips()
        if ip in existing_ips:
            return
        with open(DB_PATH, newline="", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            last_id = 0
            if len(reader) > 1:
                try:
                    last_id = int(reader[-1][0])
                except ValueError:
                    last_id = 0
        with open(DB_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([last_id + 1, ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        self.ip_combo["values"] = self._load_ips()

    def _set_ip(self):
        ip = self.ip_combo.get()
        if ip:
            self._save_ip(ip)
            self.on_ip_change(ip)


class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WSeg Image Process")
        self.geometry("1000x600")

        # Header bar
        self.header = HeaderBar(self, self.set_ip)
        self.header.pack(fill=tk.X)

        # Main layout: left notebook + right video
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook bên trái
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.original_tab = tk.Frame(self.notebook)
        self.processed_tab = tk.Frame(self.notebook)

        self.notebook.add(self.original_tab, text="Original")
        self.notebook.add(self.processed_tab, text="Processed")

        self.original_label = tk.Label(self.original_tab)
        self.original_label.pack(expand=True)

        self.processed_label = tk.Label(self.processed_tab)
        self.processed_label.pack(expand=True)

        # Video frame bên phải
        self.video_label = tk.Label(main_frame)
        self.video_label.pack(side=tk.RIGHT, expand=True)

        # Buttons
        tk.Button(self, text="Capture", command=self.capture).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self, text="Process", command=self.process_image).pack(side=tk.LEFT, padx=10, pady=10)

        self.stream = None
        self.last_capture_path = None

        self.after(30, self.update_frame)
        
        # Notification panel dưới cùng
        self.notification_label = tk.Label(self, text="Ready", bg="#eee", anchor="w")
        self.notification_label.pack(side=tk.BOTTOM, fill=tk.X)





    def set_ip(self, ip):
        self.stream = cv2.VideoCapture(f"http://{ip}:4747/video")
        self.notification_label.config(text=f"Đã kết nối tới DroidCam IP: {ip}")

    def update_frame(self):
        if self.stream is not None:
            ret, frame = self.stream.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = cv2.resize(cv2image, (640, 480))
                self.photo = tk.PhotoImage(master=self.video_label, data=cv2.imencode('.png', img)[1].tobytes())
                self.video_label.config(image=self.photo)
        self.after(30, self.update_frame)

    def capture(self):
        if self.stream is not None:
            ret, frame = self.stream.read()
            if ret:
                filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.jpg")
                path = os.path.join(ORIGINAL_DIR, filename)
                cv2.imwrite(path, frame)
                self.last_capture_path = path
                self.notification_label.config(text=f"Ảnh gốc đã lưu tại: {path}")

                # Hiển thị preview trong tab Original
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = cv2.resize(img, (400, 300))
                self.original_photo = tk.PhotoImage(master=self.original_label, data=cv2.imencode('.png', img)[1].tobytes())
                self.original_label.config(image=self.original_photo)

    def process_image(self):
        if self.last_capture_path is None:
            self.notification_label.config(text="Chưa có ảnh gốc để xử lý!")
            return

        img = cv2.imread(self.last_capture_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        kernel = np.ones((3, 3), np.uint8)
        sure_bg = cv2.dilate(thresh, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
        ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)

        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        markers = cv2.watershed(img, markers)
        img[markers == -1] = [0, 0, 255]

        filename = datetime.now().strftime("processed_%Y%m%d_%H%M%S.jpg")
        path = os.path.join(PROCESSED_DIR, filename)
        cv2.imwrite(path, img)
        self.notification_label.config(text=f"Ảnh đã xử lý lưu tại: {path}")

        # Hiển thị preview trong tab Processed
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        img = cv2.resize(img, (400, 300))
        self.processed_photo = tk.PhotoImage(master=self.processed_label, data=cv2.imencode('.png', img)[1].tobytes())
        self.processed_label.config(image=self.processed_photo)


if __name__ == "__main__":
    init_database()
    app = AppGUI()
    app.mainloop()
