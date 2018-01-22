from hypothesis import given, settings, HealthCheck, Phase
import hypothesis.strategies as st
import pytest
from io import BytesIO
from pytest import raises

from segpy.encoding import SUPPORTED_ENCODINGS
from segpy.ibm_float import EPSILON_IBM_FLOAT, ieee2ibm
import segpy.toolkit as toolkit
from segpy.util import almost_equal
from unittest.mock import patch

from test.dataset_strategy import extended_textual_header
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

