import logging

import openai
import threading
from decouple import config
from farcaster import Warpcast
from eatkiwi.commands.manager import Commands
from eatkiwi.farcaster.listeners import stream_casts, stream_notifications

# Set up env variables depending on the dev mode
dev_mode_string = config("DEV_MODE")
DEV_MODE = dev_mode_string.lower() == "true"
env_var_map = {
    "MNEMONIC": "FARCASTER_MNEMONIC_DEV01" if DEV_MODE else "FARCASTER_MNEMONIC_EATKIWI",
    "FNAME": "FARCASTER_FNAME_DEV01" if DEV_MODE else "FARCASTER_FNAME_EATKIWI",
    "OPENAI": "OPENAI_KEY" if DEV_MODE else "OPENAI_KEY",
}
MNEMONIC = config(env_var_map["MNEMONIC"])
FNAME = config(env_var_map["FNAME"])
OPENAI = config(env_var_map["OPENAI"])

def get_commands_instance():
    fcc = Warpcast(MNEMONIC, rotation_duration=1)
    openai.api_key = OPENAI
    bot_fname = FNAME

    return Commands(
        fcc=fcc,
        bot_fname=bot_fname,
        dev_mode=DEV_MODE
    )


def main():
    logging.basicConfig(
        level=logging.INFO if DEV_MODE else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("Configuring main function")
    try:
        commands_instance = get_commands_instance()
    except Exception as e:
        logging.error(f"Error occurred configuring main function: {e}")
        return

    logging.info("Starting stream threads.")
    t1 = threading.Thread(target=stream_casts, args=(commands_instance,))
    t2 = threading.Thread(target=stream_notifications, args=(commands_instance,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error occurred __main__ function: {e}")