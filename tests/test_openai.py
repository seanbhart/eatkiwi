import logging
import pytest
import openai
from decouple import config
from unittest.mock import MagicMock
from eatkiwi.utils.links import get_page_content, check_url_contains_domains
from eatkiwi.utils.openai import check_link_for_web3_content


test_urls = {
    1: "https://www.theblock.co/post/232983/republican-draft-bill-would-create-new-definition-of-decentralized-network",
    2: "https://news.yahoo.com/what-did-all-that-debt-ceiling-drama-actually-accomplish-181153866.html?guccounter=1&guce_referrer=aHR0cHM6Ly9uZXdzLmdvb2dsZS5jb20v&guce_referrer_sig=AQAAABLT6BLfShfQ5lCcUGIUeMpfKWHVamgHqGA3l_x6GvGgTyyZ1XujYLrCM2RRdDnxBGsUAA8nqrSUcPq2iitd_1lG2EJE6qg_igWXJnpBb2EWiBxtTcf0njJyrOh2Kb8-5U1YR9DI23Eu0RHRXH3WcCrh-Co20UfHJ7_8I4pOVXh1",
    3: "https://www.bizjournals.com/austin/news/2023/06/02/solana-ranch-municipal-utility-district-austin.html",
    4: "https://www.cnn.com/2023/06/02/asia/austin-shangri-law-dialogue-speech-taiwan-intl-hnk/index.html",
    5: "https://www.theblock.co/post/232996/bitcoin-is-now-more-stable-than-amazon-and-meta-shares-amid-uncommonly-low-volatility",
    6: "https://theintercept.com/2023/06/01/bluesky-owner-twitter-elon-musk/",
    7: "https://techcrunch.com/2022/07/25/the-race-to-build-a-social-media-platform-on-the-blockchain/",
    8: "https://medium.com/@Alex.Valaitis/is-the-future-of-twitter-decentralized-caffb2aa4c51",
    9: "https://nftz.me/nft/21169a1332d069fdeb46520deff59cc9f094124b82863485f213ca9f5c84e2c1",
    10: "https://sansa.xyz/asset/0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270/280000210"
}
test_url_to_test = 8

def set_config():
    openai.api_key = config("OPENAI_KEY")

def test_check_link_for_web3_content_positive():
    set_config()

    domains = config("BANNED_DOMAINS").split(',')
    logging.info(f"Checking link {test_urls[test_url_to_test]} for banned domains {domains}")
    if check_url_contains_domains(test_urls[test_url_to_test], domains): return

    link, page_content = get_page_content(test_urls[test_url_to_test])
    result = check_link_for_web3_content(page_content)
    assert isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], bool) and isinstance(result[1], str)
