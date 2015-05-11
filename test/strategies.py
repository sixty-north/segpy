from itertools import accumulate, starmap
from hypothesis import strategy
from hypothesis.specifiers import integers_in_range, just
from segpy.trace_header import TraceHeaderRev0
from segpy.util import batched

PRINTABLE_ASCII_RANGE = (32, 127)


def multiline_ascii_encodable_text(min_num_lines, max_num_lines):
    """A Hypothesis strategy to produce a multiline Unicode string.

    Args:
        min_num_lines: The minimum number of lines in the produced strings.
        max_num_lines: The maximum number of lines in the produced strings.

    Returns:
        A strategy for generating Unicode strings containing only newlines
        and characters which are encodable as printable 7-bit ASCII characters.
    """

    return strategy(integers_in_range(min_num_lines, max_num_lines))               \
           .flatmap(lambda n: ([integers_in_range(*PRINTABLE_ASCII_RANGE)],) * n)  \
           .map(lambda xs: '\n'.join(bytes(x).decode('ascii') for x in xs))


def spaced_ranges(min_num_ranges, max_num_ranges, min_interval, max_interval):
    """A Hypothesis strategy to produce separated, non-overlapping ranges.

    Args:
        min_num_ranges: The minimum number of ranges to produce. TODO: Correct?
        max_num_ranges: The maximum number of ranges to produce.
        min_interval: The minimum interval used for the lengths of the alternating ranges and spaces.
        max_interval: The maximum interval used for the lengths of the alternating ranges and spaces.
    """
    return strategy(integers_in_range(min_num_ranges, max_num_ranges))               \
           .map(lambda n: 2*n)                                                       \
           .flatmap(lambda n: (integers_in_range(min_interval, max_interval),) * n)  \
           .map(list).map(lambda lst: list(accumulate(lst)))                         \
           .map(lambda lst: list(batched(lst, 2)))                                   \
           .map(lambda pairs: list(starmap(range, pairs)))


def header(header_class, **kwargs):
    """Create a strategy for producing headers of a specific class.

    Args:
        header_class: The type of header to be produced. This class will be
            introspected to determine suitable strategies for each named
            field.

        **kwargs: Any supplied keyword arguments can be used to fix the value
            of particular header fields.
    """

    field_strategies = {}
    for field_name in header_class.ordered_field_names():
        if field_name in kwargs:
            field_strategy = just(kwargs.pop(field_name))
        else:
            value_type = getattr(header_class, field_name).value_type
            field_strategy = integers_in_range(value_type.MINIMUM, value_type.MAXIMUM)
        field_strategies[field_name] = field_strategy

    if len(kwargs) > 0:
        raise TypeError("Unrecognised binary header field names {} for {}".format(
            ', '.join(kwargs.keys()),
            header_class.__name__))

    return strategy(field_strategies).map(lambda kw: header_class(**kw))
