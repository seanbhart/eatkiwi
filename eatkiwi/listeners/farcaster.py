import logging
from decouple import config
from pymongo import MongoClient
from farcaster.models import Parent
from eatkiwi.utils.bytes import cut_off_string
from eatkiwi.utils.links import extract_link, get_page_title
from eatkiwi.utils.kiwi import send_link_to_kiwistand


def trim_to_cast(s):
    return cut_off_string(s, 320)

def stream_notifications(client):
    # Stream new casts mentioning the chatbot, find the link in the cast, and post to kiwistand
    for cast in client.stream_notifications(skip_existing=True):
        if cast:
            logging.info(f"hash: {cast.content.cast.hash}:")
            logging.info(f"parent_hash: {cast.content.cast.parent_hash}:")
            logging.info(f"thread_hash: {cast.content.cast.thread_hash}:")
            logging.info(f"text: {cast.content.cast.text}:")
            logging.info(f"mentions: {cast.content.cast.mentions}:")
            logging.info(f"reactions: {cast.content.cast.reactions}:")
            logging.info(f"username: {cast.actor.username}:")
            logging.info(f"display_name: {cast.actor.display_name}:")
            logging.info("----")

            link = extract_link(cast.text)
            logging.info(f"link: {link}")
            title = get_page_title(link)
            logging.info(f"title: {title}")

            if link is not None and title is not None:
                # post the link to kiwistand
                # send_link_to_kiwistand(link, title)
                logging.info(f"would post to kiwistand: {title} | {link}")
            else:
                logging.info("no link found - searching parent cast(s)")

                # search parent casts for a link and loop upwards until a link is found
                found_link = False
                while found_link is False and current_cast.parent_hash is not None:
                    logging.info(f"current_cast parent_hash: {current_cast.parent_hash}")
                    current_cast = client.get_cast(current_cast.parent_hash).cast
                    logging.info(f"current_cast text: {current_cast.text}")

                    link = extract_link(current_cast.text)
                    if link is None:
                        # no link found in parent cast, continue searching
                        logging.info("no link found in parent cast, continuing search")
                        logging.info("----")
                        continue

                    found_link = True
                    logging.info(f"found link in parent cast: {link}")
                    title = get_page_title(link)
                    logging.info(f"title: {title}")
                    logging.info("----")

            # last_cast = client.post_cast(m, parent=Parent(fid=cast.actor.fid, hash=cast.content.cast.hash))
            pass

def stream_casts(client):
    logging.info("streaming casts")

    # Connect to MongoDB server
    mongo_client = MongoClient(config("MONGO"))
    # Choose the database and collection
    db = mongo_client[config("MONGO_DB_FC")]
    collection = db[config("MONGO_FC_COLLECTION_LINKS")]

    # Stream new casts, and if a link is found, post to kiwistand
    for cast in client.stream_casts():
        if cast:
            current_cast = cast
            logging.info(f"{current_cast.author.username}:")
            logging.info(current_cast.text)
            logging.info(current_cast)
            logging.info("----")

            link = extract_link(current_cast.text)
            logging.info(f"link: {link}")
            title = get_page_title(link)
            logging.info(f"title: {title}")

            if link is not None and title is not None:
                # check if link has already been posted
                result = collection.find_one({"link": link})
                if result:
                    logging.info("link already exists.")
                    continue

                # save the link to mongo
                collection.insert_one({"link": link})

                # post the link to fc
                logging.info(f"posting: {title} | {link}")
                client.post_cast(f"Posted by @{current_cast.author.username}\n\n\"{title}\"", embeds=[link])
            # else:
            #     logging.info("no link found - searching parent cast(s)")

            #     # search parent casts for a link and loop upwards until a link is found
            #     found_link = False
            #     while found_link is False and current_cast.parent_hash is not None:
            #         logging.info(f"current_cast parent_hash: {current_cast.parent_hash}")
            #         current_cast = client.get_cast(current_cast.parent_hash).cast
            #         logging.info(f"current_cast text: {current_cast.text}")

            #         link = extract_link(current_cast.text)
            #         if link is None:
            #             # no link found in parent cast, continue searching
            #             logging.info("no link found in parent cast, continuing search")
            #             logging.info("----")
            #             continue

            #         found_link = True
            #         logging.info(f"found link in parent cast: {link}")
            #         title = get_page_title(link)
            #         logging.info(f"title: {title}")
            #         logging.info("----")
            #         # post the link to eatkiwi
            #         client.post_cast(f"link posted by {current_cast.author.display_name}", embeds=[link])
