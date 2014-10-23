import itertools
import time
import os

from portability import izip


def pairwise(iterable):
    """Pairwise iteration.

    Args:
        iterable: An iterable series.

    Returns:
        An iterator over 2-tuples.
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return izip(a, b)


def batched(iterable, batch_size):
    """
    """
    pending = []
    batch = pending

    for item in iterable:
        pending.append(item)
        if len(pending) == batch_size:
            batch = pending
            pending = []
            yield batch

    if len(pending) > 0:
        yield batch


def pad(iterable, padding=None, size=None):
    if size is None:
        return itertools.chain(iterable, itertools.repeat(padding))
    return itertools.islice(pad(iterable, padding), size)


def contains_duplicates(sorted_iterable):
    """Determine in an iterable series contains duplicates.

    Args:
        sorted_iterable: Any iterable series which must be sorted in either
            ascending or descending order.

    Returns:
        True if sorted_iterable contains duplicates, otherwise False.
    """
    for a, b in pairwise(sorted_iterable):
        if a == b:
            return True
    return False


def measure_stride(iterable):
    """Determine whether successive numeric items differ by a constant amount.

    Args:
        iterable: An iterable series of numeric values.

    Returns:
        The difference between successive values (e.g. item[1] - item[0]) if
        that difference is the same between all successive pairs, otherwise
        None.
    """
    stride = None
    for a, b in pairwise(iterable):
        new_stride = b - a
        if stride is None:
            stride = new_stride
        elif stride != new_stride:
            return None
    return stride

def minmax(iterable):
    """Return the minimum and maximum of an iterable series.

    This function requires only a single pass over the data.

    Args:
        iterable: An iterable series for which to determine the minimum and
            maximum values.

    Returns:
        A 2-tuple containing the minimum and maximum values.
    """
    iterator = iter(iterable)
    try:
        first = next(iterator)
    except StopIteration:
        raise ValueError("minmax() arg is an empty iterable series")
    minimum = first
    maximum = first
    for item in iterator:
        minimum = min(minimum, item)
        maximum = max(maximum, item)
    return minimum, maximum


def file_length(fh):
    """Determine the length of a file-like object in bytes.

    Args:
        fh: A seekable file-like-object.

    Returns:
        An integer length in bytes.
    """
    pos = fh.tell()
    try:
        fh.seek(0, os.SEEK_END)
        return fh.tell()
    finally:
        fh.seek(pos, os.SEEK_SET)


def filename_from_handle(fh):
    """Determine the name of the file underlying a file-like object.

    Args:
        fh: A file-like object.

    Returns:
        A string containing the file name, or '<unknown>' if it could not
        be determined.
    """
    try:
        return fh.name
    except AttributeError:
        return '<unknown>'


def now_millis():
    millis = int(round(time.time() * 1000))
    return millis


def round_up(integer, multiple):
    """Round up to the nearest multiple"""
    return integer if integer % multiple == 0 else integer + multiple - integer % multiple