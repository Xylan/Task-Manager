import os
import sys
import json
import psutil
from tkinter import Tk, Label, Checkbutton, IntVar, messagebox
from pathlib import Path
import winshell

from update_manager import update_task_manager
CURRENT_VERSION = "0.1.0"

if __name__ == "__main__":
    update_task_manager(CURRENT_VERSION)
    print("Running Task Manager...")
    # Main app logic here

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

# Functions to ensure the program runs on startup
def add_to_startup():
  startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
  script_path = sys.argv[0]
  shortcut_path = os.path.join(startup_folder, "TaskGatekeeper.lnk")
  if not os.path.exists(shortcut_path):
    try:
      with winshell.shortcut(shortcut_path) as shortcut:
        shortcut.path = script_path
        shortcut.working_directory = os.path.dirname(script_path)
        shortcut.description = "Task Gatekeeper"
    except Exception as e:
      pass

# Check and block games
def load_games_to_block():
  if not os.path.exists(GAMES_FILE):
    with open(GAMES_FILE, "w") as f:
      json.dump(GAMES_TO_BLOCK,f)
  with open(GAMES_FILE, "r") as f:
    return json.load(f)
#
def kill_all_matching_processes(target_names):
    for process in psutil.process_iter(['pid', 'name']):
        try:
            if process.info['name'] in target_names:
                process.kill()  # Terminate the process
                process.wait()  # Wait for the process to terminate
        except Exception as e:
            pass  # Handle cases where the process doesn't exist or we can't access it
    
# Prevent window closure without task completion
def on_closing():
  if not all_tasks_completed():
    messagebox.showwarning("Tasks Incomplete", "You must complete all tasks before exiting.")
  else:
    root.destroy()

# Check if tasks are completed
def all_tasks_completed():
    if all(task_status[task] for task in TASKS):
        return True
    return False

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
def update_task_status(task, status):
  task_status[task] = bool(status)
  save_task_status()
  refresh_ui()
  if all_tasks_completed():
    show_congratulations()  # Show popup and close the app
# Function to show the congratulations popup and close the app
def show_congratulations():
    messagebox.showinfo("Congratulations", "All tasks completed! You are now allowed to play games.")
    root.destroy()  # Close the app

# Refresh UI
def refresh_ui():
    for i, task in enumerate(TASKS):
        vars[i].set(1 if task_status[task] else 0)
    
# Main UI setup
root = Tk()
# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# Set the desired window width and height
window_width = 800
window_height = 600
# Calculate the x and y positions to center the window
x_position = (screen_width // 2) - (window_width // 2)
y_position = (screen_height // 2) - (window_height // 2)

root.title("Task Gatekeeper")
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.attributes('-topmost', True)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.overrideredirect(True)  # Remove minimize, maximize, and close buttons
root.attributes('-toolwindow', True)
root.resizable(False, False)
Label(root, text="Complete these tasks before playing games:", font=("Helvetica", 14)).pack(pady=10)

# Task status and UI elements
task_status = load_task_status()
vars = []
for task in TASKS:
  var = IntVar(value=1 if task_status[task] else 0)
  vars.append(var)
  checkbutton = Checkbutton(
    root,
    text=task,
    font=("Helvetica", 12),
    variable=var,
    command=lambda t=task, v=var: update_task_status(t, v.get())
  )
  checkbutton.pack(anchor="w")

# Warning message
Label(
  root,
  text="WARNING: Playing games without completing all of these tasks will cause you to forfeit your gaming privileges \n" + f"{CURRENT_VERSION}",
  font=("Arial", 12),
  fg="red"
  ).pack(pady=10)

# Background game monitoring
def monitor_games():
  if not all_tasks_completed():
     kill_all_matching_processes(GAMES_TO_BLOCK)
  root.after(5000, monitor_games)

# Ensure startup and launch monitoring
GAMES_TO_BLOCK = load_games_to_block()
#add_to_startup() #disabled for testing, reenable when ready
monitor_games()
refresh_ui()

# Run the UI loop
root.mainloop()
