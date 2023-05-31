import logging
from getpass import getpass
from eatkiwi.utils.kiwi import create_message, send

def upvote_link_on_kiwistand(href):
    """
    This function sends a test link to Kiwistand. 

    The link provided should be an original link, indicating that it's the 
    first submission. It's important that the link hasn't been previously 
    submitted to ensure accurate testing and analysis.
    """
    message = create_message(href, "", "vote")
    send(message)

if __name__ == "__main__":
    href = "https://www.theblock.co/post/232604/coinbase-ceo-cites-rising-threat-from-china-in-fresh-plea-to-us-officials"
    upvote_link_on_kiwistand(href)
