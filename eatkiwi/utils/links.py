"""
This module provides functions for working with URLs and web pages.

"""
import re
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse


def check_url_contains_domains(url, domains) -> bool:
    """
    Checks if the given URL contains any of the specified domains.

    Args:
        url (str): The URL to check.
        domains (List[str]): A list of domain names to check for.

    Returns:
        bool: True if the URL contains any of the specified domains, False otherwise.

    """
    parsed_url = urlparse(url)
    return any(domain in parsed_url.netloc.split('.') for domain in domains)


def has_link(text) -> bool:
    """
    Returns True if the given text contains a link, False otherwise.

    Args:
        text (str): The text to search for a link.

    Returns:
        bool: True if a link is found, False otherwise.

    """
    # Regular expression to match URLs
    url_regex = r"(https?://\S+)"
    match = re.search(url_regex, text)

    return bool(match)


def extract_link(text) -> Optional[str]:
    """
    Returns the first URL found in the given text, or None if no URL is found.

    Args:
        text (str): The text to search for a URL.

    Returns:
        Optional[str]: The first URL found in the text, or None if no URL is found.

    """
    # Regular expression to match URLs
    url_regex = r"(https?://\S+)"
    match = re.search(url_regex, text)

    return match.group(1) if match else None


def get_page_title(url) -> Optional[str]:
    """
    Returns the title of the web page at the given URL, or None if the title cannot be retrieved.

    Args:
        url (str): The URL of the web page to retrieve the title from.

    Returns:
        Optional[str]: The title of the web page, or None if the title cannot be retrieved.

    """
    if url is None:
        return None

    try:
        response = requests.get(url)
        if response.status_code == 200:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            title_tag = soup.find("title")

            return title_tag.text if title_tag else None
    except Exception as e:
        logging.error(f"Error during requests to {url} : {str(e)}")
        return None


def get_text_from_webpage(url) -> Optional[str]:
    """
    Retrieves the text content of a web page at the given URL.

    Args:
        url (str): The URL of the web page to retrieve.

    Returns:
        Optional[str]: The text content of the web page, or None if the page cannot be retrieved.

    """
    logging.debug(f"Getting text from {url}")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            webpage_content = response.content
            soup = BeautifulSoup(webpage_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=" ")

            return text
    except Exception as e:
        logging.error(f"Error during requests to {url} : {str(e)}")
        return None


def get_page_content(text) -> str:
    link = extract_link(text)
    if link is None:
        raise ValueError("Link is None")

    try:
        page_content = get_text_from_webpage(link)
    except Exception as e:
        logging.error(f"Error getting page content for {link} : {str(e)}")
        raise ValueError("Error getting page content")
    
    return page_content
