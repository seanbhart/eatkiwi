import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def truncate_string(s, max_length=80):
    return (s[:77] + '...') if len(s) > max_length else s

def check_url_contains_skip_list(url):
    parsed_url = urlparse(url)
    return 'kiwistand.com' in parsed_url.netloc or 'warpcast.com' in parsed_url.netloc


def has_link(text):
    """
    Returns True if the given text contains a link, False otherwise.
    """
    # Regular expression to match URLs
    url_regex = r"(https?://\S+)"

    # Search for URLs in the text
    match = re.search(url_regex, text)

    # Return True if a URL was found, False otherwise
    return bool(match)

def extract_link(text):
    """
    Returns the first URL found in the given text, or None if no URL is found.
    """
    # Regular expression to match URLs
    url_regex = r"(https?://\S+)"

    # Search for URLs in the text
    match = re.search(url_regex, text)

    # Return the URL if found, or None otherwise
    return match.group(1) if match else None

def get_page_title(url):
    """
    Returns the title of the web page at the given URL, or None if the title cannot be found.
    """
    if url is None:
        return None

    # Make a GET request to the URL
    response = requests.get(url)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the title tag in the HTML
    title_tag = soup.find("title")

    # Return the text of the title tag if found, or None otherwise
    return title_tag.text if title_tag else None
