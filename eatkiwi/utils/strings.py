import sys

def truncate_string_by_bytes(s, byte_limit):
    encoded = s.encode('utf-8')
    while len(encoded) > byte_limit:
        s = s[:-1]
        encoded = s.encode('utf-8')
    return s

def trim_to_cast(s):
    return truncate_string_by_bytes(s, 320)

def truncate_string_by_character(s, max_length=80):
    return (s[:77] + '...') if len(s) > max_length else s

# The dev version doesn't include the warpcast link
# to prevent annoying notifications for authors
def trim_generated_cast(title, author_username, hash, link, max_bytes=320, dev=False):
    base_string = f"Posted by @{author_username}\n\n\"\n{link}\nhttps://warpcast.com/{author_username}/{hash}"
    base_bytes = len(base_string.encode('utf-8'))
    ellipsis_bytes = len("...".encode('utf-8'))
    title_bytes = len(title.encode('utf-8'))

    if (base_bytes + title_bytes) <= max_bytes:
        if dev:
            return f'Posted by @{author_username}\n\n"{title}"\n{link}'
        return f'Posted by @{author_username}\n\n"{title}"\n{link}\nhttps://warpcast.com/{author_username}/{hash}'
    else:
        max_title_bytes = max_bytes - base_bytes - ellipsis_bytes
        if max_title_bytes < 1:
            raise ValueError("Base string exceeds max bytes, cannot include any title text.")

        # Truncate title at character boundary
        truncated_title = title.encode('utf-8')[:max_title_bytes].decode('utf-8', 'ignore')
        
        if dev:
            return f'Posted by @{author_username}\n\n"{truncated_title}..."\n{link}'
        return f'Posted by @{author_username}\n\n"{truncated_title}..."\n{link}\nhttps://warpcast.com/{author_username}/{hash}'
