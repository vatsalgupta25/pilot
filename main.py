import sys
from urllib.parse import urlparse
from pilot import pilot

def is_valid_url(url: str) -> bool:
    """
    Validates if a given string is a valid URL.
    Checks for the presence of a scheme (http/https) and network location (domain).
    """
    try:
        result = urlparse(url)
        # A valid URL should at least have a scheme (e.g., http) and a netloc (e.g., google.com)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

def main():
    # Allow passing URL as a command line argument or prompt for it
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Please enter a URL to shorten: ")

    url = url.strip()

    # Prepend https:// if a scheme is missing so urlparse works correctly
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    if is_valid_url(url):
        print(f"\n[Success] Received valid URL: {url}")
        short_url = pilot(url)
        print(f"[Shortened] Your short URL is: {short_url}")
    else:
        print(f"\n[Error] Invalid URL provided: '{url}'. Make sure it includes http:// or https://")

if __name__ == "__main__":
    main()
#this comment exists.