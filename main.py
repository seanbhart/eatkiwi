import logging
logging.basicConfig(level=logging.INFO)

from decouple import config
from farcaster import Warpcast
from eatkiwi.listeners.farcaster import stream_casts, stream_notifications


mnemonic = config("FARCASTER_MNEMONIC_DEV01")
fname = config("FARCASTER_FNAME_DEV01")

# The client will automagically cycle through access tokens
client = Warpcast(mnemonic, rotation_duration=1)

if __name__ == "__main__":
    stream_notifications(client, fname)
