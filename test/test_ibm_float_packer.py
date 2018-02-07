from hypothesis import given
import hypothesis.strategies as st
import pytest
from unittest.mock import MagicMock, patch

from segpy import ibm_float_packer
from segpy.ibm_float import EPSILON_IBM_FLOAT, ieee2ibm
from segpy.util import almost_equal

from test.test_float import ibm_compatible_floats
import test.util


@st.composite
def byte_arrays_of_floats(draw):
    num_items = draw(st.integers(min_value=0, max_value=10))
    floats = draw(st.lists(ibm_compatible_floats(),
                           min_size=num_items,
                           max_size=num_items))
    byte_data = b''.join([ieee2ibm(f) for f in floats])
    return (byte_data, num_items)


@pytest.mark.usefixtures("ibm_floating_point_impls")
class TestPackIBMFloat:
    """This tests the actual Python pack implementation.
    """

    def test_pack_empty(self):
        dest = ibm_float_packer.pack_ibm_floats([])
        assert len(dest) == 0

    @given(st.lists(ibm_compatible_floats()))
    def test_packed_floats_are_four_bytes(self, floats):
        packed = ibm_float_packer.pack_ibm_floats(floats)
        assert len(packed) == len(floats) * 4

    @given(st.lists(ibm_compatible_floats()))
    def test_roundtrip(self, data):
        packed = ibm_float_packer.pack_ibm_floats(data)
        unpacked = ibm_float_packer.unpack_ibm_floats(packed, len(data))
        for f, u in zip(data, unpacked):
            assert almost_equal(
                f, float(u),
                epsilon=EPSILON_IBM_FLOAT)


@pytest.mark.usefixtures("ibm_floating_point_impls")
class TestUnpackIBMFloat:
    """This tests the actual Python unpack implementation.
    """

    def test_unpack_empty(self):
        dest = ibm_float_packer.pack_ibm_floats(b'')
        assert len(dest) == 0

    @given(byte_arrays_of_floats())
    def test_roundtrip(self, floats):
        byte_data, num_items = floats
        unpacked = ibm_float_packer.unpack_ibm_floats(byte_data, num_items)
        packed = ibm_float_packer.pack_ibm_floats(unpacked)
        assert bytes(byte_data) == bytes(packed)


class TestPackImplementationSelection:
    """This tests whether the correct pack implementation is selected.
    """
    @patch('segpy.ibm_float_packer._EXTENSION_MANAGER')
    @patch('segpy.ibm_float_packer.Packer')
    def test_python_pack_used_when_forced(self, python_packer, mgr):
        # Let the manager report that it contains 'cpp'
        mgr.__contains__ = MagicMock(return_value=True)

        data = byte_arrays_of_floats().example()
        with test.util.force_python_ibm_float(True):
            ibm_float_packer.pack_ibm_floats(data)
            mgr.__getitem__.assert_not_called()
            python_packer.return_value.pack.assert_called_with(data)

    @patch('segpy.ibm_float_packer._EXTENSION_MANAGER')
    @patch('segpy.ibm_float_packer.Packer')
    def test_cpp_pack_used_when_available(self, python_packer, mgr):
        # Let the manager report that it contains 'cpp'
        mgr.__contains__ = MagicMock(return_value=True)

        data = byte_arrays_of_floats().example()
        with test.util.force_python_ibm_float(False):
            ibm_float_packer.pack_ibm_floats(data)
            mgr.__getitem__.assert_called_once_with('cpp')
            mgr.__getitem__.return_value.obj.pack.assert_called_with(data)
            python_packer.return_value.pack.assert_not_called()


    @patch('segpy.ibm_float_packer._EXTENSION_MANAGER')
    @patch('segpy.ibm_float_packer.Packer')
    def test_python_pack_used_as_fallback(self, python_packer, mgr):
        # Don't let the manager report that it contains 'cpp'
        mgr.__contains__ = MagicMock(return_value=False)

        data = byte_arrays_of_floats()
        with test.util.force_python_ibm_float(False):
            ibm_float_packer.pack_ibm_floats(data)
            python_packer.return_value.pack.assert_called_with(data)


class TestUnpackImplementationSelection:
    @patch('segpy.ibm_float_packer._EXTENSION_MANAGER')
    @patch('segpy.ibm_float_packer.Packer')
    def test_python_unpack_used_when_forced(self, python_packer, mgr):
        # Let the manager report that it contains 'cpp'
        mgr.__contains__ = MagicMock(return_value=True)

        data = byte_arrays_of_floats().example()
        with test.util.force_python_ibm_float(True):
            ibm_float_packer.unpack_ibm_floats(*data)
            mgr.__getitem__.assert_not_called()
            python_packer.return_value.unpack.assert_called_with(*data)

    @patch('segpy.ibm_float_packer._EXTENSION_MANAGER')
    @patch('segpy.ibm_float_packer.Packer')
    def test_cpp_unpack_used_when_available(self, python_packer, mgr):
        # Let the manager report that it contains 'cpp'
        mgr.__contains__ = MagicMock(return_value=True)

        data = byte_arrays_of_floats().example()
        with test.util.force_python_ibm_float(False):
            ibm_float_packer.unpack_ibm_floats(*data)
            mgr.__getitem__.assert_called_once_with('cpp')
            mgr.__getitem__.return_value.obj.unpack.assert_called_with(*data)
            python_packer.return_value.unpack.assert_not_called()

    @patch('segpy.ibm_float_packer._EXTENSION_MANAGER')
    @patch('segpy.ibm_float_packer.Packer')
    def test_python_unpack_used_as_fallback(self, python_packer, mgr):
        # Don't let the manager report that it contains 'cpp'
        mgr.__contains__ = MagicMock(return_value=False)

        data = byte_arrays_of_floats().example()
        with test.util.force_python_ibm_float(False):
            ibm_float_packer.unpack_ibm_floats(*data)
            mgr.__getitem__.assert_not_called()
            python_packer.return_value.unpack.assert_called_with(*data)
