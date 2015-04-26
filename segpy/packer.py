from collections import OrderedDict
from struct import Struct
from segpy.datatypes import SEG_Y_TYPE_TO_CTYPE
from segpy.util import pairwise, intervals_partially_overlap, complementary_intervals


def size_of(t):
    return t.SIZE


def compile_struct(header_format_class):
    """Compile a struct description from a record.

    Args:
        header_format_class: A header_format class.

    Returns:
        A two-tuple containing in the zeroth element a format string which can be used with the struct.unpack function,
        and in the second element containing a list-of-lists for field names.  Each item in the out list corresponds to
        an element of the tuple of data values returned by struct.unpack(); each name associated with that index is a
        field to which the unpacked value should be assigned.

        format, allocations = compile_struct(TraceHeaderFormat)
        values = struct.unpack(format)
        field_names_to_values = {}
        for field_names, value in zip(allocations, values):
            for field_name in field_names:
                field_names_to_values[field_name] = value
        header = Header(**field_names_to_values)

    """
    fields = [getattr(header_format_class, name) for name in header_format_class._ordered_field_names]

    sorted_fields = sorted(fields, key=lambda f: f.offset)

    for a, b in pairwise(sorted_fields):
        if intervals_partially_overlap(range(a.offset, a.offset + size_of(a.value_type)),
                                       range(b.offset, b.offset + size_of(b.value_type))):
            raise ValueError("Record fields {!r} at offset {} and {!r} at offset {} are distinct but overlap."
                              .format(a.name, a.offset, b.name, b.offset))

    offset_to_fields = OrderedDict()
    for field in sorted_fields:
        if field.offset not in offset_to_fields:
            offset_to_fields[field.offset] = []
        if len(offset_to_fields[field.offset]) > 0:
            if offset_to_fields[field.offset][0].value_type is not field.value_type:
                raise ValueError("Coincident fields {!r} and {!r} at offset {} have different types {!r} and {!r}"
                                  .format(offset_to_fields[field.offset][0],
                                          field,
                                          field.offset,
                                          offset_to_fields[0].value_type,
                                          field.value_type))
        offset_to_fields[field.offset].append(field)

    # Create a list of ranges where each range spans the byte indexes covered by each field
    field_spans = [range(offset, offset + size_of(fields[0].value_type))
                   for offset, fields in offset_to_fields.items()]

    gap_spans = complementary_intervals(field_spans)

    # Create a format string usable with the struct module
    format_chunks = []
    representative_fields = (fields[0] for fields in offset_to_fields.values())
    for field, gap_span in zip(representative_fields, gap_spans):
        format_chunks.append(SEG_Y_TYPE_TO_CTYPE[field.value_type.SEG_Y_TYPE])
        format_chunks.append('x' * len(gap_span))
    format = ''.join(format_chunks)

    # Create a list of mapping item index to field names.
    # [0] -> ['field_1', 'field_2']
    # [1] -> ['field_3']
    # [2] -> ['field_4']
    field_name_allocations = [[field.name for field in fields]
                              for fields in offset_to_fields.values()]
    return format, field_name_allocations


class HeaderPacker:

    def __init__(self, header_format_class):
        self._header_format_class = header_format_class
        self._format, self._field_name_allocations = compile_struct(header_format_class)
        self._struct = Struct(self._format)

    def pack(self, header):
        """Pack a header into a buffer.
        """
        if header._format is not self._header_format_class:
            raise TypeError("{}({}) cannot pack header of type {}.".format(
                self.__class__.__name__,
                self._header_format_class.__name__,
                header.__class__.__name__
            ))
        values = [getattr(header, names[0]) for names in self._field_name_allocations]
        return self._struct.pack(*values)

    def unpack(self, buffer, header_class):
        """Unpack a header into a header object.

        Overwrites any existing header field values with new values
        obtained from the buffer.

        Returns:
            The header object.
        """
        if header_class._format is not self._header_format_class:
            raise TypeError("{}({}) cannot unpack header of type {}.".format(
                self.__class__.__name__,
                self._header_format_class.__name__,
                header_class.__name__
            ))

        values = self._struct.unpack(buffer)

        kwargs = {name: value
                  for names, value in zip(self._field_name_allocations, values)
                  for name in names }

        return header_class(**kwargs)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            self._header_format_class.__name__)