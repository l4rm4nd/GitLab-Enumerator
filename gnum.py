import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import urllib3
from collections import defaultdict

# Predefined mapping of CSS filenames to GitLab versions
from gitlab_versions import CSS_VERSION_MAP

# Disable insecure request warnings, common for self-signed certs in internal networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_css_filenames(html_content):
    """
    Extracts CSS filenames from the HTML content.
    It parses the HTML using BeautifulSoup and looks for <link> tags
    with `rel="stylesheet"` or `rel="preload"` attributes, and a `href`
    attribute that ends with ".css".
    """
    soup = BeautifulSoup(html_content, "html.parser")
    css_links = soup.find_all("link", rel=["stylesheet", "preload"])
    css_files = []

    for link in css_links:
        href = link.get("href")
        if href and href.endswith(".css"):
            # Extract only the filename from the full URL/path
            # e.g., "https://example.com/assets/application-hash.css" -> "application-hash.css"
            css_file = href.split("/")[-1]
            css_files.append(css_file)

    return css_files


def enumerate_gitlab_version(target_url):
    """
    Fetches the target URL, extracts CSS filenames, and attempts to match them
    against known GitLab CSS hashes to enumerate potential GitLab versions.
    It collects all unique matched versions and returns them as a set.
    """
    try:
        print(f"[+] Fetching: {target_url}")
        # Make a GET request to the target URL.
        # `verify=False` is used to ignore SSL certificate verification errors,
        # `timeout=10` sets a 10-second timeout for the request,
        # `allow_redirects=False` prevents following HTTP redirects.
        response = requests.get(target_url, verify=False, timeout=10, allow_redirects=False)
    except requests.RequestException as e:
        # Catch and print any request-related errors (e.g., network issues, invalid URL).
        print(f"[!] Error requesting {target_url}: {e}")
        return None # Return None if an error occurs during the request

    # Check if the HTTP request was successful (status code 200 OK)
    if response.status_code != 200:
        print(f"[-] Got HTTP {response.status_code} from {target_url}")
        return None # Return None if the response status is not 200

    # Extract CSS filenames from the fetched HTML content
    css_files = extract_css_filenames(response.text)
    
    # Initialize a set to store all unique matched GitLab versions.
    # Using a set automatically handles duplicates, ensuring each version is listed only once.
    found_gitlab_versions = set()

    if len(css_files) > 0:
        print(f"[+] Found known CSS file(s) in page.")
        seen_css_files = set() # To keep track of CSS files already processed and avoid redundant output

        for css_file in css_files:
            # Skip if this CSS file has already been processed to avoid duplicate output
            if css_file in seen_css_files:
                continue
            seen_css_files.add(css_file)

            # Print the CSS file name if it contains "application-"
            if "application-" in css_file:
                print(f"    └── {css_file}")

            # Check if the extracted CSS file is a key in our predefined CSS_VERSION_MAP
            if css_file in CSS_VERSION_MAP:
                # Retrieve the list of versions associated with this CSS file
                matched_versions = CSS_VERSION_MAP[css_file]
                found_gitlab_versions.update(matched_versions)
    else:
        print("[-] No CSS files found in the page to match against known GitLab hashes.")

    # After iterating through all CSS files, report the overall findings
    if found_gitlab_versions:
        print("\n[+] Potential GitLab Versions:")
        # Sort the versions for consistent and readable output
        for version in sorted(list(found_gitlab_versions)):
            # Prepare version string
            cve_version = version.replace("gitlab-ce:", "").replace("gitlab-ee:", "").replace("-ce.0", "").replace("-ee.0", "")
            if "-ce.0" in version:
                cve_link = f"https://cve.ptf.one?cpe=cpe:2.3:a:gitlab:gitlab:{cve_version}:*:*:*:community:*:*:*"
            elif "-ee.0" in version:
                cve_link = f"https://cve.ptf.one?cpe=cpe:2.3:a:gitlab:gitlab:{cve_version}:*:*:*:enterprise:*:*:*"
            print(f"    - {version} >> {cve_link}")
        return found_gitlab_versions # Return the set of all unique versions found
    else:
        print()
        print("[-] No known GitLab CSS hash matched in any found CSS files.")
        print("    └── Please help fingerprinting GitLab versions:")
        print("     >> https://github.com/l4rm4nd/GitLab-Enumerator/blob/main/gitlab_versions.py")
        return None # Return None if no versions were detected


if __name__ == "__main__":
    import argparse
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="GitLab version detector via CSS hash enumeration")
    parser.add_argument("url", help="GitLab URL (e.g. https://gitlab.example.com/users/sign_in)")
    args = parser.parse_args()

    # Call the main function with the provided URL and print the final result
    detected_versions = enumerate_gitlab_version(args.url)