import logging
logging.basicConfig(level=logging.INFO)

from decouple import config
from farcaster import Warpcast
from eatkiwi.listeners.farcaster import stream_casts, stream_notifications


if __name__ == "__main__":
    # The client will automagically cycle through access tokens
    client = Warpcast(config("FARCASTER_MNEMONIC_DEV01"), rotation_duration=1)
    stream_casts(client)
