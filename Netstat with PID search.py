import subprocess
import time
import psutil
import os
import threading
import itertools

# Function to display a loading spinner
def loading_spinner():
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while True:
        print(next(spinner), end='\r')
        time.sleep(0.1)

# Function to get user input for searching connections
def get_user_input():
    while True:
        user_input = input("Enter partial URL or IP address to search for connections: ")
        if user_input.strip():  # Check if input is not empty
            return user_input.strip()

# Function to search for connections and return a list of PIDs
def search_connections():
    pids = []
    loading_thread = threading.Thread(target=loading_spinner, daemon=True)
    search_term = get_user_input()
    loading_thread.start()
    print(f"Searching for connections to {search_term}...")
    command = f"netstat -atqo | find \"{search_term}\""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Error occurred while executing the command.")
    lines = result.stdout.strip().split('\n')
    for line in lines:
        fields = line.split()
        for i, field in enumerate(fields):
            if field.isdigit() and i < len(fields) - 1 and fields[i + 1] == "InHost":
                pid = int(field)
                pids.append(pid)
    loading_thread.join()  # Stop the loading spinner
    if pids:
        return pids
    else:
        print("No connections found. Please try again.")
        return None
        
# Function to search for process name based on PID
def get_process_name(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.NoSuchProcess:
        return "Unknown"
    except Exception as e:
        return f"Error: {e}"

# Function to search for process and open Task Manager
def search_and_open_task_manager(process_ids):
    for pid in process_ids:
        process_name = get_process_name(pid)
        print(f"Process name: {process_name} (PID: {pid})")
        try:
            os.system("taskmgr /pid " + str(pid))
        except Exception as e:
            print(f"Error opening Task Manager for PID {pid}: {e}")

# Main function
def main():
    while True:
        pids = search_connections()
        if pids:
            search_and_open_task_manager(pids)
        else:
            print("No PIDs to search for process.")
        choice = input("Do you want to search for connections again? (y/n): ")
        if choice.lower() != 'y':
            break

if __name__ == "__main__":
    main()
