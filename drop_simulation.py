import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def simulate_drops():
    try:
        drop_rate = int(entry_drop_rate.get())
        num_kills = int(entry_kills.get())
        if drop_rate <= 0 or num_kills <= 0:
            raise ValueError

        drop_chance = 1 / drop_rate
        simulated_drops = [random.random() < drop_chance for _ in range(num_kills)]
        drop_indices = [i + 1 for i, drop in enumerate(simulated_drops) if drop]
        total_drops = len(drop_indices)

        if total_drops == 0:
            result_text = f"Simulated {num_kills} kills with 1 in {drop_rate} drop rate.\n\nNo drops, unluggy"
        else:
            result_text = f"Simulated {num_kills} kills with 1 in {drop_rate} drop rate.\n\n"
            result_text += f"Drops occurred at kills: {drop_indices}\n\nTotal drops: {total_drops}"

        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, result_text)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid positive integers.")

window = tk.Tk()
window.title("Drop Simulator")

bg_image = Image.open(resource_path("background.jpg"))
bg_image = bg_image.resize((600, 400))
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(window, width=600, height=400)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

entry_drop_rate = tk.Entry(window)
entry_kills = tk.Entry(window)
button_simulate = tk.Button(window, text="Simulate", command=simulate_drops)
text_output = tk.Text(window, height=8, width=60)

canvas.create_window(300, 30, window=tk.Label(window, text="Drop Rate (e.g., 1500 for 1/1500):"))
canvas.create_window(300, 55, window=entry_drop_rate)
canvas.create_window(300, 85, window=tk.Label(window, text="Number of Kills:"))
canvas.create_window(300, 110, window=entry_kills)
canvas.create_window(300, 150, window=button_simulate)
canvas.create_window(300, 250, window=text_output)

window.mainloop()
