import logging
logging.basicConfig(level=logging.INFO)

from eatkiwi.listeners.farcaster import stream_casts


if __name__ == "__main__":
    stream_casts()
