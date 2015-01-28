import os
import sys

EMPTY_BYTE_STRING = b'' if sys.version_info >= (3, 0) else ''


def seekable(fh):
    """Determine whether a file-like object supports seeking.

    Args:
        fh: The file-like-object to be tested.

    Returns:
        True if the file supports seeking, otherwise False.
    """
    try:
        return fh.seekable()
    except AttributeError:
        try:
            pos = fh.tell()
            try:
                fh.seek(0, os.SEEK_END)
            finally:
                fh.seek(pos)
        except AttributeError:
            return False
    return True


if sys.version_info >= (3, 0):
    long_int = int
else:
    long_int = long


if sys.version_info >= (3, 0):
    def byte_string(integers):
        return bytes(integers)
else:
    def byte_string(integers):
        return ''.join(chr(i) for i in integers)


if sys.version_info >= (3, 0):
    import reprlib
    reprlib = reprlib  # Keep the static analyzer happy
else:
    import repr as reprlib

if sys.version_info >= (3, 0):
    izip = zip
else:
    from itertools import izip
    izip = izip    # Keep the static analyzer happy


if sys.version_info >= (3, 0):
    def four_bytes(byte_str):
        a, b, c, d = byte_str[:4]
        return a, b, c, d
else:
    def four_bytes(byte_str):
        a = ord(byte_str[0])
        b = ord(byte_str[1])
        c = ord(byte_str[2])
        d = ord(byte_str[3])
        return a, b, c, d
