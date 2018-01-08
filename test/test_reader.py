"""Tests for segpy.reader.
"""

import io

from hypothesis import assume, given, HealthCheck, Phase, settings, unlimited
import hypothesis.strategies as ST
import pytest
from segpy.header import are_equal
from segpy.reader import create_reader
from segpy.toolkit import REEL_HEADER_NUM_BYTES
from segpy.writer import write_segy
from .dataset_strategy import dataset


@pytest.fixture
def min_reader_data():
    "Binary data of minimal size to satisfy `create_reader`."
    return io.BytesIO(b'0' * REEL_HEADER_NUM_BYTES)


# To test:
# - cache directory
# - progress callback
# - round-tripping of data
# - reader attributes
# - 1, 2, and 3D data
# - Dimensionality heuristics (i.e. passing `None` as dimensionality.)


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


@given(dataset(dims=2))
@settings(
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_round_trip(tmpdir, dataset):
    segy_file = str(tmpdir / 'test.segy')

    with open(segy_file, mode='bw') as fh:
        write_segy(fh, dataset)

    with open(segy_file, mode='br') as fh:
        reader = create_reader(
            fh,
            trace_header_format=dataset._trace_header_format,
            dimensionality=dataset.dimensionality)

        assert dataset.textual_reel_header == reader.textual_reel_header
        assert are_equal(dataset.binary_reel_header, reader.binary_reel_header)
        assert dataset.extended_textual_header == reader.extended_textual_header
        assert dataset.dimensionality == reader.dimensionality
        assert tuple(dataset.trace_indexes()) == tuple(reader.trace_indexes())
        assert dataset.num_traces() == reader.num_traces()
        assert len(list(dataset.trace_indexes())) == dataset.num_traces()
        assert len(list(reader.trace_indexes())) == reader.num_traces()
        assert sorted(dataset.trace_indexes()) == sorted(reader.trace_indexes())

        for trace_index in dataset.trace_indexes():
            assert list(dataset.trace_samples(trace_index)) == list(reader.trace_samples(trace_index))
