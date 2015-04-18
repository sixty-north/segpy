
from collections import OrderedDict
import textwrap
from weakref import WeakKeyDictionary
from segpy.docstring import docstring_property
from segpy.types import Int32, Int16

from segpy.util import underscores_to_camelcase, first_sentence


def is_magic_name(name):
    return len(name) > 4 and name.startswith('__') and name.endswith('__')


class FormatMeta(type):
    """A metaclass for header format classes.
    """

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace):

        # TODO: This is a good point to validate that the fields are in order and that the
        # TODO: format specification is valid.  We shouldn't even build the class otherwise.

        namespace['ORDERED_FIELD_NAMES'] = tuple(name for name in namespace.keys()
                                                if not is_magic_name(name))

        for name, attr in namespace.items():

            # This shenanigans is necessary so we can have all the following work is a useful way
            # help(class), help(instance), help(class.property) and help(instance.property)

            # Set the _name attribute of the field instance if it hasn't already been set
            if isinstance(attr, NamedField):
                if attr._name is None:
                    attr._name = name

            # We rename the *class* and set its docstring so help() works usefully
            # when called with a class containing such fields.
            attr_class = attr.__class__
            if issubclass(attr_class, NamedField) and attr_class is not NamedField:
                attr_class.__name__ = underscores_to_camelcase(name)
                attr_class.__doc__ = attr.documentation

        return super().__new__(mcs, name, bases, namespace)


class NamedField:
    """Instances of NamedField can be detected by the NamedDescriptorResolver metaclass."""

    def __init__(self, value_type, offset, default, documentation):
        self._name = None  # Set later by the metaclass
        self._value_type = value_type
        self._offset = offset
        self._default = self._value_type(default)
        self._documentation = documentation

    @property
    def name(self):
        "The field name."
        return self._name

    @property
    def value_type(self):
        "The field value type (e.g. Int32)"
        return self._value_type

    @property
    def offset(self):
        "The offset it bytes from the beginning of the header."
        return self._offset

    @property
    def default(self):
        "The default value of the field. Must be convertible to value_type."
        return self._default

    @property
    def documentation(self):
        "A descriptive text string."
        return self._documentation

    @docstring_property(__doc__)
    def __doc__(self):
        return first_sentence(self._documentation)

    def __repr__(self):
        return first_sentence(self._documentation)


def field(value_type, offset, default, documentation):
    """
    Args:
        value_type: The type of the field (e.g. Int32)

        offset: The offset in bytes for this field from the start of the header.

        default: The default value for this field.

        documentation: A docstring for the field. The first sentence should be usable
            as a brief description.

    Returns:
        An instance of a subclass of NamedField class.
    """

    # Create a class specifically for this field. This class will later get
    # renamed when the NamedDescriptorMangler metaclass does its job, to
    # a class name based on the field name.

    class SpecificField(NamedField):
        pass

    return SpecificField(value_type, offset, default, documentation)


class TraceHeaderFormat(metaclass=FormatMeta):

    line_sequence_num = field(
        Int32, offset=1, default=0, documentation=
        "Trace sequence number within line — Numbers continue to increase if the same line "
        "continues across multiple SEG Y files. Highly recommended for all types of data.")

    file_sequence_num = field(
        Int32, offset=5, default=0, documentation=
        "Trace sequence number within SEG Y file — Each file starts with trace sequence one.")

    field_record_num = field(
        Int32, offset=9, default=0, documentation=
        "Original field record number. Highly recommended for all types of data.")

    trace_num = field(
        Int32, offset=13, default=0, documentation=
        "Trace number within the original field record. Highly recommended for all types of data.")

    energy_source_point_num = field(
        Int32, offset=17, default=0, documentation=
        "Energy source point number — Used when more than one record occurs at the same "
        "effective surface location. It is recommended that the new entry defined in Trace "
        "Header bytes 197-202 be used for shotpoint number.")

    ensemble_num = field(
        Int32, offset=21, default=0, documentation=
        "Ensemble number (i.e. CDP , CMP , CRP , etc)")

    ensemble_trace_num = field(
        Int32, offset=25, default=0, documentation=
        "Trace number within the ensemble — Each ensemble starts with trace number one.")

    trace_identification_code = field(
        Int16, offset=29, default=0, documentation=
        "Trace identification code")

    num_vertically_summed_traces = field(
        Int16, offset=31, default=1, documentation=
        "Number of vertically summed traces yielding this trace. (1 is one trace, 2 is two summed traces, etc.)")

    num_horizontally_stacked_traces = field(
        Int16, offset=33, default=1, documentation=
        "Number of horizontally stacked traces yielding this trace. (1 is one trace, 2 is two stacked traces, etc.)")

    data_use = field(
        Int16, offset=35, default=1, documentation=
        "Data use: 1 = Production, 2 = Test")

    source_receiver_offset = field(
        Int32, offset=37, default=0, documentation=
        "Distance from center of the source point to the center of the receiver group (negative if opposite to "
        "direction in which line is shot).")

    receiver_group_elevation = field(
        Int32, offset=41, default=0, documentation=
        "Receiver group elevation (all elevations above the Vertical datum are positive and below are negative). The "
        "elevation_scalar applies to this value.")

    surface_elevation_at_source = field(
        Int32, offset=45, default=0, documentation=
        "Surface elevation at source. The elevation_scalar applies to this value.")

    source_depth_below_surface = field(
        Int32, offset=49, default=0, documentation=
        "Source depth below surface (a positive number). The elevation_scalar applies to this value.")

    datum_elevation_at_receiver_group = field(
        Int32, offset=53, default=0, documentation=
        "Source depth below surface (a positive number). The elevation_scalar applies to this value.")

    datum_elevation_at_source = field(
        Int32, offset=57, default=0, documentation=
        "Datum elevation at source. The elevation_scalar applies to this value.")

    water_depth_at_source = field(
        Int32, offset=61, default=0, documentation=
        "Water depth at source. The elevation_scalar applies to this value.")

    water_depth_at_group = field(
        Int32, offset=65, default=0, documentation=
        "Water depth at group. The elevation_scalar applies to this value."
    )

    elevation_scalar = field(
        Int16, offset=69, default=1, documentation=
        "Scalar to be applied to the elevations and depths specified in: receiver_group_elevation, "
        "surface_elevation_at_source, source_depth_below_surface, datum_elevation_at_receiver_group, "
        "datum_elevation_at_source, water_depth_at_source and water_depth_at_group, to give the real value. "
        "Scalar = 1, +10, +100, +1000, or +10,000. If positive, scalar is used as a multiplier; if negative, scalar is "
        "used as a divisor."
    )

    xy_scalar = field(
        Int16, offset=71, default=1, documentation=
        "Scalar to be applied to all coordinates specified in source_x, source_y, group_x, group_y, cdp_x and cdp_y to "
        "give the real value. Scalar = 1, +10, +100, +1000, or +10,000. If positive, scalar is used as a multiplier; "
        "if negative, scalar is used as divisor."
    )

    source_x = field(
        Int32, offset=73, default=0, documentation=
        "Source coordinate - X. The xy_scalar applies to this value. The coordinate reference system should be "
        "identified through an extended header Location Data stanza. If the coordinate units are in seconds of arc, "
        "decimal degrees or DMS, the X values represent longitude. A positive value designates east of Greenwich "
        "Meridian and a negative value designates west."
    )

    source_y = field(
        Int32, offset=77, default=0, documentation=
        "Source coordinate - Y. The xy_scalar applies to this value. The coordinate reference system should be "
        "identified through an extended header Location Data stanza. If the coordinate units are in seconds of arc, "
        "decimal degrees or DMS, the Y values represent latitude. A positive value designates north of the equator and "
        "a negative value designates south."
    )

    group_x = field(
        Int32, offset=73, default=0, documentation=
        "Group coordinate - X. The xy_scalar applies to this value. The coordinate reference system should be "
        "identified through an extended header Location Data stanza. If the coordinate units are in seconds of arc, "
        "decimal degrees or DMS, the X values represent longitude. A positive value designates east of Greenwich "
        "Meridian and a negative value designates west."
    )

    group_y = field(
        Int32, offset=77, default=0, documentation=
        "Source coordinate - Y. The xy_scalar applies to this value. The coordinate reference system should be "
        "identified through an extended header Location Data stanza. If the coordinate units are in seconds of arc, "
        "decimal degrees or DMS, the Y values represent latitude. A positive value designates north of the equator and "
        "a negative value designates south."
    )

    coordinate_units = field(
        Int16, offset=89, default=0, documentation=
        "Coordinate units: 1 = Length (meters or feet), 2 = Seconds of arc, 3 = Decimal degrees, 4 = Degrees, minutes, "
        "seconds (DMS). Note: To encode ±DDDMMSS bytes this value equals ±DDD*104 + MM*102 + SS with xy_scalar set to "
        "1; To encode ±DDDMMSS.ss this value equals ±DDD*106 + MM*104 + SS*102 with xy_scalar set to -100."
    )

    weathering_velocity = field(
        Int16, offset=91, default=0, documentation=
        "Weathering velocity. (ft/s or m/s as specified in Binary File Header bytes 3255- 3256)"  # TODO
    )

    subweathering_velocity = field(
        Int16, offset=93, default=0, documentation=
        "Subweathering velocity. (ft/s or m/s as specified in Binary File Header bytes 3255-3256)"  # TODO
    )

    uphole_time_at_source = field(
        Int16, offset=95, default=0, documentation=
        "Uphole time at source in milliseconds. The time_scalar applies to this value."
    )

    uphole_time_at_group = field(
        Int16, offset=97, default=0, documentation=
        "Uphole time at group in milliseconds. The time_scalar applies to this value."
    )

    source_static_correction = field(
        Int16, offset=99, default=0, documentation=
        "Source static correction in milliseconds. The time_scalar applies to this value."
    )

    group_static_correction = field(
        Int16, offset=101, default=0, documentation=
        "Group static correction in milliseconds. The time_scalar applies to this value."
    )


class ValueField:

    def __init__(self, name, value_type, default, documentation):
        self._name = name
        self._value_type = value_type
        self._default = default
        self._documentation = documentation
        self._instance_data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if owner is None:
            return self
        if instance not in self._instance_data:
            return self._default
        return self._instance_data[instance]

    def __set__(self, instance, value):
        try:
            self._instance_data[instance] = self._value_type(value)
        except ValueError as e:
            raise ValueError("Assigned value {!r} for {} attribute must be convertible to {}: {}"
                             .format(value, self._name, self._value_type.__name__, e)) from e

    def __delete__(self, instance):
        raise AttributeError("Can't delete {} attribute".format(self._name))

    @docstring_property(__doc__)
    def __doc__(self):
        return self._documentation

    # TODO: Get documentation of these descriptors working correctly


class BuildFromFormat(type):
    """A metaclass for building a data transfer object from a format definition."""

    def __new__(mcs, name, bases, namespace, format_class):
        """Create a new DTO class from a format class."""
        if not format_class.__class__ is FormatMeta:
            raise TypeError("Format class {} specified for class {} does not use the FormatMeta metaclass"
                            .format(format_class.__name__, name))

        for name in format_class.ORDERED_FIELD_NAMES:
            format_field = getattr(format_class, name)
            namespace[name] = ValueField(name=name,
                                         value_type=format_field.value_type,
                                         default=format_field.default,
                                         documentation=format_field.documentation)

        return super().__new__(mcs, name, bases, namespace)

    def __init__(mcs, name, bases, namespace, format_class):
        super().__init__(mcs, name, bases)
        pass


class TraceHeader(metaclass=BuildFromFormat, format_class=TraceHeaderFormat):
    pass

# This would build the TraceHeader class from something like the original TraceHeader at the bottom of this file.


#
#
# def size_of(t):
#     return t.SIZE
#
#
# def compile_struct(record, num_bytes):
#     """Compile a struct description from a record.
#
#     Args:
#         record: A record containing Field descriptors from which ftype and offset attributes can be obtained.
#
#         num_bytes: The total number of bytes to be retrieved.
#     """
#     descriptors = (descriptor for descriptor in record.__class__.__dict__.values() if isinstance(descriptor, Field))
#
#     # Sort those descriptors where offset is not None
#     sorted_descriptors = sorted(descriptor for descriptor in descriptors if descriptor.offset is not None)
#
#     # Check for overlaps
#     for a, b in pairwise(sorted_descriptors):
#         if a.offset + size_of(a.ftype) > b.offset:
#             raise ValueError("Record fields {!r} at offset {} and {!r} at offset {} are distinct but overlap."
#                              .format(a.name, a.offset, b.name, b.offset))
#
#     # Invert the mapping to give offset -> [fields]
#     # Check that the types are the same
#     offset_to_field = OrderedDict()
#     for descriptor in descriptors:
#         if descriptor.offset not in offset_to_field:
#             offset_to_field[descriptor.offset] = []
#         if len(offset_to_field) > 0:
#             if offset_to_field[0].ftype is not descriptor.ftype:
#                 raise ValueError("Coincident fields {!r} and {!r} at offset {} have different types {!r} and {!r}"
#                                  .format(offset_to_field[0], descriptor, descriptor.offset, offset_to_field[0].ftype,
#                                          descriptor.ftype ))
#         offset_to_field[descriptor.offset].append(descriptor)
#
#     range_to_field = OrderedDict()
#     for fields in offset_to_field.values():
#         field = fields[0]
#         range_to_field[range(field.offset, field.offset+size_of(field.ftype))] = fields


