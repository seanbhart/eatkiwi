
def remove_substrings(s, substrings):
    """
    Removes all occurrences of the substrings in the input string s.
    """
    for substring in substrings:
        s = s.replace(substring, "")
    return s

def reduce_word_count(text, max_words=350):
    # Split the text into words
    words = text.split()

    # If the text has max_words or less, return the original text
    if len(words) <= max_words:
        return text

    # Otherwise, truncate the text to max_words and add an ellipsis
    reduced_words = words[:max_words]
    reduced_text = " ".join(reduced_words)
    reduced_text += "..."
    return reduced_text

def truncate_string_by_bytes(s, byte_limit):
    encoded = s.encode('utf-8')
    while len(encoded) > byte_limit:
        s = s[:-1]
        encoded = s.encode('utf-8')
    return s

def trim_to_cast_max_bytes(s):
    return truncate_string_by_bytes(s, 320)

def truncate_string_by_character(s, max_characters=80):
    return (s[:77] + '...') if len(s) > max_characters else s

# The dev version doesn't include the warpcast link
# to prevent annoying notifications for authors
def trim_generated_cast(title, author_username, hash, link, max_bytes=320, dev=False):
    base_string = f"Posted by @{author_username}\n\n\"\n{link}\nhttps://warpcast.com/{author_username}/{hash}"
    base_bytes = len(base_string.encode('utf-8'))
    ellipsis_bytes = len("...".encode('utf-8'))
    title_bytes = len(title.encode('utf-8'))

    if (base_bytes + title_bytes) <= max_bytes:
        return f'Posted by @{author_username}\n\n"{title}"\n{link}'
        # return f'Posted by @{author_username}\n\n"{title}"\n{link}\nhttps://warpcast.com/{author_username}/{hash}'
    else:
        max_title_bytes = max_bytes - base_bytes - ellipsis_bytes
        if max_title_bytes < 1:
            raise ValueError("Base string exceeds max bytes, cannot include any title text.")

        # Truncate title at character boundary
        truncated_title = title.encode('utf-8')[:max_title_bytes].decode('utf-8', 'ignore')
        
        return f'Posted by @{author_username}\n\n"{truncated_title}..."\n{link}'
        # return f'Posted by @{author_username}\n\n"{truncated_title}..."\n{link}\nhttps://warpcast.com/{author_username}/{hash}'
