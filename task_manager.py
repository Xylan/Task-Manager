import os
import sys
import json
import psutil
import ctypes
from tkinter import Tk, Label, Button, Entry, StringVar, END
from tkinter import messagebox
from pathlib import Path
import subprocess
import atexit

# Constants
TASK_FILE = "task_list.json"
GAMES_FILE = "games_to_block.json"
#global variables
TASKS = ["First", "Do your homework"]
GAMES_TO_BLOCK = [
                    "Steam.exe",
                    "EpicGamesLauncher.exe",
                    "Origin.exe",
                    "UbisoftConnect.exe",
                    "Battle.net.exe",
                    "GalaxyClient.exe",
                    "Roblox.exe",
                    "Minecraft.exe"
                ]

# Function to install dependencies using pip and re-import
def install_dependencies():
    required_packages = ['winshell', 'psutil', 'tkinter', 'json', 'importlib']
    missing_packages = []
    try:
        import importlib
        import winshell
        import psutil
        import tkinter
        import json
    except ImportError as e:
        missing_packages.append(str(e).split("'")[1])

    if missing_packages:
        messagebox.showinfo("Installing Dependencies", "Installing missing dependencies...")
        for package in missing_packages:
            subprocess.check_call(['pip', 'install', package])
        messagebox.showinfo("Success", "Dependencies installed successfully!")

        # Re-import modules to use them in the current script
        import importlib
        for package in missing_packages:
            importlib.import_module(package)

# Functions to ensure the program runs on startup
def add_to_startup():
   startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
   script_path = sys.argv[0]
   shortcut_path = os.path.join(startup_folder, "TaskGatekeeper.lnk")
   if not os.path.exists(shortcut_path):
       try:
           import winshell
           with winshell.shortcut(shortcut_path) as shortcut:
               shortcut.path = script_path
               shortcut.working_directory = os.path.dirname(script_path)
               shortcut.description = "Task Gatekeeper"
       except ImportError:
           messagebox.showerror("Missing Dependency", "Please install 'winshell' package: pip install winshell")

# Check and block games
def load_games_to_block():
    if not os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, "w") as f:
            json.dump(GAMES_TO_BLOCK,f)
    with open(GAMES_FILE, "r") as f:
        return json.load(f)

# Check and block games
def is_game_running():
   for process in psutil.process_iter(['pid', 'name']):
       if process.info['name'] in GAMES_TO_BLOCK:
           return process.info['pid']
   return None

def kill_game_process(pid):l
   try:
       os.kill(pid, 9)
   except Exception as e:
       print(f"Error killing process {pid}: {e}")
# Prevent window closure without task completion

def on_closing():
   if not all_tasks_completed():
       messagebox.showwarning("Tasks Incomplete", "You must complete all tasks before exiting.")
   else:
       root.destroy()

# Check if tasks are completed
def all_tasks_completed():
   return all(task_status[task] for task in TASKS)

# Save and load task status
def save_task_status():
   with open(TASK_FILE, "w") as file:
       json.dump(task_status, file)

def load_task_status():
   if Path(TASK_FILE).is_file():
       with open(TASK_FILE, "r") as file:
           return json.load(file)
   return {task: False for task in TASKS}

# Update task status
def update_task_status(task):
   task_status[task] = True
   save_task_status()
   refresh_ui()

# Refresh UI
def refresh_ui():
   for i, task in enumerate(TASKS):
       task_labels[i].config(text=f"{task} - {'Completed' if task_status[task] else 'Incomplete'}")



# Main UI setup
root = Tk()
root.title("Task Gatekeeper")
root.geometry("800x600")
root.attributes('-topmost', True)
root.protocol("WM_DELETE_WINDOW", on_closing)
Label(root, text="Complete these tasks before playing games:", font=("Helvetica", 14)).pack(pady=10)

# Task status and UI elements
task_status = load_task_status()
task_labels = []
for task in TASKS:
   var = StringVar()
   label = Label(root, text=f"{task} - {'Completed' if task_status[task] else 'Incomplete'}", font=("Helvetica", 12))
   label.pack()
   task_labels.append(label)

# Input for task confirmation
def confirm_task():
   task = task_entry.get()
   if task in TASKS and not task_status[task]:
       update_task_status(task)
   elif task not in TASKS:
       messagebox.showerror("Error", "Task not recognized.")
   else:
       messagebox.showinfo("Info", "Task already completed.")
   task_entry.delete(0, END)
Label(root, text="Enter task to confirm:").pack(pady=10)
task_entry = Entry(root)
task_entry.pack()
Button(root, text="Confirm Task", command=confirm_task).pack(pady=10)

# Warning message
Label(root, text="WARNING: Playing games without completing all of these tasks will cause you to forfet your gaming privlidges",
font=("Arial", 12), fg="red").pack(pady=10)

# Background game monitoring
def monitor_games():
   pid = is_game_running()
   if pid and not all_tasks_completed():
       kill_game_process(pid)
       messagebox.showwarning("Blocked", "Game blocked! Complete your tasks first.")
   root.after(5000, monitor_games)

# Ensure startup and launch monitoring
GAMES_TO_BLOCK = load_games_to_block()
add_to_startup()
monitor_games()
refresh_ui()
# Run the UI loop
root.mainloop()
