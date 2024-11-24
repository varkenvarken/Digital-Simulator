from json import load
from sys import argv, stderr

url = f"http://192.168.4.6:8882/github/v/release/varkenvarken/Digital-Simulator?include_prereleases&color=blue"

import urllib.request
import urllib.error


def get_page(url):
    try:
        with urllib.request.urlopen(url) as response:
            if response.getcode() == 200:
                return response.read().decode("utf-8")  # Return the content of the page
            else:
                raise ConnectionError("Error: Received status code", response.getcode())
    except urllib.error.URLError as e:
        raise e
    
try:
    content = get_page(url)
    if content:
        print(content)
except Exception as e:
    print(e, file=stderr)
    print(
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="84" height="20" role="img" aria-label="coverage: ??"><title>coverage: ??</title><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="84" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#r)"><rect width="61" height="20" fill="#555"/><rect x="61" width="23" height="20" fill="#333"/><rect width="84" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110"><text aria-hidden="true" x="315" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">coverage</text><text x="315" y="140" transform="scale(.1)" fill="#fff" textLength="510">coverage</text><text aria-hidden="true" x="715" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="130">??</text><text x="715" y="140" transform="scale(.1)" fill="#fff" textLength="130">??</text></g></svg>'
    )
