import tkinter as tk
from tkinter import ttk
from database import load_ips, save_ip

class HeaderBar(tk.Frame):
    def __init__(self, master, on_ip_change):
        super().__init__(master, bg="#ddd")
        self.on_ip_change = on_ip_change

        tk.Label(self, text="DroidCam IP:").pack(side=tk.LEFT, padx=5)
        self.ip_combo = ttk.Combobox(self, values=load_ips())
        self.ip_combo.pack(side=tk.LEFT, padx=5)
        tk.Button(self, text="Connect", command=self._on_connect).pack(side=tk.LEFT, padx=5)

    def _on_connect(self):
        ip = self.ip_combo.get()
        if ip:
            save_ip(ip)  # lưu IP vào database.csv
            self.on_ip_change(ip)  # gọi hàm set_ip(ip) bên AppGUI
