from pytest import raises

from segpy.encoding import UnsupportedEncodingError
from segpy.writer import write_segy


def test_write_segy_with_non_callable_progress_callback_raises_type_error():
    with raises(TypeError):
        write_segy(None, None, progress=42)


def test_write_segy_with_unsupported_encoding_raises_unsupported_encoding_error():
    with raises(UnsupportedEncodingError):
        write_segy(None, None, encoding='latin1')
