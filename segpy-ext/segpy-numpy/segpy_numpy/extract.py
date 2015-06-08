"""Tools for interoperability between Segpy and Numpy arrays."""
import numpy as np

from segpy.util import ensure_superset
from segpy_numpy.dtypes import make_dtype


class DimensionalityError:
    pass


def extract_inline_3d(reader, inline_number, xline_numbers=None, sample_numbers=None, null=None):
    """Extract an inline as a two-dimensional array.

    Args:
        reader:

        inline_number: The number of the inline to be extracted.

        xline_numbers: Either a sequence of crossline numbers from which traces are
            to be extracted or a slice object indicating that some slice of all
            crossline numbers is to be used.  If None, traces will be extracted at
            all crosslines.

        sample_numbers: An optional sorted sequence of samples numbers at which to
            extract samples.  If not provided, samples will be extracted at all
            depths.

        null: A null value

    Returns:
        A two-dimensional array. If null is None a masked array will be returned, otherwise
        a simple array will be returned.. The first (slowest changing) index will correspond
        to the traces (index zero will correspond to the first crossline number). The
        second (fastest changing) index will correspond to the samples (index zero will
        correspond to the first sample number.
    """
    if inline_number not in reader.inline_numbers():
        raise ValueError("Inline number {} not present in {}".format(inline_number, reader))

    xline_numbers = ensure_superset(reader.xline_numbers(), xline_numbers)
    sample_numbers = ensure_superset(range(0, reader.max_num_trace_samples()), sample_numbers)
    shape = (len(xline_numbers), len(sample_numbers))
    dtype = make_dtype(reader.data_sample_format)
    array = make_array(shape, dtype, null)

    if isinstance(sample_numbers, range):
        _populate_inline_array_over_sample_range(reader, inline_number, xline_numbers, sample_numbers, array)
    else:
        _populate_inline_array_numbered_samples(reader, inline_number, xline_numbers, sample_numbers, array)

    return array


def _populate_inline_array_numbered_samples(reader, inline_number, xline_numbers, sample_numbers, array):
    for xline_index, xline_number in enumerate(xline_numbers):
        inline_xline_number = (inline_number, xline_number)
        if reader.has_trace_index(inline_xline_number):
            trace_index = reader.trace_index(inline_xline_number)
            num_trace_samples = reader.num_trace_samples(trace_index)
            trace_sample_start = sample_numbers[0]
            trace_sample_stop = min(sample_numbers[-1] + 1, num_trace_samples)
            trace_samples = reader.trace_samples(trace_index, trace_sample_start, trace_sample_stop)
            for sample_index, sample_number in enumerate(sample_numbers):
                array[xline_index, sample_index] = trace_samples[sample_number - trace_sample_start]


def _populate_inline_array_over_sample_range(reader, inline_number, xline_numbers, sample_numbers, array):
    for xline_index, xline_number in enumerate(xline_numbers):
        inline_xline_number = (inline_number, xline_number)
        if reader.has_trace_index(inline_xline_number):
            trace_index = reader.trace_index(inline_xline_number)
            num_trace_samples = reader.num_trace_samples(trace_index)
            trace_sample_stop = min(sample_numbers.stop, num_trace_samples)
            trace_samples = reader.trace_samples(trace_index, sample_numbers.start, trace_sample_stop)
            source_slice = slice(sample_numbers.start, trace_sample_stop, sample_numbers.step)
            array[xline_index, :] = trace_samples[source_slice]


def make_array(shape, dtype, null=None):
    """Make an array"""
    if null is None:
        return np.ma.masked_all(shape, dtype)

    array = np.empty(shape, dtype)
    array.fill(null)
    return array


def start_and_stop(sequence):
    """Obtain start and stop values from a sequence."""
    sample_start = sequence[0]
    try:
        sample_stop = sequence.stop
    except AttributeError:
        sample_stop = sequence[-1] + 1
    return sample_start, sample_stop
