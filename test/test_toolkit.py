from hypothesis import given
import hypothesis.strategies as st
import pytest
from segpy.ibm_float import EPSILON_IBM_FLOAT, ieee2ibm
import segpy.toolkit as toolkit
from segpy.util import almost_equal

from test.test_float import any_ibm_compatible_floats


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
