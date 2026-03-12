import os, csv
from datetime import datetime

DB_PATH = "D:/Project/WSegImageProcess/Program/database.csv"

def init_database():
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        with open(DB_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "ip", "timestamp"])

def load_ips():
    init_database()
    with open(DB_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(dict.fromkeys([row["ip"] for row in reader if "ip" in row]))

def save_ip(ip):
    init_database()
    existing_ips = load_ips()
    if ip in existing_ips:
        return
    with open(DB_PATH, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        last_id = int(reader[-1][0]) if len(reader) > 1 else 0
    with open(DB_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([last_id + 1, ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
