import time
import logging
import requests
from eth_account import Account
from eth_account.messages import encode_defunct, encode_structured_data
from decouple import config

def get_unix_time():
    return int(time.time())

# Define the Message class
class Message:
    def __init__(self, title, href, type_, timestamp):
        self.title = title
        self.href = href
        self.type = type_
        self.timestamp = timestamp

    def build(self):
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

def sign(message):
    # Create an account object from a mnemonic
    Account.enable_unaudited_hdwallet_features()
    acct = Account.from_mnemonic(config("FARCASTER_MNEMONIC_EATKIWI"))

    # Format and sign the message
    signable_message = encode_structured_data(message)
    signed_message = acct.sign_message(signable_message)
    return signed_message.signature.hex()

def create_message_data(href, title, type_):
    timestamp = get_unix_time()
    message = Message(title, href, type_, timestamp)
    message_eip712 = message.build()
    signature = sign(message_eip712)
    body = {
        "title": message.title,
        "href": message.href,
        "type": message.type,
        "timestamp": timestamp,
        "signature": signature,
    }
    return body

def send(data) -> bool:
    url = "https://news.kiwistand.com/api/v1/messages"
    
    try:
        response = requests.post(url, json=data)
        status_code = response.status_code

        if status_code == 200:  # OK
            logging.info('Message submission was successful')
            return True
        elif status_code == 201:  # Created
            logging.info('Message submission was successful and a resource was created')
            return True
        elif status_code == 400:  # Bad Request
            logging.error(f'There was a problem with the message submission. Check the data sent: {response.text}')
            return False
        elif status_code == 401:  # Unauthorized
            logging.error(f'The message submission lacks valid authentication credentials: {response.text}')
            return False
        elif status_code == 403:  # Forbidden
            logging.error(f'The server understood the message submission but refuses to authorize it: {response.text}')
            return False
        elif status_code == 404:  # Not Found
            logging.error(f'The requested resource could not be found: {response.text}')
            return False
        elif status_code == 500:  # Internal Server Error
            logging.error(f'The server encountered an internal error: {response.text}')
            return False
        else:
            logging.error(f'Received status code that is not handled: {status_code}')
            return False
        
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Unexpected Error: {err}")
    except Exception as e:
        logging.error(f"Failed sending message: {e}")
        raise Exception("Failed sending message") from e
    return False

def send_link_to_kiwistand(href, title):
    data = create_message_data(href, title, "amplify")
    return send(data)

def upvote_link_on_kiwistand(href):
    data = create_message_data(href, "", "amplify")
    return send(data)
