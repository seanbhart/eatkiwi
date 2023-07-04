import re
import logging

from decouple import config
from pymongo import MongoClient
from farcaster import Warpcast
from farcaster.models import Parent
from eatkiwi.utils.links import get_page_content
from eatkiwi.utils.openai import generate_webpage_title_and_summary
from eatkiwi.utils.strings import trim_to_cast_max_bytes
from eatkiwi.farcaster.utils import error_reply


class Eat:
    EAT_PATTERN = r'\beat\b'

    def __init__(self, fcc: Warpcast, bot_fname, dev_mode):
        self.fcc = fcc
        self.bot_fname = bot_fname
        self.DEV_MODE = dev_mode
    

    def eat_offline_reply(self):
        if re.search(self.EAT_PATTERN):
            return "I'm sorry, but I'm not eating 🥝links🥝 right now."


    def check_text_after_eat(self, text):
        eat_command = re.search(self.EAT_PATTERN, text)
        if eat_command:
            text_after_eat = text[eat_command.end():].strip()
            return text_after_eat
        return None
    

    def check_text_between_eat_and_link(self, text):
        eat_command = re.search(self.EAT_PATTERN, text)
        link = re.search(r'https?://\S+', text)

        if eat_command and link:
            text_between = text[eat_command.end():link.start()].strip()
            return text_between
        else:
            return None
    

    def has_url(self, text):
        url_pattern = re.compile(r'https?://\S+')
        return bool(url_pattern.search(text))
    

    def cast(self, cast_to_eat, cast_requesting_eat, writing_style):
        """
        Creates an appropriate title and summary for the webpage at the given url, and replies to the
        requesting cast with both and a kiwinews intent link with the title and link.

        Args:
            cast_to_eat (Cast): The cast object to process.
            cast_requesting_eat (Cast): The cast object to reply to. BE SURE NOT TO PASS THE NOTIFICATION, BUT RATHER THE CAST INSIDE THE NOTIFICATION

        Returns:
            None
        """
        
        try:
            link, page_content = get_page_content(cast_to_eat.text)

            # the title / summary process will throw an error if it cannot process adequately
            title, summary = generate_webpage_title_and_summary(page_content, writing_style)

            # Record the link in the database so it isn't recasted from the stream
            mongo_client = MongoClient(config("MONGO_URL"))
            db = mongo_client[config("MONGO_DB_FC")]
            collection_links = db[config("MONGO_FC_COLLECTION_LINKS")]
            collection_links.insert_one({"link": link})

            # Remove quotations marks from the title and summary
            title = title.replace('"', '')
            summary = summary.replace('"', '')

            # Format the title for a url parameter
            title = title.replace(" ", "+")

            # Create the kiwinews intent link with the title and link
            kiwinews_link = f"https://news.kiwistand.com/submit?title={title}&url={link}"

            # the title might need trimming - gpt doesn't always follow length guidelines
            # be sure to put the kiwinews intent link first so it isn't trimmed
            cast_text = trim_to_cast_max_bytes(f"{kiwinews_link}\n{summary}")
            logging.info(f"[eat] Cast text: {cast_text}")
            self.fcc.post_cast(cast_text, parent=Parent(fid=cast_requesting_eat.author.fid, hash=cast_requesting_eat.hash))

        except Exception as e:
            logging.error(f"[eat] Failed sending message: {e}")
            error_reply(self.fcc, cast_requesting_eat)


    def eat_notification(self, notification):
        # If there is a url in the text, ignore any parent cast and assume the request is about the passed url
        if self.has_url(notification.content.cast.text):
            # Check whether a writing style was passed after "eat"
            writing_style = self.check_text_between_eat_and_link(notification.content.cast.text)
            self.cast(cast_to_eat=notification.content.cast, cast_requesting_eat=notification.content.cast, writing_style=writing_style)

        else:
            # check if the cast with the mention is a reply to another cast (presumably with the link)
            if notification.content.cast.parent_hash is not None:
                parent_cast = self.fcc.get_cast(notification.content.cast.parent_hash).cast
                writing_style = self.check_text_after_eat(notification.content.cast.text)
                self.cast(cast_to_eat=parent_cast, cast_requesting_eat=notification.content.cast, writing_style=writing_style)

            else:
                # There was no url, and there is no parent cast - nothing to process
                logging.info(f"[eat] No url found in cast {notification.content.cast.hash} and no parent cast found")
                self.fcc.post_cast("I'm happy to eat any 🥝link🥝 if you send me one!", parent=Parent(fid=notification.content.cast.author.fid, hash=notification.content.cast.hash))
