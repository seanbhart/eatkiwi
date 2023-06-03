"""
This module contains functions for sending messages and links to Kiwistand.

Classes:
    Message: Represents a message to be sent to Kiwistand.

Functions:
    create_message_data(title: str, href: str, mnemonic: str) -> Dict[str, Union[str, Dict[str, str]]]:
        Creates a dictionary representing the message data to be sent to Kiwistand.

    send_link_to_kiwistand(href: str, title: str, mnemonic: str) -> None:
        Sends a link to Kiwistand for submission.

"""

from eth_account import Account
from eth_account.messages import encode_structured_data
from eatkiwi.utils.numbers import get_unix_time
from eatkiwi.utils.url import send_post_request


KIWI_MESSAGES_URL = "https://news.kiwistand.com/api/v1/messages"

class Message:
    """
    Represents a message to be sent to Kiwistand.

    Attributes:
        title (str): The title of the message.
        href (str): The URL of the message.
        type_ (str): The type of the message.
        timestamp (int): The timestamp of the message.

    """
    
    def __init__(self, title, href, type_, timestamp):
        self.title = title
        self.href = href
        self.type = type_
        self.timestamp = timestamp

    def build(self) -> dict:
        """
        Builds and returns a dictionary representing the message in EIP-712 format.

        Returns:
            dict: A dictionary representing the message in EIP-712 format.

        """
        return {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "salt", "type": "bytes32"},
                ],
                "Message": [
                    {"name": "title", "type": "string"},
                    {"name": "href", "type": "string"},
                    {"name": "type", "type": "string"},
                    {"name": "timestamp", "type": "uint256"},
                ],
            },
            "domain": {
                "name": "kiwinews",
                "version": "1.0.0",
                "salt": bytes.fromhex("fe7a9d68e99b6942bb3a36178b251da8bd061c20ed1e795207ae97183b590e5b"),
            },
            "primaryType": "Message",
            "message": {
                "title": self.title,
                "href": self.href,
                "type": self.type,
                "timestamp": self.timestamp,
            },
        }


def sign(message, mnemonic) -> str:
    """
    Signs a message using the provided private key.

    Args:
        message (Dict[str, Any]): The message to sign.
        private_key (str): The private key to use for signing.

    Returns:
        str: The signature of the message.

    """
    Account.enable_unaudited_hdwallet_features()
    acct = Account.from_mnemonic(mnemonic)
    signable_message = encode_structured_data(message)
    signed_message = acct.sign_message(signable_message)
    return signed_message.signature.hex()


def create_message_data(href, title, type_, mnemonic) -> dict:
    """
    Creates a dictionary representing the message data to be sent to Kiwistand.

    Args:
        href (str): The URL of the article.
        title (str): The title of the article.
        type_ (str): The type of the article.
        mnemonic (str): The mnemonic to use for signing the message.

    Returns:
        dict: A dictionary representing the message data to be sent to Kiwistand.

    """
    timestamp = get_unix_time()
    message = Message(title, href, type_, timestamp)
    message_eip712 = message.build()
    signature = sign(message_eip712, mnemonic)
    body = {
        "title": message.title,
        "href": message.href,
        "type": message.type,
        "timestamp": timestamp,
        "signature": signature,
    }
    return body


def send_link_to_kiwistand(href, title, mnemonic) -> bool:
    """
    Sends a link to Kiwistand for submission.

    Args:
        href (str): The URL of the article to submit.
        title (str): The title of the article to submit.
        mnemonic (str): The mnemonic to use for signing the message.

    Returns:
        requests.Response: The response from the Kiwistand API.

    Raises:
        requests.exceptions.RequestException: If an error occurs while sending the request.

    """
    data = create_message_data(href, title, "amplify", mnemonic)
    return send_post_request(KIWI_MESSAGES_URL, data)


def upvote_link_on_kiwistand(href, mnemonic) -> bool:
    data = create_message_data(href, "", "amplify", mnemonic)
    return send_post_request(KIWI_MESSAGES_URL, data)
