"""
This module provides utility functions for working with strings.

Functions:
- remove_substrings(s, substrings): Removes all occurrences of the substrings in the input string s.
- reduce_word_count(text, max_words=350): Truncates the input text to a maximum number of words, adding an ellipsis if necessary.
- truncate_string_by_bytes(s, byte_limit): Truncates the input string to a maximum number of bytes.
- trim_to_cast_max_bytes(s): Truncates the input string to a maximum number of bytes, specifically for use in a "cast" title.
- truncate_string_by_character(s, max_characters=80): Truncates the input string to a maximum number of characters, adding an ellipsis if necessary.
- trim_generated_cast(title, author_username, hash, link, max_bytes=320, dev=False): Truncates the input title and link to a maximum number of bytes, specifically for use in a "cast" post.

"""


def remove_substrings(s, substrings) -> str:
    """
    Removes all occurrences of the substrings in the input string s.

    Args:
        s (str): The input string to remove substrings from.
        substrings (List[str]): A list of substrings to remove from the input string.

    Returns:
        str: The input string with all occurrences of the substrings removed.

    """
    for substring in substrings:
        s = s.replace(substring, "")
    return s


def reduce_word_count(text, max_words=350) -> str:
    """
    Truncates the input text to a maximum number of words, adding an ellipsis if necessary.

    Args:
        text (str): The input text to truncate.
        max_words (int, optional): The maximum number of words to allow in the truncated text. Defaults to 350.

    Returns:
        str: The truncated text, with an ellipsis added if necessary.

    """
    words = text.split()
    if len(words) <= max_words:
        return text

    # The text is too long - truncate the text to max_words and add an ellipsis
    reduced_words = words[:max_words]
    reduced_text = " ".join(reduced_words)
    reduced_text += "..."
    return reduced_text

def truncate_string_by_bytes(s, byte_limit) -> str:
    """
    Truncates the input string to a maximum number of bytes.

    Args:
        s (str): The input string to truncate.
        byte_limit (int): The maximum number of bytes to allow in the truncated string.

    Returns:
        str: The truncated string.

    """
    encoded = s.encode('utf-8')
    while len(encoded) > byte_limit:
        s = s[:-1]
        encoded = s.encode('utf-8')
    return s


def trim_to_cast_max_bytes(s) -> str:
    """
    Truncates the input string to a maximum number of bytes, specifically for use in a "cast" title.

    Args:
        s (str): The input string to truncate.

    Returns:
        str: The truncated string.

    """
    return truncate_string_by_bytes(s, 320)


def truncate_string_by_character(s, max_characters=80) -> str:
    """
    Truncates the input string to a maximum number of characters, adding an ellipsis if necessary.

    Args:
        s (str): The input string to truncate.
        max_characters (int, optional): The maximum number of characters to allow in the truncated string. Defaults to 80.

    Returns:
        str: The truncated string, with an ellipsis added if necessary.

    """
    return (s[:77] + '...') if len(s) > max_characters else s


def trim_generated_cast_text(title, author_username, hash, link, max_bytes=320, dev=False) -> str:
    """
    Truncates the input title and link to a maximum number of bytes, specifically for use in a "cast" post.

    Args:
        title (str): The input title to truncate.
        author_username (str): The username of the author of the "cast" post.
        hash (str): A unique identifier for the "cast" post.
        link (str): The URL of the original content being shared.
        max_bytes (int, optional): The maximum number of bytes to allow in the truncated title and link. Defaults to 320.
        dev (bool, optional): A boolean flag indicating whether the function is being called in a development environment. Defaults to False.

    Returns:
        Tuple[str, str]: A tuple containing the truncated title and link, respectively.

    """
    base_string = f"Posted by @{author_username}\n\n\"\n{link}\nhttps://warpcast.com/{author_username}/{hash}"
    base_bytes = len(base_string.encode('utf-8'))
    ellipsis_bytes = len("...".encode('utf-8'))
    title_bytes = len(title.encode('utf-8'))

    # The dev version doesn't include the warpcast link to prevent annoying notifications for authors
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
