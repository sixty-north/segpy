from collections import OrderedDict
from segpy.field import field, BinaryFormat, binary_format
from segpy.types import Int16, Int32
from segpy.util import pairwise


class TraceHeader(object,
                  #metaclass=NamedDescriptorResolver
                 ):

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


class TraceHeaderFormat(metaclass=binary_format(traceheader)):

    pass



def size_of(t):
    return t.SIZE


def compile_struct(record, num_bytes):
    """Compile a struct description from a record.

    Args:
        record: A record containing Field descriptors from which ftype and offset attributes can be obtained.

        num_bytes: The total number of bytes to be retrieved.
    """
    descriptors = (descriptor for descriptor in record.__class__.__dict__.values() if isinstance(descriptor, Field))

    # Sort those descriptors where offset is not None
    sorted_descriptors = sorted(descriptor for descriptor in descriptors if descriptor.offset is not None)

    # Check for overlaps
    for a, b in pairwise(sorted_descriptors):
        if a.offset + size_of(a.ftype) > b.offset:
            raise ValueError("Record fields {!r} at offset {} and {!r} at offset {} are distinct but overlap."
                             .format(a.name, a.offset, b.name, b.offset))

    # Invert the mapping to give offset -> [fields]
    # Check that the types are the same
    offset_to_field = OrderedDict()
    for descriptor in descriptors:
        if descriptor.offset not in offset_to_field:
            offset_to_field[descriptor.offset] = []
        if len(offset_to_field) > 0:
            if offset_to_field[0].ftype is not descriptor.ftype:
                raise ValueError("Coincident fields {!r} and {!r} at offset {} have different types {!r} and {!r}"
                                 .format(offset_to_field[0], descriptor, descriptor.offset, offset_to_field[0].ftype,
                                         descriptor.ftype ))
        offset_to_field[descriptor.offset].append(descriptor)

    range_to_field = OrderedDict()
    for fields in offset_to_field.values():
        field = fields[0]
        range_to_field[range(field.offset, field.offset+size_of(field.ftype))] = fields


