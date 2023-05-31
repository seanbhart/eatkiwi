
def cut_off_string(s, byte_limit):
    encoded = s.encode('utf-8')
    while len(encoded) > byte_limit:
        s = s[:-1]
        encoded = s.encode('utf-8')
    return s