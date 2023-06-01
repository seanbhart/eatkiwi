import logging
from decouple import config
from pymongo import MongoClient
from farcaster.models import Parent
from eatkiwi.utils.strings import truncate_string_by_character, trim_generated_cast, remove_substrings, trim_to_cast_max_bytes
from eatkiwi.utils.links import extract_link, get_page_title, check_url_contains_domains, get_text_from_webpage
from eatkiwi.utils.openai import generate_webpage_title, generate_webpage_title_and_summary, generate_pithy_reply
from eatkiwi.utils.kiwi import send_link_to_kiwistand


def error_reply(client, cast):
    try:
        client.post_cast(f"something went wrong. I think I lost my 🥝", parent=Parent(fid=cast.content.cast.author.fid, hash=cast.content.cast.hash))
    except Exception as e:
        logging.error(f"Failed sending message: {e}")

def eat_kiwi_cast(client, fname, mnemonic, dev=False):
    # Stream new casts mentioning the chatbot, find the link in the cast, and post to kiwistand
    for cast in client.stream_notifications(skip_existing=True):
        if not cast:
            continue
            
        # check if cast has the word "eat" in it
        # if it does get the original cast and send the link to kiwistand
        if "eat" not in cast.content.cast.text.lower() or cast.content.cast.parent_hash is None:
            continue
        
        # ensure the parent cast (original cast) is from the bot
        original_cast = client.get_cast(cast.content.cast.parent_hash).cast
        if original_cast.author.username != fname:
            logging.warn("STRANGE BEHAVIOR: parent cast is not from bot, ending")
            continue

        link = extract_link(original_cast.text)
        if link is None:
            # try to find an embedded link or an attachment link
            if hasattr(original_cast, 'embeds') and original_cast.embeds is not None:
                if original_cast.embeds[0].url is not None:
                    link = original_cast.embeds[0].url
            elif hasattr(original_cast, 'attachments') and original_cast.attachments is not None:
                if original_cast.attachments[0].open_graph.url is not None:
                    link = original_cast.attachments[0].open_graph.url
            continue

        # check if link is from urls to skip
        domains = ["kiwistand.com", "warpcast.com", "alphacaster.xyz"]
        if check_url_contains_domains(link, domains):
            continue

        # title = get_page_title(link)
        page_content = get_text_from_webpage(link)
        title = generate_webpage_title(page_content)

        if title is None or title == "" or title == " " or title == "Access denied":
            continue

        # send link to kiwistand
        # truncate the title to the max kiwi post length (80 characters)
        title = truncate_string_by_character(title, max_characters=80)
        if send_link_to_kiwistand(link, title, mnemonic):
            try:
                # add a reaction to the notifying cast
                client.post_cast("🥝 nom nom nom\nhttps://news.kiwistand.com/new", parent=Parent(fid=cast.content.cast.author.fid, hash=cast.content.cast.hash))
            except Exception as e:
                logging.error(f"Failed sending message: {e}")
                error_reply(client, cast)


def get_title_and_summary(cast):
    # otherwise check if a link exists in the parent cast and create a humorous response
    link = extract_link(cast.text)
    if link is None:
        return

    # title = get_page_title(link)
    page_content = get_text_from_webpage(link)
    if page_content is None:
        return

    title, summary = generate_webpage_title_and_summary(page_content)
    if title is None or summary is None:
        return

    # remove any substrings from the title and summary
    substrings_to_remove = ["Title: ", "Summary: "]
    title = remove_substrings(title, substrings_to_remove)
    summary = remove_substrings(summary, substrings_to_remove)
    if title is None or title == "" or title == " " or title == "Access denied":
        return
    
    return title, summary

def mention_reply(client, fname, cast):
    # it's a reply mention, so get the original cast (parent cast)
    original_cast = client.get_cast(cast.content.cast.parent_hash).cast

    # check if cast has the word "eat" in it
    # if it does get the original cast and send the link to kiwistand
    if "eat" in cast.content.cast.text.lower():

        # if the parent cast (original cast) is the bot, reply that the eat command is not supported
        if original_cast.author.username == fname:
            logging.warn("someone sent an 'eat' reply to bot")

            # reply to the cast
            reply = generate_pithy_reply()
            cast_text = trim_to_cast_max_bytes(reply)
            try:
                client.post_cast(f"{cast_text} 🥝", parent=Parent(fid=cast.content.cast.author.fid, hash=cast.content.cast.hash))
            except Exception as e:
                logging.error(f"Failed sending message: {e}")
                error_reply(client, cast)
            return

    #TODO: figure out errors in below code
    # title_summary = get_title_and_summary(original_cast)
    # logging.info(f"Title and summary: {title_summary}")
    # if title_summary is None:
    #     error_reply(client, cast)
    #     return
    
    # title, summary = title_summary
    # logging.info(f"Title: {title}, Summary: {summary}")
    # if title is None or summary is None:
    #     error_reply(client, cast)
    #     return
    
    # try:
    #     # Post a reply to the cast with a trimmed title and summary (if needed)
    #     cast_text = trim_to_cast_max_bytes(f"{title}\n{summary}")
    #     logging.info(f"Replying to cast with: {cast_text}")
    #     client.post_cast(cast_text, parent=Parent(fid=cast.content.cast.author.fid, hash=cast.content.cast.hash))

    # except Exception as e:
    #     logging.error(f"Failed sending message: {e}")
    #     error_reply(client, cast)

#TODO: figure out errors in below code
def mention(client, cast):
    logging.info(f"Received mention: {cast.content.cast.text}")
    title_summary = get_title_and_summary(cast.content.cast)
    logging.info(f"Title and summary: {title_summary}")
    if title_summary is None:
        error_reply(client, cast)
        return
    
    title, summary = title_summary
    logging.info(f"Title: {title}, Summary: {summary}")
    if title is None or summary is None:
        error_reply(client, cast)
        return
    
    try:
        # Post a reply to the cast with a trimmed title and summary (if needed)
        cast_text = trim_to_cast_max_bytes(f"{title}\n{summary}")
        logging.info(f"Replying to cast with: {cast_text}")
        client.post_cast(cast_text, parent=Parent(fid=cast.content.cast.author.fid, hash=cast.content.cast.hash))

    except Exception as e:
        logging.error(f"Failed sending message: {e}")
        error_reply(client, cast)

def stream_notifications(client, fname, mnemonic, dev=False):
    logging.info("streaming notifications")
    # eat_kiwi_cast(client, fname, mnemonic, dev=dev)
    
    # Stream new casts mentioning the chatbot, find the link in the cast, and post to kiwistand
    for cast in client.stream_notifications(skip_existing=True):
        if not cast:
            continue

        # # check if the cast with the mention is a reply to another cast (presumably with the link)
        # if cast.content.cast.parent_hash is None:
        #     mention(client, cast)
        # else:
        #     mention_reply(client, fname, cast)

        if cast.content.cast.parent_hash is not None:
            mention_reply(client, fname, cast)

def stream_casts(client, fname, dev=False):
    logging.info("streaming casts")

    # Connect to MongoDB server
    mongo_client = MongoClient(config("MONGO_URL"))
    # Choose the database and collection
    db = mongo_client[config("MONGO_DB_FC")]
    collection = db[config("MONGO_FC_COLLECTION_LINKS")]

    # Stream new casts, and if a link is found, post to kiwistand
    for cast in client.stream_casts():
        if cast:
            current_cast = cast
            link = extract_link(current_cast.text)
            if link is None:
                continue
            
            # check if link is from urls to skip
            domains = ["kiwistand.com", "warpcast.com", "alphacaster.xyz"]
            if check_url_contains_domains(link, domains):
                continue
            
            # check if link has already been posted
            result = collection.find_one({"link": link})
            if result:
                continue

            # title = get_page_title(link)
            page_content = get_text_from_webpage(link)
            if page_content is None:
                continue

            # title = generate_webpage_title(page_content)
            # summary = generate_webpage_summary(page_content)
            title, summary = generate_webpage_title_and_summary(page_content)
            if title is None or summary is None:
                continue

            # remove any substrings from the title and summary
            substrings_to_remove = ["Title: ", "Summary: "]
            title = remove_substrings(title, substrings_to_remove)
            summary = remove_substrings(summary, substrings_to_remove)

            if title is None or title == "" or title == " " or title == "Access denied":
                continue

            # save the link to mongo
            collection.insert_one({"link": link})

            try:
                # truncate the entire cast to the max cast length (320 bytes)
                generated_cast = trim_generated_cast(title, current_cast.author.username, current_cast.hash, link, max_bytes=320, dev=dev)
            except Exception as e:
                logging.error(f"Failed trimming cast: {e}")
                error_reply(client, cast)

            # post the link to fc
            try:
                # Post links directly in the text, not as an attachment or embed
                # to ensure the link is visible in the cast received by the notification stream
                eatkiwi_cast = client.post_cast(generated_cast)

                # Post a reply to the cast with a trimmed summary (if needed)
                summary = trim_to_cast_max_bytes(summary)
                # client.post_cast(f"🥝 summary\n{summary}", parent=Parent(fid=eatkiwi_cast.author.fid, hash=eatkiwi_cast.hash))
                client.post_cast(summary, parent=Parent(fid=eatkiwi_cast.cast.author.fid, hash=eatkiwi_cast.cast.hash))

            except Exception as e:
                logging.error(f"Failed sending message: {e}")
                error_reply(client, cast)
