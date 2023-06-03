import logging
import pytest
import openai
from decouple import config
from unittest.mock import MagicMock
from eatkiwi.utils.links import get_page_content, check_url_contains_domains
from eatkiwi.utils.openai import check_link_for_web3_content, generate_webpage_title_and_summary


writing_styles = {
    1: "The New Yorker",
    2: "Wired",
    3: "TechCrunch",
    4: "The Block (crypto)",
    5: "Scooby-Doo voice",
    6: "SpongeBob SquarePants",
    7: "The Simpsons",
    8: "Seinfeld",
    9: "Old English",
    10: "Gothic",
    11: "Gangster",
    12: "Hemingway",
    13: "J.K. Rowling",
    14: "Stephen King",
    15: "David Foster Wallace",
    16: "Edgar Allen Poe",
    17: "George R.R. Martin",
    18: "J.R.R. Tolkien",
    19: "William Shakespeare",
    20: "Jane Austen",
    21: "Charles Dickens",
    22: "Mark Twain",
    23: "George Orwell",
    24: "Agatha Christie",
    25: "Oscar Wilde",
    26: "Emily Dickinson",
    27: "H.P. Lovecraft",
    28: "Arthur Conan Doyle",
    29: "A Pirate",
    30: "Hacker News",
    31: "magical realism, where fantastical elements blend seamlessly with reality",
    32: "stream of consciousness, where the character’s thoughts and emotions flow uninterrupted onto the page",
    33: "epistolary fiction, where the story is told through a series of letters, diary entries, or other documents",
    34: "flash fiction, where the entire story is condensed into a few hundred words or less",
    35: "experimental literature, where a traditional narrative structure is abandoned in favor of unconventional forms and techniques",
    36: "metafiction, where the story acknowledges its own status as a work of fiction",
    37: "noir fiction, where the protagonist is a cynical and hard-boiled detective navigating a corrupt world",
    38: "gothic literature, where dark, supernatural elements are woven into a brooding and atmospheric tale",
    39: "historical fiction, where the story is set in a specific time period and strives for historical accuracy",
    40: "bildungsroman, where the story follows the protagonist’s coming-of-age and personal growth",
}
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
test_url = 1
test_writing_style_key = 8

def set_config():
    openai.api_key = config("OPENAI_KEY")

def test_check_link_for_web3_content_positive():
    set_config()

    domains = config("BANNED_DOMAINS").split(',')
    logging.info(f"Checking link {test_urls[test_url]} for banned domains {domains}")
    if check_url_contains_domains(test_urls[test_url], domains): return

    link, page_content = get_page_content(test_urls[test_url])
    result = check_link_for_web3_content(page_content)
    assert isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], bool) and isinstance(result[1], str)

def test_writing_style():
    set_config()

    link, page_content = get_page_content(test_urls[test_url])
    logging.info(f"Generating title and summary of {link} with writing style {writing_styles[test_writing_style_key]}")
    result = generate_webpage_title_and_summary(page_content, writing_styles[test_writing_style_key])
    logging.info(f"Generated title and summary: {result}")
    assert isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], str) and isinstance(result[1], str) and len(result[0]) < 80 and len(result[1].encode('utf-8')) < 220
