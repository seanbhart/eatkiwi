
import openai
import pytest
from decouple import config
from farcaster import Warpcast
from farcaster.models import ApiUser, ApiCast
from eatkiwi.commands.eat import Eat


def set_config():
    openai.api_key = config("OPENAI_KEY")


@pytest.fixture
def eat_instance():
    fcc = Warpcast(config("FARCASTER_MNEMONIC_DEV01"), rotation_duration=1)
    bot_fname = config("FARCASTER_FNAME_DEV01")
    dev_mode = True
    return Eat(fcc, bot_fname, dev_mode)


def test_cast_success(eat_instance):
    set_config()

    # Create Cast objects
    cast_to_eat = ApiCast(
        hash="cast_hash",
        thread_hash=None,
        parent_hash=None,
        author=ApiUser(fid=1, profile={"bio": {"text": "value", "mentions": ["mention"]}}, follower_count=10, following_count=5),
        parent_author=None,
        parent_source=None,
        text="https://www.theblock.co/post/232754/multichain-team-says-it-cant-contact-ceo-amid-protocol-problems",
        timestamp=1,
        mentions=None,
        attachments=None,
        embeds=None,
        ancestors=None,
        replies={"count": 0},
        reactions={"count": 0},
        recasts={"count": 0},
        watches={"count": 0},
        deleted=None,
        recast=None,
        viewer_context=None
    )
    cast_requesting_eat = ApiCast(
        hash="cast_hash",
        thread_hash=None,
        parent_hash=None,
        author=ApiUser(fid=2, profile={"bio": {"text": "value", "mentions": ["mention"]}}, follower_count=10, following_count=5),
        parent_author=None,
        parent_source=None,
        text="@fcdevtest01",
        timestamp=1,
        mentions=None,
        attachments=None,
        embeds=None,
        ancestors=None,
        replies={"count": 0},
        reactions={"count": 0},
        recasts={"count": 0},
        watches={"count": 0},
        deleted=None,
        recast=None,
        viewer_context=None
    )

    # Call the cast method
    eat_instance.cast(cast_to_eat, cast_requesting_eat, None)
