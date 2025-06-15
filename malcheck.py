import os
import sys
import winreg
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import ctypes

# Elevation check
def require_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        print("[!] Elevation required. Re-launching as administrator...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# Save report to Downloads folder
downloads_dir = os.path.join(os.environ["USERPROFILE"], "Downloads")
def get_report_path():
    return os.path.join(downloads_dir, f"malware_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def prompt_app_name():
    return input("\nEnter the File/App name to search for (case-insensitive): ").strip().lower()

def search_registry(app_name):
    print("\n[+] Searching Windows Registry...")
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node"),
    ]
    matches = []
    for root, path in reg_paths:
        try:
            matches += search_reg_tree(root, path, app_name)
        except:
            pass
    return matches

def search_reg_tree(root, path, app_name):
    matches = []
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    full_path = f"{path}\\{subkey_name}"
                    if app_name in subkey_name.lower():
                        matches.append((root, full_path))
                    matches += search_reg_tree(root, full_path, app_name)
                except:
                    continue
    except:
        pass
    return matches

def search_filesystem(app_name):
    print("[+] Searching filesystem...")
    search_dirs = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("APPDATA"),
        os.environ.get("LOCALAPPDATA"),
        str(Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"),
        downloads_dir  # Include Downloads folder
    ]
    found_paths = []
    for root_dir in filter(None, search_dirs):
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if app_name in filename.lower():
                    full_path = os.path.join(dirpath, filename)
                    found_paths.append(full_path)
    return found_paths

def search_task_scheduler(app_name):
    print("[+] Searching Task Scheduler...")
    found_tasks = []
    try:
        result = subprocess.run(['schtasks', '/query', '/fo', 'LIST', '/v'], stdout=subprocess.PIPE, text=True)
        tasks = result.stdout.split("\n\n")
        for task in tasks:
            if app_name in task.lower():
                found_tasks.append(task.strip())
    except:
        pass
    return found_tasks

def winreg_key_str(root):
    return {
        winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
        winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER"
    }.get(root, str(root))

def write_report(report_path, registry_matches, file_matches, task_matches):
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("====== Malware Cleanup Report ======\n")
        f.write(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("[Registry Entries]\n")
        for root, path in registry_matches:
            f.write(f" - {winreg_key_str(root)}\\{path}\n")
        if not registry_matches:
            f.write(" - None found\n")

        f.write("\n[File System Entries]\n")
        for path in file_matches:
            f.write(f" - {path}\n")
        if not file_matches:
            f.write(" - None found\n")

        f.write("\n[Scheduled Tasks]\n")
        for task in task_matches:
            task_lines = task.splitlines()
            name = next((line for line in task_lines if line.startswith("TaskName:")), " - Unknown Task")
            f.write(f" - {name}\n")
        if not task_matches:
            f.write(" - None found\n")

    print(f"\n[✓] Report saved to: {report_path}")

# Recursive registry deletion
def delete_registry_key_recursive(root, path):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
            for i in range(winreg.QueryInfoKey(key)[0] - 1, -1, -1):
                subkey = winreg.EnumKey(key, i)
                delete_registry_key_recursive(root, f"{path}\\{subkey}")
        winreg.DeleteKey(root, path)
        return True
    except Exception as e:
        print(f"[!] Failed to delete registry key {winreg_key_str(root)}\\{path} — {e}")
        return False

def confirm_and_delete(registry_matches, file_matches, task_matches):
    confirm = input("\nDo you want to delete all the found entries? (y/n): ").strip().lower()
    if confirm != "y":
        print("Aborted. No changes made.")
        return

    print("\n[+] Deleting...")

    # Delete Registry Keys
    reg_deleted = 0
    for root, path in registry_matches:
        print(f"[Registry] Deleting: {winreg_key_str(root)}\\{path}")
        if delete_registry_key_recursive(root, path):
            print("[✓] Deleted registry key.")
            reg_deleted += 1

    # Delete Files
    file_deleted = 0
    for path in file_matches:
        print(f"[File] Deleting: {path}")
        try:
            os.remove(path)
            print("[✓] Deleted file.")
            file_deleted += 1
        except Exception as e:
            print(f"[!] Failed to delete file: {e}")

    # Delete Scheduled Tasks
    task_deleted = 0
    for task in task_matches:
        try:
            lines = task.splitlines()
            name_line = next((line for line in lines if line.startswith("TaskName:")), None)
            if name_line:
                task_name = name_line.split(":", 1)[1].strip()
                print(f"[Task] Deleting: {task_name}")
                subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("[✓] Deleted scheduled task.")
                task_deleted += 1
        except Exception as e:
            print(f"[!] Failed to delete scheduled task — {e}")

    print(f"\n✅ Cleanup complete. Deleted: {reg_deleted} registry keys, {file_deleted} files, {task_deleted} scheduled tasks.")

def scan_once():
    app_name = prompt_app_name()
    reg_hits = search_registry(app_name)
    file_hits = search_filesystem(app_name)
    task_hits = search_task_scheduler(app_name)

    report_path = get_report_path()
    write_report(report_path, reg_hits, file_hits, task_hits)

    print("\n========== Scan Summary ==========")
    print(f" Registry Matches: {len(reg_hits)}")
    print(f" Files Found:      {len(file_hits)}")
    print(f" Scheduled Tasks:  {len(task_hits)}")

    confirm_and_delete(reg_hits, file_hits, task_hits)

def main():
    require_admin()
    while True:
        scan_once()
        again = input("\nWould you like to scan for another string? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break

if __name__ == "__main__":
    if os.name != 'nt':
        print("❌ This script is for Windows only.")
    else:
        main()
