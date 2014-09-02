import os


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