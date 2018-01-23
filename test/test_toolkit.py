import os
from itertools import zip_longest
from types import SimpleNamespace

import struct
from hypothesis import given, settings, HealthCheck, Phase, assume
import hypothesis.strategies as st
import pytest
from io import BytesIO
from pytest import raises

from segpy.binary_reel_header import BinaryReelHeader
from segpy.datatypes import DataSampleFormat, SegYType, SEG_Y_TYPE_TO_CTYPE, PY_TYPES, LIMITS
from segpy.encoding import SUPPORTED_ENCODINGS
from segpy.header import are_equal
from segpy.ibm_float import EPSILON_IBM_FLOAT, ieee2ibm
import segpy.toolkit as toolkit
from segpy.packer import make_header_packer
from segpy.trace_header import TraceHeaderRev1
from segpy.util import almost_equal
from unittest.mock import patch

from test.dataset_strategy import extended_textual_header
from test.strategies import header, NUMBER_STRATEGY
from test.test_float import any_ibm_compatible_floats
import test.util


@st.composite
def byte_arrays_of_floats(draw):
    num_items = draw(st.integers(min_value=0, max_value=10))
    floats = draw(st.lists(any_ibm_compatible_floats,
                           min_size=num_items,
                           max_size=num_items))
    byte_data = b''.join([ieee2ibm(f) for f in floats])
    return (byte_data, num_items)


@pytest.mark.usefixtures("ibm_floating_point_impls")
class TestPackIBMFloat:
    def test_pack_empty(self):
        dest = toolkit.pack_ibm_floats([])
        assert len(dest) == 0

    @given(st.lists(any_ibm_compatible_floats))
    def test_packed_floats_are_four_bytes(self, floats):
        packed = toolkit.pack_ibm_floats(floats)
        assert len(packed) == len(floats) * 4

    @given(st.lists(any_ibm_compatible_floats))
    def test_roundtrip(self, data):
        packed = toolkit.pack_ibm_floats(data)
        unpacked = toolkit.unpack_ibm_floats(packed, len(data))
        for f, u in zip(data, unpacked):
            assert almost_equal(
                f, float(u),
                epsilon=EPSILON_IBM_FLOAT)


class TestPackImplementationSelection:
    @given(st.data())
    def test_python_pack_used_when_forced(self, data):
        data = data.draw(byte_arrays_of_floats())
        with patch('segpy.toolkit.pack_ibm_floats_py') as mock,\
             test.util.force_python_ibm_float(True):
            toolkit.pack_ibm_floats(data)
            assert mock.called

    @pytest.mark.skipif(toolkit.pack_ibm_floats_cpp is None,
                        reason="C++ IBM float not installed")
    @given(st.data())
    def test_cpp_pack_used_when_available(self, data):
        data = data.draw(byte_arrays_of_floats())
        with patch('segpy.toolkit.pack_ibm_floats_cpp') as mock,\
             test.util.force_python_ibm_float(False):
            toolkit.pack_ibm_floats(data)
            assert mock.called

    @pytest.mark.skipif(toolkit.pack_ibm_floats_cpp is not None,
                        reason="C++ IBM float is installed")
    @given(st.data())
    def test_python_pack_used_as_fallback(self, data):
        data = data.draw(byte_arrays_of_floats())
        with patch('segpy.toolkit.pack_ibm_floats_py') as mock,\
             test.util.force_python_ibm_float(False):
            toolkit.pack_ibm_floats(data)
            assert mock.called


@pytest.mark.usefixtures("ibm_floating_point_impls")
class TestUnpackIBMFloat:
    def test_unpack_empty(self):
        dest = toolkit.pack_ibm_floats(b'')
        assert len(dest) == 0

    @given(byte_arrays_of_floats())
    def test_roundtrip(self, floats):
        byte_data, num_items = floats
        unpacked = toolkit.unpack_ibm_floats(byte_data, num_items)
        packed = toolkit.pack_ibm_floats(unpacked)
        assert bytes(byte_data) == bytes(packed)


class TestUnpackImplementationSelection:
    @given(st.data())
    def test_python_unpack_used_when_forced(self, data):
        data = data.draw(byte_arrays_of_floats())
        with patch('segpy.toolkit.unpack_ibm_floats_py') as mock,\
             test.util.force_python_ibm_float(True):
            toolkit.unpack_ibm_floats(*data)
            assert mock.called

    @pytest.mark.skipif(toolkit.unpack_ibm_floats_cpp is None,
                        reason="C++ IBM float not installed")
    @given(st.data())
    def test_cpp_unpack_used_when_available(self, data):
        data = data.draw(byte_arrays_of_floats())
        with patch('segpy.toolkit.unpack_ibm_floats_cpp') as mock,\
             test.util.force_python_ibm_float(False):
            toolkit.unpack_ibm_floats(*data)
            assert mock.called

    @pytest.mark.skipif(toolkit.unpack_ibm_floats_cpp is not None,
                        reason="C++ IBM float is installed")
    @given(st.data())
    def test_python_unpack_used_as_fallback(self, data):
        data = data.draw(byte_arrays_of_floats())
        with patch('segpy.toolkit.unpack_ibm_floats_py') as mock,\
             test.util.force_python_ibm_float(False):
            toolkit.unpack_ibm_floats(*data)
            assert mock.called


class TestReadExtendedHeadersCounted:

    @given(num_expected=st.integers(max_value=-1),
           encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    def test_negative_num_expected_raises_value_error(self, num_expected, encoding):
        with raises(ValueError):
            toolkit.read_extended_headers_counted(None, num_expected, encoding)

    @given(encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    def test_zero_expected_returns_empty_list(self, encoding):
        headers = toolkit.read_extended_headers_counted(None, num_expected=0, encoding=encoding)
        assert headers == []

    @given(
        data=st.data(),
        count=st.integers(min_value=1, max_value=10),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_read_header_successfully(self, data, count, encoding):
        written_headers = data.draw(extended_textual_header(count=count))
        with BytesIO() as fh:
            for header in written_headers:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0)
            read_headers = toolkit.read_extended_headers_counted(fh, count, encoding=encoding)
            assert read_headers == written_headers

    @given(
        data=st.data(),
        count_a=st.integers(min_value=1, max_value=10),
        count_b=st.integers(min_value=1, max_value=10),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_premature_end_text_stanza_raises_value_error(self, data, count_a, count_b, encoding):
        headers_a = data.draw(extended_textual_header(count=count_a, end_text_stanza_probability=1.0))
        headers_b = data.draw(extended_textual_header(count=count_b))
        with BytesIO() as fh:
            for header in headers_a:
                for line in header:
                    fh.write(line.encode(encoding))
            for header in headers_b:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0)
            with raises(ValueError):
                toolkit.read_extended_headers_counted(fh, count_a + count_b, encoding=encoding)

    @given(
        data=st.data(),
        count=st.integers(min_value=1, max_value=10),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS),
        random=st.randoms())
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_read_truncated_header_raises_error(self, data, count, encoding, random):
        written_headers = data.draw(extended_textual_header(count=count))
        with BytesIO() as fh:
            for header in written_headers:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0, os.SEEK_END)
            length = fh.tell()

            truncate_pos = random.randrange(0, length - 1)

            truncated_buffer = fh.getbuffer()[:truncate_pos]
            with BytesIO(truncated_buffer):
                with raises(EOFError):
                    toolkit.read_extended_headers_counted(fh, count, encoding=encoding)
            del truncated_buffer


class TestBytesPerSample:

    @given(bad_dsf=st.integers(-32768, +32767))
    def test_invalid_bytes_per_sample_field_raises_value_error(self, bad_dsf):
        assume(all(bad_dsf != f for f in DataSampleFormat))  # IntEnum doesn't support the in operator for integers
        fake_header = SimpleNamespace()
        fake_header.data_sample_format = bad_dsf
        with raises(ValueError):
            toolkit.bytes_per_sample(fake_header)

    @given(binary_reel_header=header(BinaryReelHeader))
    def test_valid_bytes_per_sample(self, binary_reel_header):
        bps = toolkit.bytes_per_sample(binary_reel_header)
        assert bps in {1, 2, 4}


@given(binary_reel_header=header(BinaryReelHeader),
       spt=st.integers(min_value=0, max_value=1000))
def test_samples_per_trace(binary_reel_header, spt):
    binary_reel_header.num_samples = spt
    assert toolkit.samples_per_trace(binary_reel_header) == spt


@given(binary_reel_header=header(BinaryReelHeader),
       bps=st.sampled_from((1, 2, 4)))
def test_empty_traces_have_same_length_as_trace_header(binary_reel_header, bps):
    binary_reel_header.num_samples = 0
    assert toolkit.trace_length_bytes(binary_reel_header, bps) == toolkit.TRACE_HEADER_NUM_BYTES


@given(binary_reel_header=header(BinaryReelHeader),
       bps=st.sampled_from((1, 2, 4)))
def test_on_sample_traces_have_same_length_as_trace_header_plus_one_sample(binary_reel_header, bps):
    binary_reel_header.num_samples = 1
    assert toolkit.trace_length_bytes(binary_reel_header, bps) == toolkit.TRACE_HEADER_NUM_BYTES + bps


class TestCatalogTraces:

    def test_non_callable_progress_raises_type_error(self):
        with raises(TypeError):
            toolkit.catalog_traces(None, None, progress=object())


class TestReadTraceHeader:

    @given(trace_header_written=header(TraceHeaderRev1),
           endian=st.sampled_from(('<', '>')))
    def test_read_header_successfully(self, trace_header_written, endian):
        trace_header_packer = make_header_packer(TraceHeaderRev1, endian)
        buffer = trace_header_packer.pack(trace_header_written)
        with BytesIO(buffer) as fh:
            trace_header = toolkit.read_trace_header(fh, trace_header_packer, pos=0)
            assert are_equal(trace_header_written, trace_header)

    @given(trace_header_written=header(TraceHeaderRev1),
           endian=st.sampled_from(('<', '>')),
           random=st.randoms())
    def test_read_trunctated_header_raises_eoferror(self, trace_header_written, endian, random):
        trace_header_packer = make_header_packer(TraceHeaderRev1, endian)
        buffer = trace_header_packer.pack(trace_header_written)
        truncate_pos = random.randrange(0, len(buffer))
        truncated_buffer = buffer[:truncate_pos]
        with BytesIO(truncated_buffer) as fh:
            with raises(EOFError):
                toolkit.read_trace_header(fh, trace_header_packer, pos=0)


class TestReadBinaryValues:

    @given(seg_y_type=st.sampled_from(SegYType),
           num_items=st.integers(min_value=0, max_value=100),
           endian=st.sampled_from(('<', '>')),
           data=st.data())
    def test_read_binary_values_successfully(self, seg_y_type, num_items, endian, data):
        assume(seg_y_type != SegYType.IBM)
        ctype = SEG_Y_TYPE_TO_CTYPE[seg_y_type]
        c_format = ''.join(map(str, (endian, num_items, ctype)))
        py_type = PY_TYPES[seg_y_type]
        min_value, max_value = LIMITS[seg_y_type]
        items_written = data.draw(st.lists(
            elements=NUMBER_STRATEGY[py_type](min_value=min_value, max_value=max_value),
            min_size=num_items, max_size=num_items))
        buffer = struct.pack(c_format, *items_written)
        with BytesIO(buffer) as fh:
            items_read = toolkit.read_binary_values(fh, 0, seg_y_type, num_items, endian)
            assert all(a == b for a, b in zip_longest(items_read, items_read))

    @given(seg_y_type=st.sampled_from(SegYType),
           num_items=st.integers(min_value=1, max_value=100),
           endian=st.sampled_from(('<', '>')),
           data=st.data())
    def test_truncated_read_binary_values_raises_eof_error(self, seg_y_type, num_items, endian, data):
        assume(seg_y_type != SegYType.IBM)
        ctype = SEG_Y_TYPE_TO_CTYPE[seg_y_type]
        c_format = ''.join(map(str, (endian, num_items, ctype)))
        py_type = PY_TYPES[seg_y_type]
        min_value, max_value = LIMITS[seg_y_type]
        items_written = data.draw(st.lists(
            elements=NUMBER_STRATEGY[py_type](min_value=min_value, max_value=max_value),
            min_size=num_items, max_size=num_items))
        buffer = struct.pack(c_format, *items_written)
        truncate_pos = data.draw(st.integers(min_value=0, max_value=max(0, len(buffer) - 1)))
        truncated_buffer = buffer[:truncate_pos]
        with BytesIO(truncated_buffer) as fh:
            with raises(EOFError):
                toolkit.read_binary_values(fh, 0, seg_y_type, num_items, endian)
