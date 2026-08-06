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

#Show all medicine in list（Vision 3 changed）
def show_all_medicine():
    # Read the latest data
    data = load_data()
    global medicine_list
    medicine_list = data

    #Create a new window
    list_win = tk.Toplevel(window)
    list_win.title("Medicine List")
    list_win.geometry("520x300")

    #Set a list in the new window
    lb = tk.Listbox(list_win, width=55, height=12)
    lb.pack(padx=10,pady=10)

    def refresh_listbox():
        lb.delete(0,tk.END)
        current = load_data()
        if len(data) == 0:
            lb.insert(tk.END, "No medicines have been added yet!")
        else:
            for idx, item in enumerate(current, start=1):
                lb.insert(tk.END, f"{idx}. {item['name']} --- {item['time']}")

    #Delete the medicine in the list
    def delete_selected():
        selected_index = lb.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select one medicine first.")
            return
        pos = selected_index[0]
        current_data = load_data()
        confirm = messagebox.askyesno("confirm Delete", f"Are you sure you want to delete: \n{current_data[pos]['name']}{current_data[pos]['time']}")
        if confirm:
            del current_data[pos]
            save_data(current_data)
            global medicine_list
            medicine_list = current_data
            refresh_listbox()
    #Edit information of seleted medicine 
    def edit_selected():
        #Get the row number of the user's selected item in the list box.
        selected_index = lb.curselection()
        if not selected_index:
            messagebox.showwarning("Please select one record first!")
            return
        pos = selected_index[0]
        current_data = load_data()
        target_item = current_data[pos]

        #Create a pop-up child window for editing
        edit_win = tk.Toplevel(list_win)
        edit_win.title("Edit Recorded Medicine")
        edit_win.geometry("520x300")

        #Editting Window
        tk.Label(edit_win, text="Medicine Name:").pack()#Pre‑fill the original name
        new_name_entry = tk.Entry(edit_win,width=28)
        new_name_entry.insert(0, target_item["name"])#Fill the old name into the input box
        new_name_entry.pack()

        tk.Label(edit_win, text="Time(HH:MM):").pack()#Pre‑fill the original time
        new_time_entry = tk.Entry(edit_win,width=28)
        new_time_entry.insert(0, target_item["time"])#Fill the old time into the input box
        new_time_entry.pack(pady=5)

        #Save the new record
        def save_edit():
            new_name = new_name_entry.get().strip
            new_time = new_time_entry.get().strip
            if not new_name or not new_time:
                messagebox.showwarning("Name or time cannot be empty!")
                return
            #Overwrite the data at the corresponding position in the original list
            current_data[pos]["name"] = new_name
            current_data[pos]["time"] = new_time
            save_data(current_data)
            global medicine_list
            medicine_list = current_data
            refresh_listbox()
            edit_win.destroy()
            messagebox.showinfo("success", "Medicine updated")
        tk.Button(edit_win, text="Save Changes", command=save_edit).pack(pady=8)

    refresh_listbox()
    tk.Button(list_win, text="Edit Selected Item", command=edit_selected, bg="#88bbff").pack(pady=5)
    tk.Button(list_win, text="Delete Selected Item", command=delete_selected, bg="#ff8888").pack(pady=5)
    

# Start Background Thread
monitor_thread = threading.Thread(target=monitor_time, daemon=True)
monitor_thread.start()

#Add Medicine Button    
tk.Button(window, text="Add Medicine", command=add_medicine).pack(pady=10)
#Show All Medicines BUtton (Vision 2 newly added）
tk.Button(window, text="Show All Medicines", command=show_all_medicine).pack(pady=10)




#Message loop(Place it at the end to keep the window displayed)
window.mainloop()