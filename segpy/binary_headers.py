from segpy.field import field_mangler, BinaryFieldDescriptor, ValueFieldDescriptor


class BinaryFormat(object,
                   metaclass=field_mangler(descriptor=BinaryFieldDescriptor)):
    """Base class for headers format definitions comprised of BinaryFields."""

    def __init__(self, **field_types_and_offsets):
        """Override default types and offsets.

        Args:
            **field_types_and_offsets: Keywords arguments, with names corresponding to the
                binary_fields may be provided where each name is associated with a 2-tuple
                containing a field_type and an offset in bytes.
        """
        for name, (field_type, offset) in field_types_and_offsets:
            if not hasattr(self, name):
                raise TypeError("Unknown attribute {!r}".format(name))
            fld = getattr(self, name)
            fld.ftype = field_type
            fld.offset = offset
        # TODO: Consider validating for overlaps


class Header(object,
             metaclass=field_mangler(descriptor=ValueFieldDescriptor)):
    """Base class for headers comprised of ValueFields."""

    def __init__(self, **field_values):
        """Set field values.

        Args:
            **field_values: Keywords arguments, with names corresponding to the
                trace_header_fields may be provided where each name is associated with a
                value of the correct type.
        """
        for name, value in field_values:
            if not hasattr(self, name):
                raise TypeError("Unknown attribute {!r}".format(name))
            fld = getattr(self, name)
            fld.value = value