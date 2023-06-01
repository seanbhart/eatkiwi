import logging
from decouple import config
from pymongo import MongoClient
from farcaster.models import Parent
from eatkiwi.utils.bytes import cut_off_string
from eatkiwi.utils.links import extract_link, get_page_title
from eatkiwi.utils.kiwi import send_link_to_kiwistand


def trim_to_cast(s):
    return cut_off_string(s, 320)

def stream_notifications(client, fname):
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

            # check if cast has the word "eat" in it
            # if it does get the original cast and send the link to kiwistand
            if "eat" in cast.content.cast.text.lower() and cast.content.cast.parent_hash is not None:

                logging.info(f"cast parent_hash: {cast.content.cast.parent_hash}")
                original_cast = client.get_cast(cast.content.cast.parent_hash).cast
                logging.info(f"original_cast: {original_cast}")
                logging.info(f"original_cast text: {original_cast.text}")
                if hasattr(original_cast, 'embeds'):
                    logging.info(f"original_cast embeds: {original_cast.embeds}")
                if hasattr(original_cast, 'attachments'):
                    logging.info(f"original_cast attachments: {original_cast.attachments}")

                # # ensure the parent cast is from the bot
                # if original_cast.author.username != fname:
                #     logging.info("parent cast is not from bot, ending")
                #     logging.info("----")
                #     continue

                link = extract_link(original_cast.text)
                if link is None:
                    # try to find an embedded link or an attachment link
                    if hasattr(original_cast, 'embeds') and original_cast.embeds is not None:
                        if original_cast.embeds[0].url is not None:
                            link = original_cast.embeds[0].url
                        else:
                            logging.info("no embedded link found in original cast, ending")
                            logging.info("----")
                    elif hasattr(original_cast, 'attachments') and original_cast.attachments is not None:
                        if original_cast.attachments[0].open_graph.url is not None:
                            link = original_cast.attachments[0].open_graph.url
                        else:
                            logging.info("no attachment link found in original cast, ending")
                            logging.info("----")

                    logging.info("no link found in original cast, ending")
                    logging.info("----")
                    continue

                logging.info(f"found link in original cast: {link}")
                title = get_page_title(link)
                logging.info(f"title: {title}")
                logging.info("----")
                
                # send link to kiwistand
                # logging.info(f"sending link to kiwistand: {title}, {link}")
                send_link_to_kiwistand(link, title)
            pass

def stream_casts(client, fname):
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

            if link is not None and title is not None and title != "" and title != " " and title != "Access denied":
                # check if link has already been posted
                result = collection.find_one({"link": link})
                if result:
                    logging.info("link already exists.")
                    continue

                # save the link to mongo
                collection.insert_one({"link": link})

                # post the link to fc
                logging.info(f"posting: {title} | {link}")
                try:
                    # Post links directly in the text, not as an attachment or embed
                    # to ensure the link is visible in the cast received by the notification stream
                    client.post_cast(f"Posted by @{current_cast.author.username}\n\n\"{title}\"\n{link}\nhttps://warpcast.com/{current_cast.author.username}/{current_cast.hash}")
                except Exception as e:
                    logging.error(f"Failed sending message: {e}")
                    raise Exception("Failed sending message") from e
                                
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
