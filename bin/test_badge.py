import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import urllib.parse


def get_page(url):
    try:
        with urllib.request.urlopen(url) as response:
            if response.getcode() == 200:
                return response.read().decode("utf-8")  # Return the content of the page
            else:
                raise ConnectionError("Error: Received status code", response.getcode())
    except urllib.error.URLError as e:
        raise e


def get_failures_from_xml(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    for testsuite in root.findall(".//testsuite"):
        if testsuite.get("name") == "pytest":
            failures = testsuite.get("failures")
            errors = testsuite.get("errors")
            return int(failures) if failures else 0, int(errors) if errors else 0

    # If 'testsuite' element with name='pytest' is not found
    print("No 'testsuite' element with name='pytest' found.")
    return None, None


if __name__ == "__main__":
    import sys

    xml_file_path = sys.argv[1]
    failures, errors = get_failures_from_xml(xml_file_path)

    url = f"http://192.168.4.6:8882/badge/"
    if failures is None or errors is None:
        text = "test-?-yellow"
    elif failures == 0 and errors == 0:
        text = "test-passed-green"
    else:
        text = "test-failed-red"

    try:
        content = get_page(url + urllib.parse.quote(text))
        if content:
            print(content)
    except:
        print(
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="84" height="20" role="img" aria-label="coverage: ??"><title>coverage: ??</title><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="84" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#r)"><rect width="61" height="20" fill="#555"/><rect x="61" width="23" height="20" fill="#333"/><rect width="84" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110"><text aria-hidden="true" x="315" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">coverage</text><text x="315" y="140" transform="scale(.1)" fill="#fff" textLength="510">coverage</text><text aria-hidden="true" x="715" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="130">??</text><text x="715" y="140" transform="scale(.1)" fill="#fff" textLength="130">??</text></g></svg>'
        )