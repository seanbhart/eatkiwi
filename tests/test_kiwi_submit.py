import logging
logging.basicConfig(level=logging.info)

from decouple import config
from eatkiwi.kiwi.message import send_link_to_kiwistand


MNEMONIC = config("FARCASTER_MNEMONIC_DEV01")

if __name__ == "__main__":
    """
    This function sends a test link to Kiwistand. 

    The link provided should be an original link, indicating that it's the 
    first submission. It's important that the link hasn't been previously 
    submitted to ensure accurate testing and analysis.
    """
    href = "https://www.theblock.co/post/232604/coinbase-ceo-cites-rising-threat-from-china-in-fresh-plea-to-us-officials"
    title = "Coinbase CEO cites rising threat from China in fresh plea to US officials"
    send_link_to_kiwistand(href, title, MNEMONIC)
