"""Optional interoperability with Numpy."""

import numpy

NUMPY_DTYPES = {'ibm': numpy.dtype('f4'),
                'l':   numpy.dtype('i4'),
                'h':   numpy.dtype('i2'),
                'f':   numpy.dtype('f4'),
                'b':   numpy.dtype('i1')}


def make_dtype(data_sample_format):
    """Convert a SEG Y data sample format to a compatible numpy dtype.

    Note :
        IBM float data sample formats ('ibm') will correspond to IEEE float data types.

    Args:
        data_sample_format: A data sample format string.

    Returns:
        A numpy.dtype instance.

    Raises:
        ValueError: For unrecognised data sample format strings.
    """
    try:
        return NUMPY_DTYPES[data_sample_format]
    except KeyError:
        raise ValueError("Unknown data sample format string {!r}".format(data_sample_format))


