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
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            #Return an empty list when the JSON file is corrupted to prevent the program from crashing.(Vision 3 newly added)
            print("Warning: The data file is corrupted, reset to an empty list")
            return []
    return []

# Save Data to File
def save_data(data):
    with open (DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)


#Create the Main Window
window = tk.Tk()
window.title("Medication Reminder")
window.geometry("600x500")
window.minsize(600, 500)#Main window minimum size

#Create a text label on the window（Vision 2 newly added）
tk.Label(window, text="Medication Reminder", font=("Arial",16)).pack(pady=8)

#Medicine Name Input
tk.Label(window, text= "Medicine Name:").pack()
med_name = tk.Entry(window, width=30)
med_name.pack()

#Medication Time Input 
tk.Label(window, text="Administration Time(HH:MM, accept multiple entries separated by commas. )").pack()
med_time = tk.Entry(window, width=30)
med_time.pack()

#Medication Dosage Input
tk.Label(window, text= "Dosage").pack()
med_name = tk.Entry(window, width=30)
med_name.pack()

#Reminder Date Input
tk.Label(window, text= "Reminder Date (YYYY-MM-DD)").pack()
med_name = tk.Entry(window, width=30)
med_name.pack()

#Note Input
tk.Label(window, text= "Note (Optional)").pack()
med_name = tk.Entry(window, width=30)
med_name.pack()

#Store Medicine List
medicine_list = load_data()

#Track opened list windows(Vision 3 newly added)
list_window_ref = None# Save the reference to the list window
list_refresh_func = None# Save the refresh function for the list window

#Refresh the opened list window
def refresh_opened_list():
    global list_refresh_func
    if list_refresh_func is not None:
        try:
            list_refresh_func()
        except Exception as e:
            # Reset the reference if the window has been closed
            print(f"Error occurred while refreshing the list: {e}")
            list_refresh_func = None

def add_medicine():
    name = med_name.get().strip ()
    time_str = med_time.get().strip ()
    dosage = med_dosage.get().strip ()
    reminder_date = med_date.get().strip ()
    note = med_note.get().strip ()
    #Vision 2 newly added
    if not name or not time_str or not dosage or not reminder_date:
        messagebox.showwarning("Warning", "Please fill in all information!")
        return

    #Allow multiple times eg. 12:20,14:10
    times = [item.strip() for item in time_str.split(",") if item.strip()]

    if not times:
        messagebox.showwarning("Invalid Time", "Please enter at least one time.")
        return

    #Validate time form
    for one_time in items:
        try:
            datetime.strptime(one_time, "%H:%M")
        except ValueError:
            messagebox.showwarning("Invalid Time", f"Invalid time: {one_time}\nPlease follow HH:MM form")
        return

    #Validate date form
    try:
        selected_date = datetime.strptime(reminder_date, "%Y-%m-%d").date()
        if selected_date < datetime.today().date():
            messagebox.showwarning("Invalid Date", "Please enter today or a future date.")
            return

    except ValueError:
        messagebox.showwarning("Invalid Date", "Please follow YYYY-MM-DD form")
        return
    
    medicine_list.append({"name":name,"time": ",".join(times), "dosage": dosage, "date": reminder_date, "note": note})
    save_data(medicine_list)
    messagebox.showinfo("Successfully",f"You will be reminded to take{dosage} {name} on{reminder_date} at {','.join(times)}.\n"f"Note: {note or 'None'}")
    med_name.delete(0,tk.END)
    med_time.delete(0,tk.END)
    med_dosage.delete(0,tk.END)
    med_date.delete(0,tk.END)
    med_note.delete(0,tk.END)
    #Refresh the opened list window after adding the medicine(Vision 3 newly added)
    refresh_opened_list()

    
#Background Monitoring Function
def monitor_time():
    already_reminded = set()
    while True:
    # Get current date and time 
        now_dt = datetime.now()
        today = now_dt.strftime("%Y-%m-%d")
        now = now_dt.strftime("%H:%M")

        #Read multiple time from the same record.
        for med in medicine_list:
            med_times = [
                item.strip()
                for item in med.get("time", "").split(",")
                if item.strip()
            ]

            #Aviod 
            if med.get("date","") != today:
                continue

            #Check every recorded time independently.
            for med_t in med_times:
                key = f"{med.get('name', '')}_{today}_{med_t}"
                if now == med_t and key not in already_reminded:
                    
                    #Optional show the note
                    note = med.get("note", "")
                    # Pop-up Reminder
                    window.after(0, lambda m=med, d=dosage, n=note, t=med_t:messagebox.showinfo("Medication Reminder",f"It's time to take{d} {m.get['name','']}!\n" f"Note: {n or 'None'}"))
                    already_reminded.add(key)
        # Cross-day Reset Reminder Flag
        if now == "00:00":
            already_reminded.clear()
        time.sleep(30)

#Show all medicine in list（Vision 3 newly added）
def show_all_medicine():
    #Reference global variables
    global list_window_ref, list_refresh_func
    # Read the latest data
    data = load_data()
    global medicine_list
    medicine_list = data

    #If the window already exists, refresh it and bring it to the foreground directly.
    if list_window_ref is not None and list_window_ref.winfo_exists():
        list_window_ref.lift()
        refresh_opened_list()
        return

    #Create a new window
    list_win = tk.Toplevel(window)
    list_win.title("Medicine List")
    list_win.geometry("600x500")
    #List window minimum size
    list_win.minsize(600,500)

    #Save window reference
    list_window_ref = list_win

    #Set a list in the new window
    lb = tk.Listbox(list_win, width=55, height=12)
    lb.pack(padx=10,pady=10, fill=tk.BOTH, expand=True)

    def refresh_listbox():
        lb.delete(0,tk.END)
        current = load_data()
        if len(current) == 0:
            lb.insert(tk.END, "No medicines have been added yet!")
        else:
            for idx, item in enumerate(current, start=1):
                lb.insert(tk.END, 
                          f"{idx}. {item.get('name', '')} --- {item.get('date', 'Not set')}"
                          f"Times: {item.get('time', '')} --- Dosage: {item.get('dosage', 'Not set')}"
                          f"Note: {item.get('note', '')} --- {item.get('date', 'Not set')}"
                          )

    #Save the refresh function to a global variable
    list_refresh_func = refresh_listbox

    #Delete the medicine in the list
    def delete_selected():
        selected_index = lb.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select one medicine first.")
            return
        pos = selected_index[0]
        current_data = load_data()
        #Fundamentally prevent the IndexError‑list‑out‑of‑range error
        if pos >= len(current_data):
            messagebox.showerror("Error", "Invalid Operation")
            refresh_listbox()
            return
        confirm = messagebox.askyesno("confirm Delete", f"Are you sure you want to delete: \n{current_data[pos]['name']} {current_data[pos]['time']}")
        if confirm:
            del current_data[pos]
            save_data(current_data)
            global medicine_list
            medicine_list = current_data
            refresh_listbox()
            #Refresh all opened list windows after deletion
            refresh_opened_list()

    #Edit information of seleted medicine 
    def edit_selected():
        #Get the row number of the user's selected item in the list box.
        selected_index = lb.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select one record first!")
            return
        pos = selected_index[0]
        current_data = load_data()
        #Fundamentally prevent the IndexError‑list‑out‑of‑range error
        if pos >= len(current_data):
            messagebox.showerror("Error", "The record no longer exists, refresh list")
            refresh_listbox()
            return
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
            new_name = new_name_entry.get().strip()
            new_time = new_time_entry.get().strip()
            new_dosage = new_dosage_entry.get().strip()
            new_date = new_date_entry.get().strip()
            new_note = new_note_entry.get().strip()

            if not new_name or not new_time:
                messagebox.showwarning("Name, time,dosage and date cannot be empty!")
                return

            #Validate every edited reminder time.

            #Overwrite the data at the corresponding position in the original list
            current_data[pos]["name"] = new_name
            current_data[pos]["time"] = new_time
            save_data(current_data)
            global medicine_list
            medicine_list = current_data
            refresh_listbox()
            edit_win.destroy()
            messagebox.showinfo("success", "Medicine updated")
            #Refresh all opened list windows after editing
            refresh_opened_list()

        tk.Button(edit_win, text="Save Changes", command=save_edit).pack(pady=8)

    #Vision 3 newly added
    refresh_listbox()
    tk.Button(list_win, text="Edit Selected Item", command=edit_selected, bg="#88bbff").pack(pady=5)
    tk.Button(list_win, text="Delete Selected Item", command=delete_selected, bg="#ff8888").pack(pady=5)

    #Clean up global references when the window is closed
    def on_list_window_close():
        global list_window_ref, list_refresh_func
        list_window_ref = None
        list_refresh_func = None
        list_win.destroy()

    list_win.protocol("WM_DELETE_WINDOW", on_list_window_close)
    

# Start Background Thread
monitor_thread = threading.Thread(target=monitor_time, daemon=True)
monitor_thread.start()

#Add Medicine Button    
tk.Button(window, text="Add Medicine", command=add_medicine).pack(pady=10)
#Show All Medicines BUtton (Vision 2 newly added）
tk.Button(window, text="Show All Medicines", command=show_all_medicine).pack(pady=10)





#Message loop(Place it at the end to keep the window displayed)
window.mainloop()