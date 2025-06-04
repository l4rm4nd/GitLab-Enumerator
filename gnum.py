import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import urllib3

# Predefined mapping of CSS filenames to GitLab versions
from gitlab_versions import CSS_VERSION_MAP 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_css_filenames(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    css_links = soup.find_all("link", rel=["stylesheet", "preload"])
    css_files = []

    for link in css_links:
        href = link.get("href")
        if href and href.endswith(".css"):
            css_file = href.split("/")[-1]
            css_files.append(css_file)

    return css_files


def enumerate_gitlab_version(target_url):
    try:
        print(f"[+] Fetching: {target_url}")
        response = requests.get(target_url, verify=False, timeout=10, allow_redirects=False)
    except requests.RequestException as e:
        print(f"[!] Error requesting {target_url}: {e}")
        return

    if response.status_code != 200:
        print(f"[-] Got HTTP {response.status_code} from {target_url}")
        return

    css_files = extract_css_filenames(response.text)
    if len(css_files) > 0:
        print(f"[+] Found target CSS file(s) in page.")
        seen = set()

        for css_file in css_files:
            if css_file in seen:
                continue
            seen.add(css_file)

            if "application-" in css_file:
                print(f"    └── {css_file}")

            if css_file in CSS_VERSION_MAP:
                print(f"[+] Matched CSS: {css_file}")
                print(f"[+] GitLab Version: {CSS_VERSION_MAP[css_file]}")
                return CSS_VERSION_MAP[css_file]

    print("[-] No known GitLab CSS hash matched.")
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GitLab version detector via CSS hash enumeration")
    parser.add_argument("url", help="GitLab URL (e.g. https://gitlab.example.com/users/sign_in)")
    args = parser.parse_args()

    enumerate_gitlab_version(args.url)
