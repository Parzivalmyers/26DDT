#Import the tkinter library
import tkinter as tk
from tkinter import messagebox, ttk
#Vision 2 newly added
import json
import os
import time
import threading
from datetime import datetime, timedelta


#Store data file name（Vision 2 newly added）
DATA_FILE = "Medicine_data.json"


#Read Saved Data（Vision 2 newly added）
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            #Add reminded_times to old medicine records
            has_updated_data = False

            for medicine in data:
                #Reminder Completion Records
                if "reminded_times" not in medicine:
                    medicine["reminded_times"] = []
                    has_updated_data = True

                #Repeat type
                #Just once
                if "repeat_type" not in medicine:
                    medicine["repeat_type"] = "Once"
                    has_updated_data = True

                #Repeat by selected weekdays
                if "weekdays" not in medicine:
                    medicine["weekdays"] = []
                    has_updated_data = True

                #Consecutive reminder days
                if "consecutive_days" not in medicine:
                    medicine["consecutive_days"] = 1
                    has_updated_data = True
                    

            #Save the upgraded old records back to JSON
            if has_updated_data:
                save_data(data)

            return data

        except json.JSONDecodeError:
            #Return an empty list when the JSON file is corrupted to prevent the program from crashing.(Vision 3 newly added)
            print("Warning: The data file is corrupted, reset to an empty list")
            return []

    return []

# Save Data to File
def save_data(data):
    with open (DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)


#Create the Window
window = tk.Tk()
window.title("Medication Reminder")
window.geometry("600x500")
window.minsize(600, 500)#Window minimum size

#Main menu page
main_menu_frame = tk.Frame(window)

#Add reminder page
add_reminder_frame = tk.Frame(window)

#Create a text label on the window（Vision 2 newly added）
tk.Label(add_reminder_frame, text="Add Medication Reminder", font=("Arial",16)).pack(pady=8)

#Medicine Name Input
tk.Label(add_reminder_frame, text= "Medicine Name:").pack()
med_name = tk.Entry(add_reminder_frame, width=30)
med_name.pack()

#Medication Time Input 
tk.Label(add_reminder_frame, text="Remind Time (HH:MM):").pack()
med_time = tk.Entry(add_reminder_frame, width=30)
med_time.pack()

#Medication Dosage Input
tk.Label(add_reminder_frame, text= "Dosage:").pack()
med_dosage = tk.Entry(add_reminder_frame, width=30)
med_dosage.pack()

#Reminder Date Input
tk.Label(add_reminder_frame, text= "Reminder Date (YYYY-MM-DD):").pack()
med_date = tk.Entry(add_reminder_frame, width=30)
med_date.pack()

#Note Input
tk.Label(add_reminder_frame, text= "Note (Optional):").pack()
med_note = tk.Entry(add_reminder_frame, width=30)
med_note.pack()

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

#Function of changing windows
def show_main_menu():
    add_reminder_frame.pack_forget()
    main_menu_frame.pack(fill=tk.BOTH, expand=True)
    window.update_idletasks()#Update Button Display Immediately

def show_add_menu():
    main_menu_frame.pack_forget()
    add_reminder_frame.pack(fill=tk.BOTH, expand=True)
    window.update_idletasks()#Update Input Box Display Immediately

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
    for one_time in times:
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
    
    medicine_list.append({"name":name,"time": ",".join(times), "dosage": dosage, "date": reminder_date, "note": note, "reminded_times": []})
    save_data(medicine_list)
    messagebox.showinfo("Successfully",f"You will be reminded to take {dosage} {name} on {reminder_date} at {','.join(times)}.\n"f"Note: {note or 'None'}")
    med_name.delete(0,tk.END)
    med_time.delete(0,tk.END)
    med_dosage.delete(0,tk.END)
    med_date.delete(0,tk.END)
    med_note.delete(0,tk.END)
    #Refresh the opened list window after adding the medicine(Vision 3 newly added)
    refresh_opened_list()

#Add new buttons for changing windows
add_button_frame = tk.Frame(add_reminder_frame)
add_button_frame.pack(pady=12)

tk.Button(
    add_button_frame,
    text="Add Reminder",
    command=add_medicine
).pack(side=tk.LEFT,pady=12)

tk.Button(
    add_button_frame,
    text="Back to Main Menu",
    command=show_main_menu
).pack(side=tk.LEFT, pady=12)

    
#Background Monitoring Function
def monitor_time():
    while True:
    # Get current date and time 
        now_dt = datetime.now()
        today = now_dt.strftime("%Y-%m-%d")
        now = now_dt.strftime("%H:%M")

        need_save = False #Mark whether saving is required

        #Read multiple time from the same record.
        for med in medicine_list:
            med_times = [
                item.strip()
                for item in med.get("time", "").split(",")
                if item.strip()
            ]

            #Skip if not today's reminder
            if med.get("date","") != today:
                continue

            #Check every recorded time independently.
            for med_t in med_times:
                #Get the list of reminded times; automatically create an empty list if it does not exist
                reminded_times = med.setdefault("reminded_times", [])

                #This time has not been reminded yet
                if now == med_t and med_t not in reminded_times:
                    #Get the dosage and remarks from the dictionary
                    dosage = med.get("dosage", "")
                    note = med.get("note", "")
                    # Pop-up Reminder
                    window.after(0, lambda m=med, d=dosage, n=note, t=med_t:messagebox.showinfo("Medication Reminder", f"It's time to take {d} {m.get('name','')}!\n" f"Note: {n or 'None'}"))

                    #Mark this time as reminded
                    reminded_times.append(med_t)
                    need_save = True#Marks need to be saved
                
                    #Refresh Medicine List to show the latest reminder status
                    window.after(0, refresh_opened_list)

        #Save only when changes occur
        if need_save:
            save_data(medicine_list)

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

    #Create a new window for list
    list_win = tk.Toplevel(window)
    list_win.title("Medicine List")
    list_win.geometry("750x500")
    #List window minimum size
    list_win.minsize(750,500)

    #Save window reference
    list_window_ref = list_win

    #Set a list in the new window
    lb = tk.Listbox(list_win, width=55, height=12)
    lb.pack(padx=10,pady=10, fill=tk.BOTH, expand=True)

    #Show reminder status
    def get_reminder_status(item):
        times = [
            one_time.strip()
            for one_time in item.get("time", "").split(",")
            if one_time.strip()
        ]

        if not times:
            return "No reminder time"       

        reminded_times = item.get("reminded_times", [])

        #Calculate the number of reminded items correctly
        reminded_count = 0
        for one_time in times:
            if one_time in reminded_times:
                reminded_count += 1

        #Check if all times have been reminded
        if reminded_count == len(times):
            return "Reminded"

        #Check if all records have been reminded
        if reminded_count > 0:
            return f"Partially reminded ({reminded_count}/{len(times)})"

        #Check if the date is in the future
        try:
            reminder_date = datetime.strptime(item.get("date", ""), "%Y-%m-%d").date()
            today = datetime.now().date()
            if reminder_date > today:
                return "Not due"
        except ValueError:
            pass #If the date format is invalid, proceed to the next step

        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")
        #Check if the date is already in the past
        if item.get("date", "") < today:
            return "Past Due"

        #Check if the date is today but every time has passed without a reminder
        if item.get("date", "") == today and all(one_time < now_time for one_time in times):
            return "Past due"
        
        return"Not reminded"
    
    #Refresh listbox
    def refresh_listbox():
        lb.delete(0,tk.END)
        current = load_data()

        if len(current) == 0:
            lb.insert(tk.END, "No medicines have been added yet!")
        else:
            for idx, item in enumerate(current, start=1):
                status = get_reminder_status(item)

                lb.insert(tk.END, 
                          f"{idx}. {item.get('name', '')} --- Date: {item.get('date', 'Not set')} ---"
                          f"Time: {item.get('time', '')} --- Dosage: {item.get('dosage', 'Not set')} ---"
                          f"Note: {item.get('note', '') or 'None'} ---"
                          f"Status: {status}"
                          )

    #Save the refresh function to a global variable
    list_refresh_func = refresh_listbox

    #Delete the medicine in the list
    def delete_selected():
        selected_index = lb.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select one reminder first")
            return
        pos = selected_index[0]
        current_data = load_data()
        #Fundamentally prevent the IndexError‑list‑out‑of‑range error
        if pos >= len(current_data):
            messagebox.showerror("Error", "Invalid Operation")
            refresh_listbox()
            return
        confirm = messagebox.askyesno("confirm Delete", f"Are you sure you want to delete: \n{current_data[pos]['name']} {current_data[pos]['time']}?")
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
            messagebox.showwarning("Warning", "Please select one reminder first")
            return
        pos = selected_index[0]
        current_data = load_data()
        #Fundamentally prevent the IndexError‑list‑out‑of‑range error
        if pos >= len(current_data):
            messagebox.showerror("Error", "The reminder no longer exists, refresh list")
            refresh_listbox()
            return
        target_item = current_data[pos]

        #Create a pop-up child window for editing
        edit_win = tk.Toplevel(list_win)
        edit_win.title("Edit Recorded Reminder")
        edit_win.geometry("600x500")
        edit_win.minsize(600,500)

        #Editting Window
        tk.Label(edit_win, text="Medicine Name:").pack()#Pre‑fill the original name
        new_name_entry = tk.Entry(edit_win,width=28)
        new_name_entry.insert(0, target_item.get("name", ""))#Fill the old name into the input box
        new_name_entry.pack(pady=5)

        tk.Label(edit_win, text="Time(HH:MM):").pack()#Pre‑fill the original time
        new_time_entry = tk.Entry(edit_win,width=28)
        new_time_entry.insert(0, target_item.get("time", ""))#Fill the old time into the input box
        new_time_entry.pack(pady=5)

        tk.Label(edit_win, text="Dosage:").pack()#Pre‑fill the original dosage
        new_dosage_entry = tk.Entry(edit_win,width=28)
        new_dosage_entry.insert(0, target_item.get("dosage", ""))#Fill the old dosage into the input box
        new_dosage_entry.pack(pady=5)

        tk.Label(edit_win, text="Remind Date (YYYY-MM-DD):").pack()#Pre‑fill the original date
        new_date_entry = tk.Entry(edit_win,width=28)
        new_date_entry.insert(0, target_item.get("date", ""))#Fill the old date into the input box
        new_date_entry.pack(pady=5)

        tk.Label(edit_win, text="Note:").pack()#Pre‑fill the original note
        new_note_entry = tk.Entry(edit_win,width=28)
        new_note_entry.insert(0, target_item.get("note", ""))#Fill the old note into the input box
        new_note_entry.pack(pady=5)

        #Save the new record
        def save_edit():

            new_name = new_name_entry.get().strip()
            new_time = new_time_entry.get().strip()
            new_dosage = new_dosage_entry.get().strip()
            new_date = new_date_entry.get().strip()
            new_note = new_note_entry.get().strip()

            if not new_name or not new_time or not new_dosage or not new_date:
                messagebox.showwarning("Name, time,dosage and date cannot be empty!")
                return

            #Validate every edited reminder time.
            new_times = [item.strip() for item in new_time.split(",") if item.strip()]
            if not new_times:
                messagebox.showwarning("Invalid Time", "Please enter at least one time.")
                return

            #Validate every edited time form
            for one_time in new_times:
                try:
                    datetime.strptime(one_time, "%H:%M")
                except ValueError:
                    messagebox.showwarning("Invalid Time", f"Invalid time: {one_time}\nPlease follow HH:MM form")
                    return

            #Validate every edited date form
            try:
                selected_date = datetime.strptime(new_date, "%Y-%m-%d").date()
                if selected_date < datetime.today().date():
                    messagebox.showwarning("Invalid Date", "Please enter today or a future date")
                    return

            except ValueError:
                messagebox.showwarning("Invalid Date", "Please follow YYYY-MM-DD form")
                return

            #Overwrite the data at the corresponding position in the original list
            old_time = current_data[pos].get("time", "")
            old_date = current_data[pos].get("date", "")
            new_time_text = ",".join(new_times)
            current_data[pos]["name"] = new_name
            current_data[pos]["date"] = new_date
            current_data[pos]["time"] = new_time_text
            current_data[pos]["dosage"] = new_dosage
            current_data[pos]["note"] = new_note

            #Reset completion status only when the reminder schedule changes
            if old_time != new_time_text or old_date != new_date:
                current_data[pos]["reminded_times"] = []

            save_data(current_data)
            global medicine_list
            medicine_list = current_data
            refresh_listbox()
            edit_win.destroy()
            messagebox.showinfo("Success", "Reminder updated")
            #Refresh all opened list windows after editing
            refresh_opened_list()

        #Place buttons side-by-side, horizontally centered.(Vision 3 newly added)
        button_frame = tk.Frame(edit_win)
        button_frame.pack(pady=12)
        tk.Button(button_frame, text="Save Changes", command=save_edit).pack(side=tk.LEFT, pady=12)
        tk.Button(button_frame, text="Cancel", command=edit_win.destroy).pack(side=tk.LEFT, pady=12)

    #Vision 3 newly added
    refresh_listbox()
    #Place buttons side-by-side, horizontally centered.
    list_button_frame = tk.Frame(list_win)
    list_button_frame.pack(pady=12)
    tk.Button(list_button_frame, text="Edit Selected Reminder", command=edit_selected).pack(side=tk.LEFT,pady=12)
    tk.Button(list_button_frame, text="Delete Selected Reminder", command=delete_selected).pack(side=tk.LEFT, pady=12)

    #Clean up global references when the window is closed
    def on_list_window_close():
        global list_window_ref, list_refresh_func
        list_window_ref = None
        list_refresh_func = None
        list_win.destroy()
        show_main_menu()

    list_win.protocol("WM_DELETE_WINDOW", on_list_window_close)

    #Add button for Medicine List that can return Add Medicine window
    def back_to_main_menu():
        on_list_window_close()
        show_main_menu()
        window.lift()
        window.update_idletasks()

    tk.Button(
        list_button_frame,
        text="Back to Main Window",
        command=back_to_main_menu
    ).pack(side=tk.LEFT, pady=12)
    

# Start Background Thread
monitor_thread = threading.Thread(target=monitor_time, daemon=True)
monitor_thread.start()

#Not needed
# #Place buttons side-by-side, horizontally centered.
# main_button_frame = tk.Frame(window)
# main_button_frame.pack(pady=12)
# #Add Medicine Button    
# tk.Button(main_button_frame, text="Add Reminder", command=add_medicine).pack(side=tk.LEFT, pady=12)
# #Show All Medicines BUtton (Vision 2 newly added）
# tk.Button(main_button_frame, text="Show All Reminders", command=show_all_medicine).pack(side=tk.LEFT, pady=12)

#Buttons for Main Menu
tk.Label(
    main_menu_frame,
    text="Main Menu",
    font=("Arial", 30, "bold")
).pack(pady=(70,15))

tk.Button(
    main_menu_frame,
    text="Add Reminder",
    width=25,
    height=2,
    command=show_add_menu
).pack(pady=12)

tk.Button(
    main_menu_frame,
    text="Show All Reminders",
    width=25,
    height=2,
    command=show_all_medicine
).pack(pady=12)

tk.Button(
    main_menu_frame,
    text="Exit",
    width=25,
    height=2,
    command=window.destroy
).pack(pady=12)

#Start by showing the main menu
main_menu_frame.pack(fill=tk.BOTH, expand=True)



#Message loop(Place it at the end to keep the window displayed)
window.mainloop()