import logging
import openai
import pytest
from decouple import config
from farcaster import Warpcast
from farcaster.models import ApiUser, ApiCast
from eatkiwi.commands.eat import Eat


def set_config():
    openai.api_key = config("OPENAI_KEY")


@pytest.fixture
def fcc_instance():
    fcc = Warpcast(config("FARCASTER_MNEMONIC_DEV01"), rotation_duration=1)
    return fcc


def test_get_cast(fcc_instance):
    set_config()

    # Call the cast method
    cast = fcc_instance.get_cast("0x62adcf85c2641bd88256080b2a0391813b06aeca")
    logging.info(f"Cast: {cast}")
