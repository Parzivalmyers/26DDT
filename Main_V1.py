#Import the tkinter library
import tkinter as tk
from tkinter import messagebox


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
medicine_list = []

def add_medicine():
    name = med_name.get()
    time_str = med_time.get()
    medicine_list.append({"name":name,"time":time_str})
    messagebox.showinfo("Successful",f"Added:{name} {time_str}")
    med_name.delete(0,tk.END)
    med_time.delete(0,tk.END)

#Add Medicine Button    
tk.Button(window, text="Add Medicine", command=add_medicine).pack(pady=10)
    

#Message loop(Place it at the end to keep the window displayed)
window.mainloop()