import json
import matplotlib.pyplot as plt
import re
import sys
from pathlib import Path

from pathlib import Path

def get_most_recent_json_file(folder_path: Path) -> Path:
    """
    Returns the most recent .json file in the given folder.
    
    :param folder_path: Path object pointing to the folder.
    :return: Path object of the most recent .json file or None if no .json file exists.
    """
    if not folder_path.is_dir():
        raise ValueError(f"The provided path '{folder_path}' is not a valid directory.")

    # Filter for .json files in the directory
    json_files = list(folder_path.glob("*.json"))
    
    # Return None if no .json files are found
    if not json_files:
        return None
    
    # Find the most recent .json file
    most_recent_file = max(json_files, key=lambda file: file.stat().st_mtime)
    return most_recent_file



def read_file(file_path:Path | str):
    with open(Path(file_path)) as f:
        obj = json.load(f)

    x_values = []
    y_values = []

    # Iterate through each benchmark
    for testcase in obj["benchmarks"]:
        name = testcase["name"]
        time = testcase["stats"]["mean"]

        # Extract the number from the name attribute using regex
        match = re.search(r"\[(\d+)\]", name)
        if match:
            x_values.append(int(match.group(1)))
            y_values.append(time)

    return x_values, y_values

# Function to create and save the plot
def plot_data(x, y, output_file):
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='b')
    plt.title("Testcase Times")
    plt.xlabel("Input Size")
    plt.ylabel("Time (seconds)")
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

# Main function
def main():
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    x_values, y_values = read_file(get_most_recent_json_file(Path(input_dir)))
    plot_data(x_values, y_values, output_file)
    
if __name__ == "__main__":
    main()
