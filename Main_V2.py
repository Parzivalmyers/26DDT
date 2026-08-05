#Import the tkinter library
import tkinter as tk
from tkinter import messagebox
#Vision 2 newly added
import json
import os
import time
import threading
from datetime import datetime


#Store data file name（Vision 2 newly added）
DATA_FILE = "Medicine_data.json"


#Read Saved Data（Vision 2 newly added）
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save Data to File
def save_data(data):
    with open (DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)


#Create the Main Window
window = tk.Tk()
window.title("Medication Reminder")
window.geometry("500x300")


#Create a text label on the window（Vision 2 newly added）
tk.Label(window, text="Medication Reminder", font=("Arial",16)).pack(pady=8)

#Medicine Name Input
tk.Label(window, text= "Medicine Name: ").pack()
med_name = tk.Entry(window, width=30)
med_name.pack()

#Medication Time Input 
tk.Label(window, text="Administration Time(HH:MM): ").pack()
med_time = tk.Entry(window, width=30)
med_time.pack()

#Store Medicine List
medicine_list = load_data()

def add_medicine():
    name = med_name.get().strip ()
    time_str = med_time.get().strip ()
    #Vision 2 newly added
    if not name or not time_str:
        messagebox.showwarning("Warning", "Please fill in all information!")
        return
    medicine_list.append({"name":name,"time":time_str})
    save_data(medicine_list)
    messagebox.showinfo("Successfully",f"{name} | {time_str}")
    med_name.delete(0,tk.END)
    med_time.delete(0,tk.END)
    
#Background Monitoring Function
def monitor_time():
    already_reminded = set()
    while True:
    # Get current time HH:MM
        now = datetime.now().strftime("%H:%M")
        for med in medicine_list:
            med_t = med["time"]
            key = f"{med['name']}_{med_t}"
            if now == med_t and key not in already_reminded:
               # Pop-up Reminder
               window.after(0, lambda m=med:messagebox.showinfo("Medication Reminder",f"It's time to take {m['name']}!"))
               already_reminded.add(key)
            # Cross-day Reset Reminder Flag
            if now == "00:00":
                already_reminded.clear()
        time.sleep(30)

#Show all medicine in list（Vision 2 newly added）
def show_all_medicine():
    # Read the latest data
    data = load_data()
    if len(data) == 0:
        messagebox.showinfo("Medicine List", "No medicines have been added yet!")
        return 
    content = ""
    for idx, item in enumerate(data, start=1):
        content += f"{idx}. Medicine: {item['name']} | Time: {item['time']}\n"
    messagebox.showinfo("All Saved Medicines", content)

# Start Background Thread
monitor_thread = threading.Thread(target=monitor_time, daemon=True)
monitor_thread.start()

#Add Medicine Button    
tk.Button(window, text="Add Medicine", command=add_medicine).pack(pady=10)
#Show All Medicines BUtton (Vision 2 newly added）
tk.Button(window, text="Show All Medicines", command=show_all_medicine).pack(pady=10)




#Message loop(Place it at the end to keep the window displayed)
window.mainloop()