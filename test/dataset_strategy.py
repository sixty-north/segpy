from hypothesis.strategies import composite, integers, lists, sampled_from, text, tuples
from segpy.binary_reel_header import BinaryReelHeader
from segpy.dataset import Dataset
from segpy.toolkit import CARD_LENGTH, CARDS_PER_HEADER
from segpy.trace_header import TraceHeaderRev1

from .strategies import header, PRINTABLE_ASCII_ALPHABET


class InMemoryDataset(Dataset):
    def __init__(self,
                 dimensions,
                 textual_reel_header,
                 binary_reel_header,
                 extended_textual_header,
                 trace_headers,
                 trace_header_format=TraceHeaderRev1):
        """Args:
            dimensions: An iterable of 1, 2, or 3 dimension extents.
        """
        if trace_headers:
            assert isinstance(trace_headers[0], trace_header_format)

        if binary_reel_header.num_extended_textual_headers >= 0:
            assert binary_reel_header.num_extended_textual_headers == len(extended_textual_header)

        self._dimensions = tuple(dimensions)
        self._textual_reel_header = textual_reel_header
        self._binary_reel_header = binary_reel_header

        self._trace_headers = trace_headers
        self._trace_header_format = trace_header_format

        self._extended_textual_header = extended_textual_header

    @property
    def textual_reel_header(self):
        """The textual real header as an immutable sequence of forty Unicode strings each 80 characters long.
        """
        return self._textual_reel_header

    @property
    def binary_reel_header(self):
        """The binary reel header.
        """
        return self._binary_reel_header

    @property
    def extended_textual_header(self):
        return self._extended_textual_header

    @property
    def dimensionality(self):
        """The spatial dimensionality of the data: 3 for 3D seismic volumes, 2 for 2D seismic lines, 1 for a
        single trace_samples, otherwise 0.
        """
        return len(self._dimensions)

    def trace_indexes(self):
        """An iterator over zero-based trace_samples indexes.

        Returns:
            An iterator which yields integers in the range zero to
            num_traces - 1
        """
        return range(self.num_traces())

    def num_traces(self):
        """The number of traces."""
        # This is non-trivial! https://detectation.com/forum/viewtopic.php?t=3461
        return len(self._trace_headers)

    def trace_header(self, trace_index):
        """The trace header for a given trace index.

        Args:
            trace_index: An integer in the range zero to num_traces() - 1

        Returns:
            A TraceHeader corresponding to the requested trace_samples.
        """
        return self._trace_headers[trace_index]

    def trace_samples(self, trace_index, start=None, stop=None):
        """The trace samples for a given trace index.

        Args:
            trace_index: An integer in the range zero to num_traces - 1

            start: Optional zero-based start sample index. The default
                is to read from the first (i.e. zeroth) sample.

            stop: Optional zero-based stop sample index. Following Python
                slice convention this is one beyond the end.

        Returns:
            A sequence of numeric trace_samples samples.
        """
        hdr = self.trace_header(trace_index)
        start = 0 if start is None else start
        stop = hdr.num_samples if stop is None else stop
        return tuple(0 for _ in range(start, stop))


@composite
def textual_header_line(draw):
    return draw(text(alphabet=PRINTABLE_ASCII_ALPHABET,
                     min_size=CARD_LENGTH,
                     max_size=CARD_LENGTH))


@composite
def textual_reel_header(draw):
    return tuple(draw(lists(textual_header_line(),
                            min_size=CARDS_PER_HEADER,
                            max_size=CARDS_PER_HEADER)))


END_TEXT_STANZA = tuple(
    ['{:{width}}'.format('((SEG: EndText))', width=CARD_LENGTH)] + [' ' * CARD_LENGTH for _ in range(CARDS_PER_HEADER - 1)])


@composite
def stanza_header(draw):
    "Generate an extended textual header stanza header."

    alphabet = list(PRINTABLE_ASCII_ALPHABET)
    # Remove the separator character
    alphabet.remove(':')

    org = draw(text(alphabet=alphabet,
                    min_size=1,
                    max_size=(CARD_LENGTH - 6) // 2))

    name = draw(text(alphabet=alphabet,
                     min_size=1,
                     max_size=(CARD_LENGTH - 6) // 2))

    header = '(({}: {}))'.format(org, name)
    assert len(header) <= CARD_LENGTH

    header = '{:{width}}'.format(header, width=CARD_LENGTH)
    assert len(header) == CARD_LENGTH

    return header


@composite
def stanza_line(draw):
    "Generate an extended textual header stanze non-header line."

    alphabet = list(PRINTABLE_ASCII_ALPHABET)
    # Remove the separator character
    alphabet.remove('=')

    key = draw(text(alphabet=alphabet,
                    min_size=1,
                    max_size=(CARD_LENGTH - 3) // 2))

    value = draw(text(alphabet=alphabet,
                      min_size=1,
                      max_size=(CARD_LENGTH - 3) // 2))

    line = '{} = {}'.format(key, value)
    assert len(line) <= CARD_LENGTH

    line = '{:{width}}'.format(line, width=CARD_LENGTH)
    assert len(line) == CARD_LENGTH

    return line


@composite
def stanza(draw):
    "Generate an extended textual header stanza."
    count = draw(integers(min_value=0, max_value=CARDS_PER_HEADER - 1))
    header = draw(stanza_header())
    lines = [draw(stanza_line()) for _ in range(count)]
    empty_lines = [' ' * CARD_LENGTH for _ in range(CARDS_PER_HEADER - 1 - count)]
    full_stanza = [header] + lines + empty_lines
    assert len(full_stanza) == CARDS_PER_HEADER
    return tuple(full_stanza)


@composite
def extended_textual_header(draw, count):
    if count == -1:
        count = draw(integers(min_value=0, max_value=10))
        headers = draw(lists(stanza(),
                             min_size=count,
                             max_size=count))
        headers.append(END_TEXT_STANZA)
        return headers

    # TODO: This can *optionally* have an end-stanza. We should generate those sometimes.
    return draw(lists(stanza(),
                      min_size=count,
                      max_size=count))


@composite
def dataset(draw, dims):
    dims = draw(lists(integers(min_value=0, max_value=10),
                      min_size=dims,
                      max_size=dims))
    text_header = draw(textual_reel_header())
    binary_header = draw(header(BinaryReelHeader))
    ext_text_headers = draw(extended_textual_header(binary_header.num_extended_textual_headers))

    # TODO: We need to look at making sure `sample_interval` is set
    # appropriately/consistently. See the docstring for
    # TraceHeader.sample_interval for more information.
    trace_headers = draw(lists(header(TraceHeaderRev1),
                               min_size=0,
                               max_size=100))

    return InMemoryDataset(dims,
                           text_header,
                           binary_header,
                           ext_text_headers,
                           trace_headers)
