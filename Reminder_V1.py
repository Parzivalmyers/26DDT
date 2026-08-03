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

def test_alert():
    messagebox.showinfo("It's time to take your medicine!")

btn_test = tk.Button(window, text="Reminder", command=test_alert)
btn_test.pack()


#Message loop(Place it at the end to keep the window displayed)
window.mainloop()