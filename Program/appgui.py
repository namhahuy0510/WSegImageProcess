import tkinter as tk
from tkinter import ttk
import cv2, os
from datetime import datetime
import numpy as np
from headerbar import HeaderBar
import pipeline

ORIGINAL_DIR = "D:/Project/WSegImageProcess/Program/Original"
PROCESSED_DIR = "D:/Project/WSegImageProcess/Program/Processed"
os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WSeg Image Process - Pipeline Full")
        self.geometry("1200x700")

        self.header = HeaderBar(self, self.set_ip)
        self.header.pack(fill=tk.X)

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.labels = {}
        steps = ["Original","Grayscale","Blur","Threshold","Distance","Marker","Watershed"]
        for step in steps:
            frame = tk.Frame(self.notebook)
            label = tk.Label(frame, text=f"{step} preview")
            label.pack(expand=True)
            self.notebook.add(frame, text=step)
            self.labels[step] = label

        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=5)
        tk.Button(button_frame,text="Capture",command=self.capture).pack(side=tk.LEFT,padx=5)
        tk.Button(button_frame,text="Run Pipeline",command=self.run_pipeline).pack(side=tk.LEFT,padx=5)

        self.notification_label = tk.Label(self,text="Ready",bg="#eee",anchor="w")
        self.notification_label.pack(side=tk.BOTTOM,fill=tk.X)

        self.last_capture_path=None
        self.stream=None

        self.video_label = tk.Label(main_frame)
        self.video_label.pack(side=tk.RIGHT, expand=True)

    def set_ip(self, ip):
        self.stream = cv2.VideoCapture(f"http://{ip}:4747/video")
        if not self.stream.isOpened():
            self.notification_label.config(text=f"Không kết nối được tới DroidCam IP: {ip}")
        else:
            self.notification_label.config(text=f"Đã kết nối tới DroidCam IP: {ip}")
            self.after(30, self.update_frame)

    def update_frame(self):
        if self.stream is not None:
            ret, frame = self.stream.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = cv2.resize(cv2image, (640, 480))
                photo = tk.PhotoImage(master=self.video_label,
                                      data=cv2.imencode('.png', img)[1].tobytes())
                self.video_label.config(image=photo)
                self.video_label.image = photo
        self.after(30, self.update_frame)

    def show_step(self,img,step):
        if img is None: return
        if len(img.shape)==2: img=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
        img=cv2.resize(img,(400,300))
        photo=tk.PhotoImage(master=self.labels[step],data=cv2.imencode('.png',img)[1].tobytes())
        self.labels[step].config(image=photo)
        self.labels[step].image=photo
        self.notification_label.config(text=f"{step} hoàn thành")

    def capture(self):
        if self.stream is not None:
            ret, frame = self.stream.read()
            if ret:
                filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.jpg")
                path = os.path.join(ORIGINAL_DIR, filename)
                cv2.imwrite(path, frame)
                self.last_capture_path = path
                self.show_step(frame, "Original")
                self.notification_label.config(text=f"Ảnh gốc đã lưu tại: {path}")
        else:
            self.notification_label.config(text="Chưa kết nối camera để chụp")


    def run_pipeline(self):
        if not self.last_capture_path:
            self.notification_label.config(text="Chưa có ảnh gốc để chạy pipeline!")
            return
        img=cv2.imread(self.last_capture_path)
        gray=pipeline.grayscale(img); self.show_step(gray,"Grayscale")
        blur=pipeline.blur(gray); self.show_step(blur,"Blur")
        thresh=pipeline.threshold(blur); self.show_step(thresh,"Threshold")
        dist=pipeline.distance(thresh); self.show_step(dist,"Distance")
        markers=pipeline.marker(thresh); self.show_step(np.uint8(markers*20),"Marker")
        result=pipeline.watershed(img,markers)
        filename=datetime.now().strftime("processed_%Y%m%d_%H%M%S.jpg")
        path=os.path.join(PROCESSED_DIR,filename)
        cv2.imwrite(path,result)
        self.show_step(result,"Watershed")
        self.notification_label.config(text=f"Pipeline hoàn thành, ảnh lưu tại: {path}")
