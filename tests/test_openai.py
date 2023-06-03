import logging
import pytest
import openai
from decouple import config
from unittest.mock import MagicMock
from eatkiwi.utils.links import get_page_content
from eatkiwi.utils.openai import check_link_for_web3_content


test_urls = {
    1: "https://www.theblock.co/post/232983/republican-draft-bill-would-create-new-definition-of-decentralized-network",
    2: "https://news.google.com/articles/CBMiPmh0dHBzOi8vd3d3Lm55dGltZXMuY29tLzIwMjMvMDYvMDIvdXMvcG9saXRpY3MvYmlkZW4tZGVidC5odG1s0gEA?hl=en-US&gl=US&ceid=US%3Aen",
    3: "https://news.google.com/articles/CBMiZmh0dHBzOi8vd3d3LmJpempvdXJuYWxzLmNvbS9hdXN0aW4vbmV3cy8yMDIzLzA2LzAyL3NvbGFuYS1yYW5jaC1tdW5pY2lwYWwtdXRpbGl0eS1kaXN0cmljdC1hdXN0aW4uaHRtbNIBAA?hl=en-US&gl=US&ceid=US%3Aen",
    4: "https://news.google.com/articles/CBMiY2h0dHBzOi8vd3d3LmZveGJ1c2luZXNzLmNvbS9wZXJzb25hbC1maW5hbmNlL2dlbi16LW1pbGxlbmlhbHMtYmxlYWstb3V0bG9vay1maW5hbmNpYWwtZnV0dXJlcy1zdHVkedIBZ2h0dHBzOi8vd3d3LmZveGJ1c2luZXNzLmNvbS9wZXJzb25hbC1maW5hbmNlL2dlbi16LW1pbGxlbmlhbHMtYmxlYWstb3V0bG9vay1maW5hbmNpYWwtZnV0dXJlcy1zdHVkeS5hbXA?hl=en-US&gl=US&ceid=US%3Aen",
    5: "https://www.theblock.co/post/232996/bitcoin-is-now-more-stable-than-amazon-and-meta-shares-amid-uncommonly-low-volatility",
    6: "https://theintercept.com/2023/06/01/bluesky-owner-twitter-elon-musk/",
    7: "https://techcrunch.com/2022/07/25/the-race-to-build-a-social-media-platform-on-the-blockchain/",
    8: "https://medium.com/@Alex.Valaitis/is-the-future-of-twitter-decentralized-caffb2aa4c51",
    9: "https://nftz.me/nft/21169a1332d069fdeb46520deff59cc9f094124b82863485f213ca9f5c84e2c1",
    10: "https://sansa.xyz/asset/0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270/280000210"
}

def set_config():
    openai.api_key = config("OPENAI_KEY")

def test_check_link_for_web3_content_positive():
    set_config()
    link, page_content = get_page_content(test_urls[1])
    result = check_link_for_web3_content(page_content)
    logging.info(f"positive result: {result}")
    assert result == True
