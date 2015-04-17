from hypothesis import strategy
from hypothesis.specifiers import integers_in_range

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

    return strategy(integers_in_range(0, 10))                                      \
           .flatmap(lambda n: ([integers_in_range(*PRINTABLE_ASCII_RANGE)],) * n)  \
           .map(lambda xs: '\n'.join(bytes(x).decode('ascii') for x in xs))
