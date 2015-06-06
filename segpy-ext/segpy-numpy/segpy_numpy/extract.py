"""Tools for interoperability between Segpy and Numpy arrays."""
from functools import singledispatch
import numpy as np
from segpy.util import make_sorted_distinct_sequence

from segpy_numpy.dtypes import make_dtype


class DimensionalityError:
    pass


def extract_inline_3d(reader, inline_number, xline_numbers=None, sample_numbers=None, null=None, packed=False):
    """Extract an inline as a two-dimensional array.

    Args:
        reader:

        inline_number: The number of the inline to be extracted.

        xline_numbers: An optional sorted sequence of crossline numbers at which to
            extract samples.  If not provided, samples will be extracted at all
            crosslines.

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

    if xline_numbers is None:
        xline_numbers = reader.xline_numbers()
    elif isinstance(xline_numbers, slice):
        xline_numbers = reader.xline_numbers()[xline_numbers]
    else:
        xline_numbers = make_sorted_distinct_sequence(xline_numbers)

    if sample_numbers is None:
        sample_numbers = range(0, reader.max_num_trace_samples())
    elif isinstance(sample_numbers, slice):
        sample_numbers = range(0, reader.max_num_trace_samples())[sample_numbers]
    else:
        sample_numbers = make_sorted_distinct_sequence(sample_numbers)

    shape = (len(xline_numbers), len(sample_numbers))
    dtype = make_dtype(reader.data_sample_format)

    if null is None:
        array = np.ma.masked_all(shape, dtype)
    else:
        array = np.empty(shape, dtype)
        array.fill(null)

    for xline_index, xline_number in enumerate(xline_numbers):
        inline_xline_number = (inline_number, xline_number)
        if reader.has_trace_index(inline_xline_number):
            # Read the trace
            trace_index = reader.trace_index(inline_xline_number)

            sample_start = sample_numbers[0]
            try:
                sample_stop = sample_numbers.stop
            except AttributeError:
                sample_stop = sample_numbers[-1] + 1

            num_trace_samples = reader.num_trace_samples(trace_index)
            sample_stop = max(sample_stop, num_trace_samples)

            trace_samples = reader.trace_samples(trace_index, sample_start, sample_stop)

            try:
                sample_step = sample_numbers.step
            except AttributeError:
                sample_step = None

            if sample_step is not None:
                # Assign to a slice of the target array
                source_slice = slice(
                    sample_numbers.start - sample_start,
                    sample_numbers.stop - sample_start,
                    sample_step)
                array[xline_index, :] = trace_samples[source_slice]
            else:
                # Assign element by element
                for sample_index, sample_number in enumerate(sample_numbers):
                    array[xline_number, sample_index] = trace_samples[sample_number - sample_start]
    return array