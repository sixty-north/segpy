"""Functions for packing and unpacking IBM floats to and from standard Python
floats.

The main job of this module is to select the correct implementation of the
un/packing routines. The default version is written in pure Python, but if the
faster C++ implementation is detected then it will be used.
"""

from segpy.ibm_float import IBMFloat
from segpy.util import EMPTY_BYTE_STRING

try:
    import segpy_ibm_float_ext
    _unpack_ibm_floats_cpp = segpy_ibm_float_ext.unpack_ibm_floats
    _pack_ibm_floats_cpp = segpy_ibm_float_ext.pack_ibm_floats
except ImportError:
    _pack_ibm_floats_cpp = None
    _unpack_ibm_floats_cpp = None


# Boolean controller whether the Python implementation of IBM floating points
# numbers will be required. If this is True, then the Python implementation
# will always be used. If it is False (default) then the C++ implementation
# will be used if it's available.
#
# This is primarily for testing purposes.
force_python_ibm_floats = False


def _unpack_ibm_floats_py(data, num_items):
    return [IBMFloat.from_bytes(data[i: i+4])
            for i in range(0, num_items * 4, 4)]


def unpack_ibm_floats(data, num_items):
    """Unpack a series of binary-encoded big-endian single-precision IBM floats.

    Args:
        data: A sequence of bytes.
        num_items: The number of floats to be read.

    Returns:
        A sequence of floats.
    """
    if force_python_ibm_floats or not _unpack_ibm_floats_cpp:
        return _unpack_ibm_floats_py(data, num_items)
    else:
        return _unpack_ibm_floats_cpp(data, num_items)


def _pack_ibm_floats_py(values):
    return EMPTY_BYTE_STRING.join(bytes(IBMFloat.from_real(value))
                                  for value in values)


def pack_ibm_floats(values):
    """Pack floats into binary-encoded big-endian single-precision IBM floats.

    Args:
        values: An iterable series of numeric values.

    Returns:
        A sequence of bytes.
    """
    if force_python_ibm_floats or not _pack_ibm_floats_cpp:
        return _pack_ibm_floats_py(values)
    else:
        return _pack_ibm_floats_cpp(values)
