from json import load
from sys import argv, stderr

import urllib.request
import urllib.error

from pathlib import Path


def get_most_recent_json_file(folder_path: Path) -> Path:
    """
    Returns the most recent .json file in the given folder.

    :param folder_path: Path object pointing to the folder.
    :return: Path object of the most recent .json file or None if no .json file exists.
    """
    if not folder_path.is_dir():
        raise ValueError(f"The provided path '{
                         folder_path}' is not a valid directory.")

    # Filter for .json files in the directory
    json_files = list(folder_path.glob("*.json"))

    # Return None if no .json files are found
    if not json_files:
        return None

    # Find the most recent .json file
    most_recent_file = max(json_files, key=lambda file: file.stat().st_mtime)
    return most_recent_file


def get_page(url):
    try:
        with urllib.request.urlopen(url) as response:
            if response.getcode() == 200:
                return response.read().decode("utf-8")  # Return the content of the page
            else:
                raise ConnectionError(
                    "Error: Received status code", response.getcode())
    except urllib.error.URLError as e:
        raise e


input_dir = argv[1]
with open(get_most_recent_json_file(Path(input_dir))) as f:
    info = load(f)

benchmark = info["benchmarks"][-1]
ops_per_second = (1.0/benchmark["stats"]["mean"])*benchmark["params"]["n"]

color = "red"
if ops_per_second > 20_000_000:
    color = "orange"
if ops_per_second > 50_000_000:
    color = "yellow"
if ops_per_second > 100_000_000:
    color = "yellowgreen"
if ops_per_second > 200_000_000:
    color = "lawngreen"
if ops_per_second > 300_000_000:
    color = "green"

url = f"http://192.168.4.6:8882/badge/performance-{
    ops_per_second/1_000_000:.1f}%20Mops-{color}"

print(url, file=stderr)

try:
    content = get_page(url)
    if content:
        print(content)
except Exception as e:
    print(e, file=stderr)
    print(
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="84" height="20" role="img" aria-label="coverage: ??"><title>coverage: ??</title><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="84" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#r)"><rect width="61" height="20" fill="#555"/><rect x="61" width="23" height="20" fill="#333"/><rect width="84" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110"><text aria-hidden="true" x="315" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">coverage</text><text x="315" y="140" transform="scale(.1)" fill="#fff" textLength="510">coverage</text><text aria-hidden="true" x="715" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="130">??</text><text x="715" y="140" transform="scale(.1)" fill="#fff" textLength="130">??</text></g></svg>'
    )
