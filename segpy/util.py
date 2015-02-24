import itertools
import time
import os
import sys

from segpy.portability import izip

NATIVE_ENDIANNESS = '<' if sys.byteorder == 'little' else '>'

UNSET = object()

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


def batched(iterable, batch_size, padding=UNSET):
    """Batch an iterable series into equal sized batches.

    Args:
        iterable: The series to be batched.

        batch_size: The size of the batch. Must be at least one.

        padding: Optional value used to pad the final batch to batch_size. If
            omitted, the final batch may be smaller than batch_size.

    Yields:
        A series of lists, each containing batch_size items from iterable.

    Raises:
        ValueError: If batch_size is less than one.
    """
    if batch_size < 1:
        raise ValueError("Batch size {} is not at least one.".format(batch_size))

    pending = []

    for item in iterable:
        pending.append(item)
        if len(pending) == batch_size:
            batch = pending
            pending = []
            yield batch

    num_left_over = len(pending)
    if num_left_over > 0:
        if padding is not UNSET:
            pending.extend([padding] * (batch_size - num_left_over))
        yield pending


def pad(iterable, padding=None, size=None):
    if size is None:
        return itertools.chain(iterable, itertools.repeat(padding))
    return itertools.islice(pad(iterable, padding), size)


def complementary_intervals(intervals, start=None, stop=None):
    """Compute a complementary set of intervals which alternate with given intervals to form a contiguous range.

    Given,

        Start                          Stop
           [-----)    [-----) [----)

    produces,

        [--)     [----)     [-)    [---)

    Args:
        intervals: An sequence of at least one existing slices or ranges. The type of the first interval (slice or
            range) is used as the result type.
        start: An optional start index, defaults to the start of the first slice.
        stop: An optional one-beyond-the-end index, defaults to the stop attribute of the last slice.

    Yields:
        A complementary series of slices which alternate with the supplied slices.  The number of returned
        slices will always be len(slices) + 1 since both leading and trailing slices will always be returned.
        Note the some of the returned slices may be 'empty' (having zero length).
    """
    if len(intervals) < 1:
        raise ValueError("intervals must contain at least one interval (slice or range) object")

    interval_type = type(intervals[0])

    if start is None:
        start = intervals[0].start

    if stop is None:
        stop = intervals[-1].stop

    index = start
    for s in intervals:
        yield interval_type(index, s.start)
        index = s.stop

    yield interval_type(index, stop)


def roundrobin(*iterables):
    """Take items from each iterable in turn until all iterables are exhausted.

    roundrobin('ABC', 'D', 'EF') --> A D E B F C
    """
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for n in nexts:
                yield n()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))


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


def underscores_to_camelcase(s):
    """Convert text_in_this_style to TextInThisStyle."""
    return ''.join(w.capitalize() for w in s.split('_'))