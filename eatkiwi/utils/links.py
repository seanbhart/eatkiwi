import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def check_url_contains_domains(url, domains):
    parsed_url = urlparse(url)
    return any(domain in parsed_url.netloc for domain in domains)

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

    try:
        # Send a GET request
        response = requests.get(url)
        # If the GET request is successful, the status code will be 200
        if response.status_code == 200:
            # Make a GET request to the URL
            response = requests.get(url)

            # Parse the HTML response using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the title tag in the HTML
            title_tag = soup.find("title")

            # Return the text of the title tag if found, or None otherwise
            return title_tag.text if title_tag else None
    except Exception as e:
        logging.error(f"Error during requests to {url} : {str(e)}")
        return None

def get_text_from_webpage(url):
    logging.info(f"Getting text from {url}")
    try:
        # Send a GET request
        response = requests.get(url, timeout=5)
        # If the GET request is successful, the status code will be 200
        if response.status_code == 200:
            # Get the content of the response
            webpage_content = response.content
            # Create a Beautiful Soup object and specify the parser
            soup = BeautifulSoup(webpage_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get the text from the Beautiful Soup object
            text = soup.get_text(separator=" ")
            # Return the text
            return text
    except Exception as e:
        logging.error(f"Error during requests to {url} : {str(e)}")
        return None
