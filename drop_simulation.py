import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
from collections import defaultdict

COX_ITEMS = {
    "Dexterous Prayer Scroll": 1 / 3.45,
    "Arcane Prayer Scroll": 1 / 3.45,
    "Twisted Buckler": 1 / 17.25,
    "Dragon Hunter Crossbow": 1 / 17.25,
    "Dinh's Bulwark": 1 / 23,
    "Ancestral Hat": 1 / 23,
    "Ancestral Robe Top": 1 / 23,
    "Ancestral Robe Bottom": 1 / 23,
    "Dragon Claws": 1 / 23,
    "Elder Maul": 1 / 34.5,
    "Kodai Insignia": 1 / 34.5,
    "Twisted Bow": 1 / 34.5
}

TOB_ITEMS = {
    'regular': {
        'Scythe of Vitur': 0.0526,
        'Ghrazi Rapier': 0.1053,
        'Sanguinesti Staff': 0.1053,
        'Justiciar Faceguard': 0.1053,
        'Justiciar Chestguard': 0.1053,
        'Justiciar Legguards': 0.1053,
        'Avernic Defender Hilt': 0.4209
    },
    'hmt': {
        'Scythe of Vitur': 0.0555,
        'Ghrazi Rapier': 0.1111,
        'Sanguinesti Staff': 0.1111,
        'Justiciar Faceguard': 0.1111,
        'Justiciar Chestguard': 0.1111,
        'Justiciar Legguards': 0.1111,
        'Avernic Defender Hilt': 0.3889
    }
}

OLMLET_RATE = 1 / 53


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def calculate_cox_chance(points):
    chance = min(points / 8676 / 100, 0.657)
    return chance


def roll_cox_item():
    total_weight = sum(COX_ITEMS.values())
    roll = random.random() * total_weight
    current_weight = 0

    for item, rate in COX_ITEMS.items():
        current_weight += rate
        if roll < current_weight:
            return item
    return list(COX_ITEMS.keys())[0]



def roll_tob_item(is_hmt):
    items = TOB_ITEMS['hmt' if is_hmt else 'regular']
    roll = random.random()
    cumulative = 0

    for item, chance in items.items():
        cumulative += chance
        if roll < cumulative:
            return item
    return list(items.keys())[0]


def simulate_drops():
    try:
        drop_rate = int(entry_drop_rate.get())
        num_kills = int(entry_kills.get())
        if drop_rate <= 0 or num_kills <= 0:
            raise ValueError

        if drop_rate == 1:
            text_output.delete("1.0", tk.END)
            text_output.insert(tk.END, "Really?")
            return

        drop_chance = 1 / drop_rate
        simulated_drops = [random.random() < drop_chance for _ in range(num_kills)]
        drop_indices = [i + 1 for i, drop in enumerate(simulated_drops) if drop]
        total_drops = len(drop_indices)

        result_text = ""

        if drop_rate == 2:
            result_text = "You either get it or you don't\n\n"

        if total_drops == 0:
            result_text += f"Simulated {num_kills} kills with 1 in {drop_rate} drop rate.\n\nNo drops, unluggy"
        else:
            result_text += f"Simulated {num_kills} kills with 1 in {drop_rate} drop rate.\n\n"
            result_text += f"Drops occurred at kills: {drop_indices}\n\nTotal drops: {total_drops}"

        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, result_text)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid positive integers.")


def simulate_cox():
    try:
        points = int(entry_cox_points.get())
        num_raids = int(entry_cox_raids.get())

        if points <= 0 or num_raids <= 0:
            raise ValueError("Points and raids must be positive numbers")

        if points > 570000:
            messagebox.showwarning("Points Capped", "Points have been capped at 570,000")
            points = 570000

        drop_chance = calculate_cox_chance(points)

        unique_drops = defaultdict(int)
        drop_raids = defaultdict(list)
        total_uniques = 0

        for raid_num in range(1, num_raids + 1):
            if random.random() < drop_chance:
                total_uniques += 1
                item = roll_cox_item()
                unique_drops[item] += 1
                drop_raids[item].append(raid_num)

                if random.random() < OLMLET_RATE:
                    unique_drops["Olmlet"] += 1
                    drop_raids["Olmlet"].append(raid_num)

        result_text = f"Simulated {num_raids:,} raids with {points:,} points\n"
        result_text += f"Drop chance per raid: {drop_chance:.2%}\n"
        result_text += f"Total uniques: {total_uniques:,}\n\n"

        if total_uniques > 0:
            if "Olmlet" in unique_drops:
                result_text += f"Olmlet: {unique_drops['Olmlet']:,} [{', '.join(map(str, drop_raids['Olmlet']))}]  (gz pet!)\n\n"

            sorted_drops = sorted(
                [(item, count, drop_raids[item]) for item, count in unique_drops.items() if item != "Olmlet"],
                key=lambda x: COX_ITEMS[x[0]]
            )

            for item, count, raids in sorted_drops:
                raids_str = ", ".join(map(str, raids))
                result_text += f"{item}: {count:,} [{raids_str}]\n"
        else:
            result_text += "No unique drops... unluggy!"

        text_cox_output.delete("1.0", tk.END)
        text_cox_output.insert(tk.END, result_text)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid positive integers for points and raids.")


def simulate_tob():
    try:
        num_raids = int(entry_tob_raids.get())
        team_size = int(entry_team_size.get())
        is_hmt = hmt_var.get()

        if num_raids <= 0:
            raise ValueError("Raids must be positive")
        if team_size < 1 or team_size > 5:
            raise ValueError("Team size must be between 1 and 5")

        unique_chance = 1 / 7.7 if is_hmt else 1 / 9.1
        pet_chance = 1 / 500 if is_hmt else 1 / 650
        personal_chance = 1 / team_size

        team_drops = defaultdict(int)
        personal_drops = defaultdict(int)
        drop_raids = defaultdict(list)
        team_uniques = 0
        personal_uniques = 0

        for raid_num in range(1, num_raids + 1):
            if random.random() < unique_chance:
                team_uniques += 1
                item = roll_tob_item(is_hmt)
                team_drops[item] += 1
                if random.random() < personal_chance:
                    personal_uniques += 1
                    personal_drops[item] += 1
                    drop_raids[item].append(raid_num)

            if random.random() < pet_chance:
                team_drops["Lil Zik"] += 1
                personal_drops["Lil Zik"] += 1
                drop_raids["Lil Zik"].append(raid_num)

        mode = "Hard Mode" if is_hmt else "Regular"
        result_text = f"Theatre of Blood {mode} Simulator\n"
        result_text += "Disclaimer: This calculator assumes deathless raids\n\n"
        result_text += f"Simulated {num_raids:,} raids with {team_size} team members\n"
        result_text += f"Unique chance per raid: {unique_chance:.2%}\n"
        result_text += f"Team uniques: {team_uniques:,}\n"
        result_text += f"My uniques: {personal_uniques:,}\n\n"

        if "Lil Zik" in personal_drops:
            result_text += f"Lil Zik: {personal_drops['Lil Zik']:,} [{', '.join(map(str, drop_raids['Lil Zik']))}]  (gz pet!)\n\n"

        if personal_uniques > 0:
            mode_key = 'hmt' if is_hmt else 'regular'
            sorted_items = sorted([(k, personal_drops[k], drop_raids[k])
                                   for k in TOB_ITEMS[mode_key].keys()
                                   if k in personal_drops],
                                  key=lambda x: TOB_ITEMS[mode_key][x[0]]
                                  )

            for item, count, raids in sorted_items:
                raids_str = ", ".join(map(str, raids))
                result_text += f"{item}: {count:,} [{raids_str}]\n"
        else:
            result_text += "No personal unique drops... unluggy!"

        text_tob_output.delete("1.0", tk.END)
        text_tob_output.insert(tk.END, result_text)

    except ValueError as e:
        messagebox.showerror("Invalid Input",
                             "Please enter valid numbers:\n- Raids must be positive\n- Team size must be between 1-5")


window = tk.Tk()
window.title("Drop Simulator")
window.geometry("800x600")

notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

custom_tab = ttk.Frame(notebook)
cox_tab = ttk.Frame(notebook)
tob_tab = ttk.Frame(notebook)

notebook.add(custom_tab, text='Custom')
notebook.add(cox_tab, text='CoX')
notebook.add(tob_tab, text='ToB')

bg_image = Image.open(resource_path("background.jpg"))
bg_image = bg_image.resize((800, 600))
bg_photo = ImageTk.PhotoImage(bg_image)

bg_cox_image = Image.open(resource_path("bg_cox.jpg"))
bg_cox_image = bg_cox_image.resize((800, 600))
bg_cox_photo = ImageTk.PhotoImage(bg_cox_image)

bg_tob_image = Image.open(resource_path("bg_tob.jpg"))
bg_tob_image = bg_tob_image.resize((800, 600))
bg_tob_photo = ImageTk.PhotoImage(bg_tob_image)

custom_canvas = tk.Canvas(custom_tab, width=800, height=600)
custom_canvas.pack(fill="both", expand=True)
custom_canvas.create_image(0, 0, image=bg_photo, anchor="nw")

entry_drop_rate = tk.Entry(window)
entry_kills = tk.Entry(window)
button_simulate = tk.Button(window, text="Simulate", command=simulate_drops)
text_output = tk.Text(window, height=8, width=60)

custom_canvas.create_window(400, 30, window=tk.Label(window, text="Drop Rate (e.g., 1500 for 1/1500):"))
custom_canvas.create_window(400, 55, window=entry_drop_rate)
custom_canvas.create_window(400, 85, window=tk.Label(window, text="Number of Kills:"))
custom_canvas.create_window(400, 110, window=entry_kills)
custom_canvas.create_window(400, 150, window=button_simulate)
custom_canvas.create_window(400, 280, window=text_output)

cox_canvas = tk.Canvas(cox_tab, width=800, height=600)
cox_canvas.pack(fill="both", expand=True)
cox_canvas.create_image(0, 0, image=bg_cox_photo, anchor="nw")

entry_cox_points = tk.Entry(window)
entry_cox_raids = tk.Entry(window)
button_simulate_cox = tk.Button(window, text="Simulate CoX", command=simulate_cox)
text_cox_output = tk.Text(window, height=15, width=80)

cox_canvas.create_window(400, 30, window=tk.Label(window, text="Points (max 570,000):"))
cox_canvas.create_window(400, 55, window=entry_cox_points)
cox_canvas.create_window(400, 85, window=tk.Label(window, text="Number of Raids:"))
cox_canvas.create_window(400, 110, window=entry_cox_raids)
cox_canvas.create_window(400, 150, window=button_simulate_cox)
cox_canvas.create_window(400, 280, window=text_cox_output)

tob_canvas = tk.Canvas(tob_tab, width=800, height=600)
tob_canvas.pack(fill="both", expand=True)
tob_canvas.create_image(0, 0, image=bg_tob_photo, anchor="nw")

hmt_var = tk.BooleanVar()
hmt_checkbox = tk.Checkbutton(window, text="Hard Mode Theatre", variable=hmt_var)
entry_tob_raids = tk.Entry(window)
entry_team_size = tk.Entry(window)
button_simulate_tob = tk.Button(window, text="Simulate ToB", command=simulate_tob)
text_tob_output = tk.Text(window, height=20, width=80)

tob_canvas.create_window(400, 50, window=tk.Label(window, text="Number of Raids:"))
tob_canvas.create_window(400, 75, window=entry_tob_raids)
tob_canvas.create_window(400, 105, window=tk.Label(window, text="Team Size (1-5):"))
tob_canvas.create_window(400, 130, window=entry_team_size)
tob_canvas.create_window(400, 160, window=hmt_checkbox)
tob_canvas.create_window(400, 190, window=button_simulate_tob)
tob_canvas.create_window(400, 380, window=text_tob_output)

window.mainloop()