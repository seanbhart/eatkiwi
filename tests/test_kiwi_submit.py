import logging
from getpass import getpass
from eatkiwi.utils.kiwi import create_message, send

def send_test_link_to_kiwistand(href, title):
    """
    This function sends a test link to Kiwistand. 

    The link provided should be an original link, indicating that it's the 
    first submission. It's important that the link hasn't been previously 
    submitted to ensure accurate testing and analysis.
    """
    message = create_message(href, title, "amplify")
    send(message)

if __name__ == "__main__":
    href = "https://www.theblock.co/post/232604/coinbase-ceo-cites-rising-threat-from-china-in-fresh-plea-to-us-officials"
    title = "Coinbase CEO cites rising threat from China in fresh plea to US officials"
    send_test_link_to_kiwistand(href, title)
