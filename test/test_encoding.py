from segpy.encoding import (UnsupportedEncodingError, guess_encoding,
                            COMMON_ASCII_CHARS, COMMON_EBCDIC_CHARS,
                            ASCII, EBCDIC)
from test.predicates import check_balanced


class TestUnsupportedEncodingError:

    def test_encoding(self):
        e = UnsupportedEncodingError("abcdef", 'latin4')
        assert e.encoding == 'latin4'

    def test_str(self):
        e = UnsupportedEncodingError("abcdef", 'latin5')
        s = str(e)
        assert 'abcdef' in s
        assert 'latin5' in s

    def test_repr(self):
        e = UnsupportedEncodingError("abcdef", 'latin5')
        r = repr(e)
        assert 'abcdef' in r
        assert 'latin5' in r
        assert check_balanced(r)


class TestGuessEncoding:

    def test_guess_encoding_ascii(self):
        assert guess_encoding(bytes(COMMON_ASCII_CHARS)) == ASCII

    def test_guess_encoding_ebcdic(self):
        assert guess_encoding(bytes(COMMON_EBCDIC_CHARS)) == EBCDIC

    def test_guess_encoding_empty_is_none(self):
        assert guess_encoding(b'') is None

    def test_guess_encoding_all_null_is_ascii(self):
        assert guess_encoding(bytes(5)) == ASCII

    def test_guess_encoding_mostly_ascii(self):
        assert guess_encoding(bytes(COMMON_ASCII_CHARS) + bytes(COMMON_ASCII_CHARS) + bytes(COMMON_EBCDIC_CHARS)) == ASCII

    def test_guess_encoding_mostly_ebcdic(self):
        assert guess_encoding(bytes(COMMON_ASCII_CHARS) + bytes(COMMON_EBCDIC_CHARS) + bytes(COMMON_EBCDIC_CHARS)) == EBCDIC

    def test_guess_encoding_inconclusive(self):
        assert guess_encoding(bytes(COMMON_ASCII_CHARS) + bytes(5) + bytes(COMMON_EBCDIC_CHARS)) == None

