COMMON = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:_- '
EBCDIC = set(COMMON.encode('cp037'))
ASCII = set(COMMON.encode('ascii'))

def guess_encoding(bs, threshold=0.5):
    """Try to determine whether the encoding of byte stream b is an ASCII string or an EBCDIC string.

    Args:
        bs: A byte string (Python 2 - str; Python 3 - bytes)

    Returns:
        A string which can be used with the Python encoding functions: 'cp037' for EBCDIC, 'ascii' for ASCII or None
        if neither.
    """

    ebcdic_count = 0
    ascii_count = 0

    count = 0
    for b in bs:
        if b in EBCDIC:
            ebcdic_count +=1
        if b in ASCII:
            ascii_count +=1
        count += 1

    if count == 0:
        return None

    ebcdic_freq = ebcdic_count / count
    ascii_freq = ascii_count / count

    if ebcdic_freq < threshold and ascii_freq < threshold:
        return None

    if ebcdic_freq < threshold and ascii_freq >= threshold:
        return 'ascii'

    if ebcdic_freq >= threshold and ascii_freq < threshold:
        return 'cp037'

    return None
