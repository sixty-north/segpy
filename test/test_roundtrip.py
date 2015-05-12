import unittest
from hypothesis import given
from io import BytesIO
from hypothesis.specifiers import sampled_from
from segpy.binary_reel_header import BinaryReelHeader
from segpy.header import are_equal

from segpy.toolkit import write_binary_reel_header, read_binary_reel_header
from test.strategies import header


class TestBinaryReelHeader(unittest.TestCase):

    @given(header(BinaryReelHeader),
           sampled_from(['<', '>']))
    def test_roundtrip(self, write_header, endian):
        with BytesIO() as write_stream:
            write_binary_reel_header(write_stream, write_header, endian)
            written_steam = write_stream.getvalue()

        with BytesIO(written_steam) as read_stream:
            read_header = read_binary_reel_header(read_stream, endian)

        self.assertTrue(are_equal(write_header, read_header))
