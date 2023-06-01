import logging
logging.basicConfig(level=logging.INFO)

import threading
from decouple import config
from farcaster import Warpcast
from eatkiwi.listeners.farcaster import stream_casts, stream_notifications

dev = True
if dev:
    mnemonic = config("FARCASTER_MNEMONIC_DEV01")
    fname = config("FARCASTER_FNAME_DEV01")
else:
    mnemonic = config("FARCASTER_MNEMONIC_EATKIWI")
    fname = config("FARCASTER_FNAME_EATKIWI")

# The client will automagically cycle through access tokens
client = Warpcast(mnemonic, rotation_duration=1)

def main():
    t1 = threading.Thread(target=stream_casts, args=(client, fname))
    t2 = threading.Thread(target=stream_notifications, args=(client, fname))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == "__main__":
    main()