import hashlib
import operator
import time
import os
import sys
import math
import fractions

from contextlib import contextmanager
from enum import Enum
from itertools import (islice, cycle, tee, chain, repeat, groupby)

from segpy.reversed_sequence_view import ReversedSequenceView
from segpy.sorted_frozen_set import SortedFrozenSet

UNKNOWN_FILENAME = '<unknown>'

NATIVE_ENDIANNESS = '<' if sys.byteorder == 'little' else '>'

EMPTY_BYTE_STRING = b''

UNSET = object()


def pairwise(iterable):
    a, b = tee(iterable)
    next(b)
    yield from zip(a, b)


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
    return _batched(batch_size, iterable, padding)


def _batched(batch_size, iterable, padding):
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
        return chain(iterable, repeat(padding))
    return islice(pad(iterable, padding), size)


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

    return _complementary_intervals(intervals, start, stop)


def _complementary_intervals(intervals, start, stop):
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


def intervals_are_contiguous(intervals):
    """Determine whether a series of intervals are contiguous.

    Args:
        intervals: An iterable series of intervals where each interval is either
            a range or slice object.

    Returns:
        True if the intervals are in order, contiguous and non-overlapping,
        otherwise False.
    """

    for a, b in pairwise(intervals):
        if a.stop != b.start:
            return False
    return True


def intervals_partially_overlap(interval_a, interval_b):
    """Determine whether two intervals partially overlap.

    Args:
        interval_a: A range or slice object.
        interval_b: A range or slice object.

    Returns:
        True if interval_a partially overlaps interval_b, otherwise False if the intervals
        are either disjoint or exactly coincident.
    """
    if interval_a == interval_b:
        return False

    if interval_a.start <= interval_b.start:
        first_interval = interval_a
        second_interval = interval_b
    else:
        first_interval = interval_b
        second_interval = interval_a

    return second_interval.start < first_interval.stop


def roundrobin(*iterables):
    """Take items from each iterable in turn until all iterables are exhausted.

    roundrobin('ABC', 'D', 'EF') --> A D E B F C
    """
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for n in nexts:
                yield n()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))


def contains_duplicates(sorted_iterable):
    """Determine if an iterable series contains duplicates.

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
    if isinstance(iterable, range):
        return iterable.step

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
        A string containing the file name, or UNKNOWN_FILENAME if it could not
        be determined.
    """
    try:
        return fh.name
    except AttributeError:
        return UNKNOWN_FILENAME


def now_millis():
    millis = int(round(time.time() * 1000))
    return millis


def round_up(integer, multiple):
    """Round up to the nearest multiple"""
    if multiple <= 0:
        raise ValueError("Can not round up to non-positive multiple {}".format(multiple))
    return integer if integer % multiple == 0 else integer + multiple - integer % multiple


def underscores_to_camelcase(s):
    """Convert text_in_this_style to TextInThisStyle."""
    return ''.join(w.capitalize() for w in s.split('_'))


def first_sentence(s):
    sentence, stop, _ = s.partition('.')
    return sentence + stop


def lower_first(s):
    """Lower case the first character of a string."""
    return s[:1].lower() + s[1:]


def almost_equal(x, y, epsilon=sys.float_info.epsilon):
    max_xy_one = max(1.0, abs(x), abs(y))
    e = epsilon * max_xy_one
    delta = abs(x - y)
    return delta <= e


def is_magic_name(name):
    return len(name) > 4 and name.startswith('__') and name.endswith('__')


def super_class(cls):
    """Return the next class in the MRO of cls, or object."""
    mro = cls.__mro__
    assert len(mro) > 0
    if len(mro) == 1:
        assert mro[0] is object
        return object
    return mro[1]


def four_bytes(byte_str):
    a, b, c, d = byte_str[:4]
    return a, b, c, d


def is_sorted(iterable, key=None, reverse=False, distinct=False):
    if key is None:
        key = identity
    if reverse:
        if distinct:
            if isinstance(iterable, range) and iterable.step < 0:
                return True
            op = operator.gt
        else:
            op = operator.ge
    else:
        if distinct:
            if isinstance(iterable, range) and iterable.step > 0:
                return True
            if isinstance(iterable, SortedFrozenSet):
                return True
            op = operator.lt
        else:
            op = operator.le
    return all(op(a, b) for a, b in pairwise(map(key, iterable)))


def single_item_range(item):
    """Construct a range object which generates a single value.
    """
    return range(item, item + 1)


class SortSense(Enum):
    ascending = 0
    descending = 1


def make_sorted_distinct_sequence(iterable, sense=SortSense.ascending):
    """Create a sorted immutable sequence from an iterable series.

    The resulting collected will be sorted ascending.

    Args:
        iterable: An iterable series of comparable values.

        sense: If None, the any original sense of the data is preserved,
            so ascending data remains ascending, and descending data
            remains descending. If the original data was unsorted,
            the result will be ascending. Force a particular sense
            by specifying SortSense.ascending or SortSense.descending.

    Returns:
        An immutable collection which supports the Sized, Iterable,
        Container and Sequence protocols.
    """
    if isinstance(iterable, range):
        if sense is None:
            return iterable
        elif sense == SortSense.ascending:
            if iterable.step > 0:
                return iterable
            else:
                return reversed_range(iterable)
        elif sense == SortSense.descending:
            if iterable.step < 0:
                return iterable
            else:
                return reversed_range(iterable)
        else:
            raise TypeError("sense {} is neither a SortSense nor None".format(sense))

    if sense == SortSense.ascending:
        sorted_seq = SortedFrozenSet(iterable)
    elif sense == SortSense.descending:
        sorted_seq = ReversedSequenceView(SortedFrozenSet(iterable))
    elif sense is None:
        items = list(iterable)
        if is_sorted(items, reverse=True, distinct=True):
            sorted_seq = ReversedSequenceView(SortedFrozenSet(iterable))
        else:
            sorted_seq = SortedFrozenSet(iterable)
    else:
        raise TypeError("sense {} is neither a SortSense nor None".format(sense))

    return compress_sorted_sequence_to_range(sorted_seq)


def reversed_range(r):
    """Given a range object produce the reversed range.

    Args:
        r: A range object.

    Returns:
        The reversed range.
    """
    q, remainder = divmod(r.stop - r.start, r.step)
    num_steps = q - (remainder == 0)
    s_start = r.start + num_steps * r.step
    s_step = -r.step
    s_stop = s_start + num_steps * s_step + (s_step + remainder)
    return range(s_start, s_stop, s_step)


def compress_sorted_sequence_to_range(sorted_sequence):
    """Attempt to represent the supplied sequence as a range.

    Useful for reducing the size of large stored integer sequences.

    Args:
        sorted_sequence: A sequence of integers which may be
            ordered in an ascending or descending sense.

    Returns:
        An ordered sequence which may be a range or may be
        the unaltered argument.
    """
    if len(sorted_sequence) == 1:
        return single_item_range(sorted_sequence[0])
    stride = measure_stride(sorted_sequence)
    if stride is not None:
        start = sorted_sequence[0]
        stop = sorted_sequence[-1] + stride
        return range(start, stop, stride)
    return sorted_sequence


def hash_for_file(fh, *args):
    """Compute the SHA1 hash for file combined with any stringified additional args.

    The resulting hash is based on both the contents and length of the supplied file-
    like object.

    Args:
        fh: A file-like object opened in binary mode.

        *args: The stringified values of ny additional arguments with be combined
            with the file data used to compute the hash.

    Returns:
        A string containing the hexadecimal digest.
    """
    # TODO: Use decorator to reset file pointer
    block_size=512*128
    sha1 = hashlib.sha1()
    fh.seek(0)
    for chunk in iter(lambda: fh.read(block_size), EMPTY_BYTE_STRING):
        sha1.update(chunk)
    length = fh.tell()
    length_as_bytes = length.to_bytes((length.bit_length() // 8) + 1, byteorder='little')
    sha1.update(length_as_bytes)
    fh.seek(0)
    for arg in args:
        encoded_arg = repr(arg).encode('utf8')
        sha1.update(encoded_arg)
    digest = sha1.hexdigest()
    return digest


def first(iterable):
    i = iter(iterable)
    try:
        return next(i)
    except StopIteration:
        raise ValueError("Cannot return the first item from an empty iterable.")


def last(iterable):
    try:
        # Don't rely on support for negative indexing
        return iterable[len(iterable) - 1]
    except (TypeError, IndexError):
        i = iter(iterable)
        try:
            item = next(i)
        except StopIteration:
            raise ValueError("Cannot return the last item from an empty iterable")
        for item in i:
            pass
        return item


def identity(x):
    return x


def collect_attributes(derived_class, base_class, predicate):
    """

    Args:
        derived_class: The class at which to start searching.
        base_class: The class at which to stop searching
        predicate: A predicate which accepts a name and value for each attribute.

    Returns:
        A generator of items containing the (class, attribute_name)
    """
    for cls in derived_class.__mro__:
        for key, value in vars(cls).items():
            if predicate(key, value):
                yield cls, key, value
        if cls is base_class:
            break


@contextmanager
def restored_position_seek(fh, pos):
    original = fh.tell()
    fh.seek(pos)
    yield
    fh.seek(original)


def cmp(x, y):
    """Compare the two objects x and y and return an integer according to the outcome.

    Args:
        x: The first number to compare.
        y: The second number to compare.

    Returns:
        A negative value if x < y, zero if x == y and  positive if x > y.
    """
    return (x > y) - (x < y)


def sgn(x):
    """The sign of a number.

    Args:
        x: The number for which to compute the sign.

    Returns:
        +1 is x is positive, -1 if x is negative, 0 if x is zero.
    """
    return cmp(x, 0)


def all_equal(iterable):
    "Returns True if all the elements are equal to each other"
    g = groupby(iterable)
    return next(g, True) and not next(g, False)
