import requests
import os
import subprocess
import sys

GITHUB_REPO = "Xylan/Task-Manager"

def get_latest_release():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch release information.")
        return None

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    with open(output_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
    print(f"Downloaded update to {output_path}")

def apply_update(executable_path, new_version_path):
    try:
        os.rename(executable_path, f"{executable_path}.old")  # Backup the old executable
        os.rename(new_version_path, executable_path)  # Replace it
        print("Update applied successfully.")
    except Exception as e:
        print(f"Failed to update: {e}")
        return False
    return True

def update_task_manager(current_version):
    latest_release = get_latest_release()
    if not latest_release:
        return

    latest_version = latest_release.get("tag_name", "0.0.0")
    if latest_version > current_version:
        print(f"New version available: {latest_version}")
        for asset in latest_release.get("assets", []):
            if "task_manager.exe" in asset["name"]:  # Match your executable name
                download_url = asset["browser_download_url"]
                download_path = "task_manager_new.exe"
                download_file(download_url, download_path)
                if apply_update(sys.argv[0], download_path):
                    subprocess.Popen([sys.argv[0]])  # Restart
                    sys.exit()
    else:
        print("You are running the latest version.")
