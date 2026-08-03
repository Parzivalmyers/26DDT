#Import the tkinter library
import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = "Medicine_data.json"

#Read Saved Data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return

# Save Data to File
def save_data(data):
    with open (DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)


#Create the Main Window
window = tk.Tk()
window.title("Medication Reminder")
window.geometry("500x300")

label = tk.Label(
    window,
    text="Medication Reminder",
    font=("Arial", 16),
    
)
label.pack(pady=30)

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
    name = med_name.get()
    time_str = med_time.get()
    #Vision 2 newly added
    if name == "" or time_str == "":
        messagebox.showwarning("Warning", "Name or time cannot be empty!")
        return
    medicine_list.append({"name":name,"time":time_str})
    messagebox.showinfo("Successful",f"Added:{name} {time_str}")
    med_name.delete(0,tk.END)
    med_time.delete(0,tk.END)
    

#Add Medicine Button    
tk.Button(window, text="Add Medicine", command=add_medicine).pack(pady=10)
    

#Message loop(Place it at the end to keep the window displayed)
window.mainloop()