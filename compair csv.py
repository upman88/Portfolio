import os
import csv
from datetime import datetime

def compare_and_write(output_file):
    # Specify the download directory
    download_dir = "C:\\Users\\pupman\\Downloads"
    
    # Check if the download directory exists
    if not os.path.exists(download_dir):
        print(f"Error: Download directory '{download_dir}' does not exist.")
        return
    
    # Print the contents of the download directory
    print("Contents of the download directory:")
    print(os.listdir(download_dir))
    
    block_csv_path = os.path.join(download_dir, "block.csv")
    mc_copy_csv_path = os.path.join(download_dir, "MCcopy.csv")
    
    # Check if the block.csv file exists
    if not os.path.exists(block_csv_path):
        print(f"Error: block.csv file not found in '{download_dir}'.")
        return
    
    # Check if the MCcopy.csv file exists
    if not os.path.exists(mc_copy_csv_path):
        print(f"Error: MCcopy.csv file not found in '{download_dir}'.")
        return
    
    block_data = set()
    with open(block_csv_path, 'r') as block_file:
        block_reader = csv.reader(block_file)
        for row in block_reader:
            if row:  # Check if row is not empty
                block_data.add(row[0]) if len(row) > 0 else None  # Assuming Column A is 0-indexed

    output_data = []
    with open(mc_copy_csv_path, 'r') as mc_copy_file:
        mc_copy_reader = csv.reader(mc_copy_file)
        for row in mc_copy_reader:
            if row and len(row) > 1:  # Check if row is not empty and has at least 2 elements
                if row[1] not in block_data:
                    output_data.append(row)

    # Write output to a new CSV file with timestamp
    with open(output_file, 'w', newline='') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerows(output_data)

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join("C:\\Users\\pupman\\Downloads", f"MC_copy_filtered_{timestamp}.csv")
    compare_and_write(output_file)
    print(f"Filtered data written to {output_file}")
