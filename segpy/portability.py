import os
import sys

EMPTY_BYTE_STRING = b'' if sys.version_info >= (3, 0) else ''


if sys.version_info >= (3, 0):
    unicode = str
else:
    unicode = unicode




