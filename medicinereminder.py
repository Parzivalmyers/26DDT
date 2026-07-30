import tkinter as tk
from tkinter import ttk, messagebox
import json 
import os 
import time 
import threading
from datetime import datetime
import sys

#Mac system Notification(Optional)
if sys.platform == "darwin":
    try:
        from Foundation import NSUserNotification
        from Foundation import NSUserNotificationCenter 
        MAC_NOTIFY = True
    except ImportError:
        MAC_NOTIFY = False
else:
    MAC_NOTIFY = False

DATA_FILE = os.path.join(os.path.dirname(__file__), "medicines.json")

#Read local JSON medicine reminder data upon program startup
def load_medicines():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

#Improve file readability
def save_medicines(meds):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(meds,f,ensure_ascii=False, indent=2)


def mac_notify(title,message):
    """Send Mac system Notification"""
    if sys.platform == "darwin":
        if MAC_NOTIFY:
            notification = NSUserNotification.alloc().init()
            notification.satTitle_(title)
            notification.setInformativeText_(message)
            center = NSUserNotificationCenter.defaultUserNotificationCenter()
            center.deliverNotification_(notification)
        else:
            #Fallback Solution: Use osascript
            os.system(
                f'''osascript -e 'display notification "{message}" with title "{title}" sound name "Glass'''

            )

class MedReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medication Reminder")
        self.root.geometry("520*480")
        self.root.resizable(False, False)

        self.medicines = load_medicines()
        self.notified_today = set() #Record entries that have been reminded today to avoid duplicate reminders

        self._build_ui()
        self._refresh_list()

        #Start Background Check Thread
        self.running = True
        self.check_thread = threading.Thread(target=self._check_reminders, da)




        
   
        



            