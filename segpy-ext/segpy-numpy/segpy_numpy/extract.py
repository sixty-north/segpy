"""Tools for interoperability between Segpy and Numpy arrays."""
from collections import namedtuple
import numpy as np
from segpy.header import Header, SubFormatMeta
from segpy.packer import make_header_packer

from segpy.util import ensure_superset
from segpy_numpy.dtypes import make_dtype


class DimensionalityError:
    pass


# TODO: Add inline_numbers and xline_numbers arguments
def extract_trace_header_field_3d(reader, fields, null=None):
    """Extract a single trace header field from all trace headers as an array.

    Args:
        reader: A SegYReader3D

        fields: A an iterable series where each item is either the string name of a field
            or an object with a 'name' attribute which is the name of a field, such as a
            NamedField.

        null: An optional null value for missing traces. The null value must be convertible
            to all field value types.

    Returns:
        An namedtuple object with attributes which are two-dimensional Numpy arrays.
        If a null value was specified the arrays will be ndarrays, otherwise they
        will be masked arrays.  The attributes of the named tuple are in the same
        order as the fields specified in the `fields` argument.

    Raises:
        AttributeError: If the the named fields do not exist in the trace header definition.
    """
    field_names = [_extract_field_name(field) for field in fields]

    class SubHeader(metaclass=SubFormatMeta,
                    parent_format=reader.trace_header_format_class,
                    parent_field_names=field_names):
        pass

    sub_header_packer = make_header_packer(SubHeader, reader.endian)
    TraceHeaderArrays = namedtuple('TraceHeaderArrays', field_names)
    shape = (reader.num_inlines(), reader.num_xlines())

    arrays = (_make_array(shape,
                          make_dtype(getattr(SubHeader, field_name).value_type.SEG_Y_TYPE),
                          null)
              for field_name in field_names)

    trace_header_arrays = TraceHeaderArrays(*arrays)

    for inline_xline in reader.inline_xline_numbers():
        inline_number, xline_number = inline_xline
        trace_index = reader.trace_index(inline_xline)
        trace_header = reader.trace_header(trace_index, sub_header_packer)
        inline_index = reader.inline_numbers().index(inline_number)
        xline_index = reader.xline_numbers().index(xline_number)

        for field_name, a in zip(field_names, trace_header_arrays):
            field_value = getattr(trace_header, field_name)
            a[inline_index, xline_index] = field_value

    return trace_header_arrays


def extract_trace(reader, trace_index, sample_numbers):
    """Extract an single trace as a one-dimensional array.

    Args:
        reader: A SegYReader3D object.

        trace_index: The index of the trace to be extracted.

        sample_numbers: The sample numbers within each trace at which samples are to be extracted.
            This argument can be specified in three ways:

            None (the default) - All samples within the trace will be be extracted.

            sequence - When a sequence, such as a range or a list is provided only those samples at
                sample numbers corresponding to the items in the sequence will be extracted. The
                samples will always be extracted in increasing numeric order and duplicate entries
                will be ignored.  For example sample_numbers=range(100, 200, 2) will extract alternate
                samples from sample number 100 to sample number 198 inclusive.

            slice - When a slice object is provided the slice will be applied to the sequence of all
                sample numbers. For example sample_numbers=slice(100, -100) will omit the first
                one hundred and the last one hundred samples, irrespective of their numbers.

    Returns:
        A one-dimensional array.
    """
    if not reader.has_trace_index(trace_index):
        raise ValueError("Inline number {} not present in {}".format(trace_index, reader))

    sample_numbers = ensure_superset(range(0, reader.max_num_trace_samples()), sample_numbers)

    trace_sample_start = sample_numbers[0]
    trace_sample_stop = min(sample_numbers[-1] + 1, reader.num_trace_samples(trace_index))
    trace_samples = reader.trace_samples(trace_index, trace_sample_start, trace_sample_stop)
    arr = np.fromiter((trace_samples[sample_number - trace_sample_start] for sample_number in sample_numbers),
                      make_dtype(reader.data_sample_format))
    return arr


def extract_inline_3d(reader_3d, inline_number, xline_numbers=None, sample_numbers=None, null=None):
    """Extract an inline as a two-dimensional array.

    Args:
        reader: A SegYReader3D object.

        inline_number: The number of the inline to be extracted.

        xline_numbers: The crossline numbers within the inline at which traces are to be extracted.
            This argument can be specified in three ways:

            None (the default) - All traces within the inline will be be extracted.

            sequence - When a sequence, such as a range or a list is provided only those traces at
                crossline numbers corresponding to the items in the sequence will be extracted. The
                traces will always be extracted in increasing numeric order and duplicate entries
                will be ignored.  For example xline_numbers=range(100, 200, 2) will extract alternate
                traces from crossline number 100 to crossline number 198 inclusive.

            slice - When a slice object is provided the slice will be applied to the sequence of all
                crossline numbers. For example xline_numbers=slice(100, -100) will omit the first
                one hundred and the last one hundred traces, irrespective of their numbers.

        sample_numbers: The sample numbers within each trace at which samples are to be extracted.
            This argument can be specified in three ways:

            None (the default) - All samples within the trace will be be extracted.

            sequence - When a sequence, such as a range or a list is provided only those samples at
                sample numbers corresponding to the items in the sequence will be extracted. The
                samples will always be extracted in increasing numeric order and duplicate entries
                will be ignored.  For example sample_numbers=range(100, 200, 2) will extract alternate
                samples from sample number 100 to sample number 198 inclusive.

            slice - When a slice object is provided the slice will be applied to the sequence of all
                sample numbers. For example sample_numbers=slice(100, -100) will omit the first
                one hundred and the last one hundred samples, irrespective of their numbers.

        null: A null value. When None is specified as the null value a masked array will be returned.

    Returns:
        A two-dimensional array. If null is None a masked array will be returned, otherwise
        a regular array will be returned. The first (slowest changing) index will correspond
        to the traces (index zero will correspond to the first crossline number). The
        second (fastest changing) index will correspond to the samples (index zero will
        correspond to the first sample number.
    """
    if inline_number not in reader_3d.inline_numbers():
        raise ValueError("Inline number {} not present in {}".format(inline_number, reader_3d))

    xline_numbers = ensure_superset(reader_3d.xline_numbers(), xline_numbers)
    sample_numbers = ensure_superset(range(0, reader_3d.max_num_trace_samples()), sample_numbers)
    shape = (len(xline_numbers), len(sample_numbers))
    dtype = make_dtype(reader_3d.data_sample_format)
    array = _make_array(shape, dtype, null)

    if isinstance(sample_numbers, range):
        _populate_inline_array_over_sample_range(reader_3d, inline_number, xline_numbers, sample_numbers, array)
    else:
        _populate_inline_array_numbered_samples(reader_3d, inline_number, xline_numbers, sample_numbers, array)

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


def _make_array(shape, dtype, null=None):
    """Make an array"""
    if null is None:
        return np.ma.masked_all(shape, dtype)
    array = np.empty(shape, dtype)
    array.fill(null)
    return array

def _extract_field_name(field):
    """Args:
        field: If field in an object with a name attribute the name is returned. If field is a string it is returned
            unmodified.
      Raises:
        TypeError:
    """
    if isinstance(field, str):
        return field
    try:
        return field.name
    except AttributeError:
        raise TypeError("{!r} neither is a string nor has a 'name' attribute".format(field))