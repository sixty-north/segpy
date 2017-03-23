from hypothesis import given
from hypothesis.strategies import sampled_from, just, booleans

from segpy.encoding import EBCDIC, ASCII
from segpy.toolkit import format_extended_textual_header, CARDS_PER_HEADER, END_TEXT_STANZA, CARD_LENGTH
from test.strategies import multiline_ascii_encodable_text


class TestFormatExtendedTextualHeader:

    @given(multiline_ascii_encodable_text(0, 100),
           sampled_from([ASCII, EBCDIC]),
           booleans())
    def test_forty_lines_per_page(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        assert all(len(page) == CARDS_PER_HEADER for page in pages)

    @given(multiline_ascii_encodable_text(0, 100),
           sampled_from([ASCII, EBCDIC]),
           booleans())
    def test_eighty_bytes_per_encoded_line(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        assert all([len(line.encode(encoding)) == CARD_LENGTH for page in pages for line in page])

    @given(multiline_ascii_encodable_text(0, 100),
           sampled_from([ASCII, EBCDIC]),
           booleans())
    def test_lines_end_with_cr_lf(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        assert all([line.endswith('\r\n') for page in pages for line in page])

    @given(multiline_ascii_encodable_text(0, 100),
           sampled_from([ASCII, EBCDIC]),
           just(True))
    def test_end_text_stanza_present(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        assert pages[-1][0].startswith(END_TEXT_STANZA)
