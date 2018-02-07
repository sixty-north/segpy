"""Functions for packing and unpacking IBM floats to and from standard Python
floats.

The main job of this module is to select the correct implementation of the
un/packing routines. The default version is written in pure Python, but if the
faster C++ implementation is detected then it will be used.
"""

import abc
from stevedore.extension import ExtensionManager

from segpy.ibm_float import IBMFloat
from segpy.util import EMPTY_BYTE_STRING


class PackerExtension(metaclass=abc.ABCMeta):
    """Abstract base class defining the Packer extension.

    Packers know how to pack and unpack IBM floating point format.
    """

    @abc.abstractmethod
    def pack(self, values):
        """Pack floats into binary-encoded big-endian single-precision IBM floats.

        Args:
            values: An iterable series of numeric values.

        Returns:
            A sequence of bytes.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def unpack(self, data, num_items):
        """Unpack a series of binary-encoded big-endian single-precision IBM floats.

        Args:
            data: A sequence of bytes.
            num_items: The number of floats to be read.

        Returns:
            A sequence of floats.
        """
        raise NotImplementedError


class Packer(PackerExtension):
    """Default implementation of IBM float un/packing.
    """
    def pack(self, values):
        return EMPTY_BYTE_STRING.join(bytes(IBMFloat.from_real(value))
                                      for value in values)

    def unpack(self, data, num_items):
        return [IBMFloat.from_bytes(data[i: i+4])
                for i in range(0, num_items * 4, 4)]


_EXTENSION_MANAGER = ExtensionManager(
    namespace='segpy.ibm_float_packer',
    invoke_on_load=True)


# Boolean controller whether the Python implementation of IBM floating points
# numbers will be required. If this is True, then the Python implementation
# will always be used. If it is False (default) then the C++ implementation
# will be used if it's available.
#
# This is primarily for testing purposes.
force_python_ibm_floats = False


def _active_packer():
    if force_python_ibm_floats or 'cpp' not in _EXTENSION_MANAGER:
        return Packer()

    return _EXTENSION_MANAGER['cpp'].obj


def unpack_ibm_floats(data, num_items):
    """Unpack a series of binary-encoded big-endian single-precision IBM floats.

    Args:
        data: A sequence of bytes.
        num_items: The number of floats to be read.

    Returns:
        A sequence of floats.
    """

    return _active_packer().unpack(data, num_items)


def pack_ibm_floats(values):
    """Pack floats into binary-encoded big-endian single-precision IBM floats.

    Args:
        values: An iterable series of numeric values.

    Returns:
        A sequence of bytes.
    """
    return _active_packer().pack(values)
