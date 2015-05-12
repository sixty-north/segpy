from itertools import zip_longest
import unittest
from hypothesis import given
from io import BytesIO
from hypothesis.specifiers import sampled_from
from segpy.binary_reel_header import BinaryReelHeader
from segpy.encoding import ASCII, EBCDIC
from segpy.header import are_equal

from segpy.toolkit import write_binary_reel_header, read_binary_reel_header, write_textual_reel_header, \
    read_textual_reel_header, CARDS_PER_HEADER, CARD_LENGTH
from test.strategies import header, multiline_ascii_encodable_text


class TestBinaryReelHeader(unittest.TestCase):

    @given(header(BinaryReelHeader),
           sampled_from(['<', '>']))
    def test_roundtrip(self, write_header, endian):
        with BytesIO() as write_stream:
            write_binary_reel_header(write_stream, write_header, endian)
            written_stream = write_stream.getvalue()

        with BytesIO(written_stream) as read_stream:
            read_header = read_binary_reel_header(read_stream, endian)

        self.assertTrue(are_equal(write_header, read_header))


class TestTextualReelHeader(unittest.TestCase):

    @given(multiline_ascii_encodable_text(0, CARDS_PER_HEADER),
           sampled_from([ASCII, EBCDIC]))
    def test_roundtrip(self, write_header_text, encoding):
        write_header_lines = write_header_text.splitlines()
        with BytesIO() as write_stream:
            write_textual_reel_header(write_stream, write_header_lines, encoding)
            written_stream = write_stream.getvalue()

        with BytesIO(written_stream) as read_stream:
            read_header_lines = read_textual_reel_header(read_stream, encoding)

        for written_line, read_line in zip_longest(write_header_lines[:CARDS_PER_HEADER],
                                                   read_header_lines,
                                                   fillvalue=""):
            self.assertEqual(written_line[:CARD_LENGTH].rstrip().ljust(CARD_LENGTH),
                             read_line)

    @given(multiline_ascii_encodable_text(0, CARDS_PER_HEADER),
           sampled_from([ASCII, EBCDIC]))
    def test_header_num_lines(self, write_header_text, encoding):
        write_header_lines = write_header_text.splitlines()
        with BytesIO() as write_stream:
            write_textual_reel_header(write_stream, write_header_lines, encoding)
            written_stream = write_stream.getvalue()

        with BytesIO(written_stream) as read_stream:
            read_header_lines = read_textual_reel_header(read_stream, encoding)

        self.assertEqual(len(read_header_lines), CARDS_PER_HEADER)

    @given(multiline_ascii_encodable_text(0, CARDS_PER_HEADER),
           sampled_from([ASCII, EBCDIC]))
    def test_header_line_length(self, write_header_text, encoding):
        write_header_lines = write_header_text.splitlines()
        with BytesIO() as write_stream:
            write_textual_reel_header(write_stream, write_header_lines, encoding)
            written_stream = write_stream.getvalue()

        with BytesIO(written_stream) as read_stream:
            read_header_lines = read_textual_reel_header(read_stream, encoding)

        self.assertTrue(all(len(line) == CARD_LENGTH for line in read_header_lines))