"""Tests for segpy.reader.
"""

import io

from hypothesis import assume, given
import hypothesis.strategies as ST
import pytest
from segpy.reader import create_reader
from segpy.toolkit import REEL_HEADER_NUM_BYTES


@pytest.fixture
def min_reader_data():
    "Binary data of minimal size to satisfy `create_reader`."
    return io.BytesIO(b'0' * REEL_HEADER_NUM_BYTES)


class Test_create_reader_Exceptions:
    """Tests for exceptions that `create_reader` can throw.
    """
    def test_type_error_on_non_binary_handle(self):
        handle = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        with pytest.raises(TypeError):
            create_reader(handle)

    def test_type_error_on_non_seekable_handle(self):
        with pytest.raises(TypeError):
            create_reader(io.RawIOBase())

    def test_value_error_on_closed_handle(self):
        handle = io.BytesIO()
        handle.close()
        with pytest.raises(ValueError):
            create_reader(handle)

    def test_value_error_on_short_file(self):
        handle = io.BytesIO(b'')
        with pytest.raises(ValueError):
            create_reader(handle)

    @given(endian=ST.text())
    def test_value_error_on_invalid_endian(self, endian, min_reader_data):
        assume(endian not in ('<', '>'))
        with pytest.raises(ValueError):
            create_reader(min_reader_data,
                          endian=endian)

    def test_type_error_if_progress_callback_not_callable(self, min_reader_data):
        with pytest.raises(TypeError):
            create_reader(min_reader_data,
                          progress='not callable')

    @given(dims=ST.integers())
    def test_value_error_on_invalid_dimensionality(self, dims, min_reader_data):
        assume(dims not in (None, 1, 2, 3))
        with pytest.raises(ValueError):
            create_reader(min_reader_data,
                          dimensionality=dims)
