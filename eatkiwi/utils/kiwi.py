import argparse
import json
import time
import os
from pathlib import Path
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from decouple import config


# Define the Message class
class Message:
    def __init__(self, title, href, type_, timestamp):
        self.title = title
        self.href = href
        self.type = type_
        self.timestamp = timestamp


def get_unix_time():
    return int(time.time())

def sign(message):
    # hash = keccak(encode_abi_packed(['string'],[message]))
    message_hash = encode_defunct(text=message)
    Account.enable_unaudited_hdwallet_features()
    acct = Account.from_mnemonic(config("FARCASTER_MNEMONIC_DEV01"))
    print(f"sending from address: {acct.address}")
    signature = acct.sign_message(message_hash)
    return signature.messageHash.hex()

def create_message(href, title, type_):
    timestamp = get_unix_time()
    message = Message(title, href, type_, timestamp)
    message_json = json.dumps(message.__dict__)
    signature = sign(message_json)
    body = {
        "title": message.title,
        "href": message.href,
        "type": message.type,
        "timestamp": timestamp,
        "signature": signature,
    }
    print(body)
    return body

def send(message):
    try:
        response = requests.post("https://news.kiwistand.com/messages", json=message)
        print(response.text)
    except Exception as e:
        raise Exception("Failed sending message") from e

def send_link_to_kiwistand(href, title):
    message = create_message(href, title, "amplify")
    send(message)
