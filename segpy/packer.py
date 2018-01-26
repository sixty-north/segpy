from abc import abstractmethod, ABC
from collections import OrderedDict
from struct import Struct
from itertools import zip_longest

import struct

from segpy import __version__
from segpy.datatypes import SEG_Y_TYPE_TO_CTYPE
from segpy.util import pairwise, intervals_partially_overlap, complementary_intervals, all_equal


def size_of(t):
    return t.SIZE


def compile_struct(header_format_class, start_offset=0, length_in_bytes=None, endian='>'):
    """Compile a struct description from a record.

    Args:
        header_format_class: A header_format class.

        start_offset: Optional start offset for the header in bytes.  Indicates the position of the start of
            the header in the same reference frame as which the field offsets are given.

        length_in_bytes: Optional length in bytes for the header. If the supplied header described a format shorter
            than this value the returned format will be padded with placeholders for bytes to be discarded. If the
            value is less than the minimum required for the format described by header_format_class an error will be
            raised.

        endian: '>' for big-endian data (the standard and default), '<'
            for little-endian (non-standard).

    Returns:
        A two-tuple containing in the zeroth element a format string which can be used with the struct.unpack function,
        and in the second element containing a list-of-lists for field names.  Each item in the outer list corresponds
        to an element of the tuple of data values returned by struct.unpack(); each name associated with that index is a
        field to which the unpacked value should be assigned.

    Usage:

        format, allocations = compile_struct(TraceHeaderFormat)
        values = struct.unpack(format)
        field_names_to_values = {}
        for field_names, value in zip(allocations, values):
            for field_name in field_names:
                field_names_to_values[field_name] = value
        header = Header(**field_names_to_values)

    Raises:
        ValueError: If header_format_class defines no fields.
        ValueError: If header_format_class contains fields which overlap but are not exactly coincident.
        ValueError: If header_format_class contains coincident fields of different types.
        ValueError: If header_format_class described a format longer than length_in_bytes.

    """
    if start_offset < 0:
        raise ValueError("start_offset {} is less than zero".format(start_offset))

    if isinstance(length_in_bytes, int) and length_in_bytes < 1:
        raise ValueError("length_in_bytes {} is less than one".format(length_in_bytes))

    fields = [getattr(header_format_class, name) for name in header_format_class.ordered_field_names()]

    sorted_fields = sorted(fields, key=lambda f: f.offset)

    if len(sorted_fields) < 1:
        raise TypeError("Header format class {!r} defines no fields".format(header_format_class.__name__))

    if len(sorted_fields) > 1:
        for a, b in pairwise(sorted_fields):
            if intervals_partially_overlap(range(a.offset, a.offset + size_of(a.value_type)),
                                           range(b.offset, b.offset + size_of(b.value_type))):
                raise ValueError("Fields {!r} at offset {} and {!r} at offset {} of {} are distinct but overlap."
                                  .format(a.name, a.offset, b.name, b.offset, header_format_class.__name__))

    last_field = sorted_fields[-1]
    defined_length = (last_field.offset - start_offset) + size_of(last_field.value_type)
    specified_length = defined_length if (length_in_bytes is None) else length_in_bytes
    padding_length = specified_length - defined_length
    if padding_length < 0:
        raise ValueError("Header length {!r} bytes defined by {!r} is less than specified length in bytes {!r}"
                         .format(defined_length, header_format_class.__name__, specified_length))

    offset_to_fields = OrderedDict()
    for field in sorted_fields:
        relative_offset = field.offset - start_offset  # relative_offser is zero-based
        if relative_offset not in offset_to_fields:
            offset_to_fields[relative_offset] = []
        if len(offset_to_fields[relative_offset]) > 0:
            if offset_to_fields[relative_offset][0].value_type is not field.value_type:
                raise TypeError("Coincident fields {!r} and {!r} at offset {} have different types {} and {}"
                                  .format(offset_to_fields[relative_offset][0],
                                          field,
                                          offset_to_fields[relative_offset][0].offset,
                                          offset_to_fields[relative_offset][0].value_type.__name__,
                                          field.value_type.__name__))
        offset_to_fields[relative_offset].append(field)

    # Create a list of ranges where each range spans the byte indexes covered by each field
    field_spans = [range(offset, offset + size_of(fields[0].value_type))
                   for offset, fields in offset_to_fields.items()]

    gap_intervals = complementary_intervals(field_spans, start=0, stop=specified_length)  # One-based indexes

    # Create a format string usable with the struct module
    format_chunks = [endian]
    representative_fields = (fields[0] for fields in offset_to_fields.values())
    for gap_interval, field in zip_longest(gap_intervals, representative_fields, fillvalue=None):
        gap_length = len(gap_interval)
        if gap_length > 0:
            format_chunks.append('x' * gap_length)
        if field is not None:
            format_chunks.append(SEG_Y_TYPE_TO_CTYPE[field.value_type.SEG_Y_TYPE])
    cformat = ''.join(format_chunks)

    # Create a list of mapping item index to field names.
    # [0] -> ['field_1', 'field_2']
    # [1] -> ['field_3']
    # [2] -> ['field_4']
    field_name_allocations = [[field.name for field in fields]
                              for fields in offset_to_fields.values()]
    return cformat, field_name_allocations


def make_header_packer(header_format_class, endian='>'):
    cformat, field_name_allocations = compile_struct(
        header_format_class,
        getattr(header_format_class, 'START_OFFSET_IN_BYTES', 0),
        getattr(header_format_class, 'LENGTH_IN_BYTES', None),
        endian)
    structure = Struct(cformat)

    one_to_one = all(len(fields) == 1 for fields in field_name_allocations)

    if one_to_one:
        return BijectiveHeaderPacker(header_format_class, structure, field_name_allocations)
    return SurjectiveHeaderPacker(header_format_class, structure, field_name_allocations)


class HeaderPacker(ABC):
    """Packing and unpacking header instances."""

    def __init__(self, header_format_class, structure, field_name_allocations):
        self._header_format_class = header_format_class
        self._structure = structure
        self._field_name_allocations = field_name_allocations

    def __getstate__(self):
        state = self.__dict__.copy()
        state['__version__'] = __version__
        state['_structure_format'] = self._structure.format
        del state['_structure']
        return state

    def __setstate__(self, state):
        if state['__version__'] != __version__:
            raise TypeError("Cannot unpickle {} version {} into version {}"
                            .format(self.__class__.__name__,
                                    state['__version__'],
                                    __version__))
        del state['__version__']

        structure = Struct(state['_structure_format'])
        state['_structure'] = structure
        del state['_structure_format']
        self.__dict__.update(state)

    @property
    def header_format_class(self):
        return self._header_format_class

    def pack(self, header):
        """Pack a header into a buffer.
        """
        if not isinstance(header, self._header_format_class):
            raise TypeError("{}({}) cannot pack header of type {}.".format(
                self.__class__.__name__,
                self._header_format_class.__name__,
                header.__class__.__name__
            ))
        return self._pack(header)

    def unpack(self, buffer):
        """Unpack a header into a header object.

        Overwrites any existing header field values with new values
        obtained from the buffer.

        Returns:
            The header object.
        """
        try:
            values = self._structure.unpack(buffer)
        except struct.error as e:
                raise ValueError("Buffer of length {} too short"
                                 .format(len(buffer),
                                         str(e).capitalize())) from e
        else:
            return self._unpack(values)

    @abstractmethod
    def _pack(self, header):
        raise NotImplementedError

    @abstractmethod
    def _unpack(self, values):
        raise NotImplementedError

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            self._header_format_class.__name__)


class BijectiveHeaderPacker(HeaderPacker):
    """One-to-one packing/unpacking of serialised values to header fields."""

    def _pack(self, header):
        values = [getattr(header, names[0]) for names in self._field_name_allocations]
        return self._structure.pack(*values)

    def _unpack(self, values):
        return self._header_format_class(*values)


class SurjectiveHeaderPacker(HeaderPacker):
    """One-to-many unpacking of serialised values to header fields."""

    def _pack(self, header):
        for names in self._field_name_allocations:
            field_values = [getattr(header, name) for name in names]
            if not all_equal(field_values):
                raise ValueError("fields {} have unequal values {}"
                                 .format(', '.join(names),
                                         ', '.join(map(str, field_values))))

        values = [getattr(header, names[0]) for names in self._field_name_allocations]
        return self._structure.pack(*values)

    def _unpack(self, values):
        kwargs = {name: value
                  for names, value in zip(self._field_name_allocations, values)
                  for name in names}

        return self._header_format_class(**kwargs)
