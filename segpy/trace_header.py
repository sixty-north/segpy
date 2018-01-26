from enum import IntEnum

from segpy.header import field, Header
from segpy.field_types import IntEnumFieldMeta, IntFieldMeta, Int32, Int16, NNInt16, NNInt32


class DataUse(IntEnum):
    """Data use:
    1 = Production,
    2 = Test"""
    PRODUCTION = 1
    TEST = 2


class DataUseField(metaclass=IntEnumFieldMeta,
                   enum=DataUse):
    pass


class ScalarFactor(IntEnum):
    """Scalar to be applied to other fields.

    See specific fields (i.e. use of this class) to see the specific fields to
    which scalars are applied.

    Scalar = 1, +10, +100, +1000, or +10,000. If positive, scalar is used as a
    multiplier; if negative, scalar is used as a divisor.
    """
    UNKNOWN = 0
    POS_1 = 1
    POS_10 = 10
    POS_100 = 100
    POS_1000 = 1000
    POS_10000 = 10000
    NEG_1 = -1
    NEG_10 = -10
    NEG_100 = -100
    NEG_1000 = -1000
    NEG_10000 = -10000


class ScalarFactorField(metaclass=IntEnumFieldMeta,
                        enum=ScalarFactor):
    pass


class CoordinateUnits(IntEnum):
    """Coordinate units: 1 = Length (meters or feet), 2 = Seconds of arc, 3 =
    Decimal degrees, 4 = Degrees, minutes, seconds (DMS). Note: To encode
    ±DDDMMSS bytes this value equals ±DDD*104 + MM*102 + SS with xy_scalar set
    to 1; To encode ±DDDMMSS.ss this value equals ±DDD*106 + MM*104 + SS*102
    with xy_scalar set to -100.
    """
    UNKNOWN = 0
    LENGTH = 1
    SECONDS_OF_ARC = 2
    DECIMAL_DEGREES = 3
    DMS = 4


class CoordinateUnitsField(metaclass=IntEnumFieldMeta,
                           enum=CoordinateUnits):
    pass


class Correlated(IntEnum):
    "Correlated: 1 = no, 2 = yes."
    NO = 1
    YES = 2


class CorrelatedField(metaclass=IntEnumFieldMeta,
                      enum=Correlated):
    pass


class SweepType(IntEnum):
    """Sweep type:
    1 = linear,
    2 = parabolic,
    3 = exponential
    4 = other.
    """
    UNKNOWN = 0
    LINEAR = 1
    PARABOLIC = 2
    EXPONENTIAL = 3
    OTHER = 4


class SweepTypeField(metaclass=IntEnumFieldMeta,
                     enum=SweepType):
    pass


class TaperType(IntEnum):
    """Taper type:
    1 = linear,
    2 = cos2,
    3 = other
    """
    UNKNOWN = 0
    LINEAR = 1
    COS_SQUARED = 2
    OTHER = 3


class TaperTypeField(metaclass=IntEnumFieldMeta,
                     enum=TaperType):
    pass


class DayOfYearField(metaclass=IntFieldMeta,
                     seg_y_type='int16',
                     min_value=0, max_value=366):
    """Day of year. (Julian day for GMT and UTC time basis).

    Value range based on:
    https://seg.org/Portals/0/SEG/News%20and%20Resources/Technical%20Standards/seg_y_rev2_0-mar2017.pdf
    """
    pass


class HourOfDayField(metaclass=IntFieldMeta,
                     seg_y_type='int16',
                     min_value=0, max_value=24):
    "Hour of day. (24 hour clock)."
    pass


class MinuteOfHourField(metaclass=IntFieldMeta,
                        seg_y_type='int16',
                        min_value=0, max_value=60):
    "Minute of hour."
    pass


class SecondOfMinute(metaclass=IntFieldMeta,
                     seg_y_type='int16',
                     min_value=0, max_value=60):
    "Second of minutes."
    pass


class TimeBasisCode(IntEnum):
    """Time basis code. 1 = Local, 2 = GMT (Greenwich Mean Time), 3 = Other, should
    be explained in a user defined stanza in the Extended Textual File Header,
    4 = UTC (Coordinated Universal Time).
    """
    UNKNOWN = 0
    LOCAL = 1
    GMT = 2
    OTHER = 3
    UTC = 4


class TimeBasisCodeField(metaclass=IntEnumFieldMeta,
                         enum=TimeBasisCode):
    pass


class OverTravel(IntEnum):
    """Over travel associated with taper at beginning or end of line.
    1 = down (or behind)
    2 = up (or ahead)
    """
    UNKNOWN = 0
    DOWN = 1
    UP = 2


class OverTravelField(metaclass=IntEnumFieldMeta,
                      enum=OverTravel):
    pass


class SampleUnit(IntEnum):
    """-1 = Other (should be described in Data Sample Measurement Units Stanza)
    0 = Unknown,
    1 = Pascal (Pa),
    2 = Volts (v),
    3 = Millivolts (mV),
    4 = Amperes (A),
    5 = Meters (m),
    6 = Meters per second (m/s),
    7 = Meters per second squared (m/s^2),
    8 = Newton (N),
    9 = Watt (W)
    """
    OTHER = -1
    UNKNOWN = 0
    PASCAL = 1
    VOLTS = 2
    MILLIVOLTS = 3
    AMPERES = 4
    METERS = 5
    METERS_PER_SECOND = 6
    METERS_PER_SECOND_SQUARED = 7
    NEWTON = 8
    WATT = 9


class SampleUnitField(metaclass=IntEnumFieldMeta,
                      enum=SampleUnit):
    pass


class SourceTypeField(metaclass=IntFieldMeta,
                      seg_y_type='int16',
                      max_value=9):
    """Source Type/Orientation — Defines the type and the orientation of the energy source. The terms vertical,
    cross-line and in-line refer to the three axes of an orthogonal coordinate system. The absolute azimuthal
    orientation of the coordinate system axes can be defined in the Bin Grid Definition Stanza.
    -1 to -n = Other (should be described in Source Type/Orientation stanza),
    0 = Unknown,
    1 = Vibratory - Vertical orientation,
    2 = Vibratory - Cross-line orientation,
    3 = Vibratory - In-line orientation,
    4 = Impulsive - Vertical orientation,
    5 = Impulsive - Cross-line orientation,
    6 = Impulsive - In-line orientation,
    7 = Distributed Impulsive - Vertical orientation,
    8 = Distributed Impulsive - Cross-line orientation,
    9 = Distributed Impulsive - In-line orientation"""
    pass


class SourceMeasurementUnit(IntEnum):
    """Source Measurement Unit. The unit used for the source measurement.

    -1 = Other (should be described in Source Measurement Unit stanza),
    0 = Unknown,
    1 = Joule (J),
    2 = Kilowatt (kW),
    3 = Pascal (Pa),
    4 = Bar (Bar),
    4 = Bar-meter (Bar-m),
    5 = Newton (N),
    6 = Kilograms (kg)
    """
    OTHER = -1
    UNKNOWN = 0
    JOULE = 1
    KILOWATT = 2
    PASCAL = 3
    BAR = 4
    BAR_METER = 4
    NEWTON = 5
    KILOGRAMS = 6


class SourceMeasurementUnitField(metaclass=IntEnumFieldMeta,
                                 enum=SourceMeasurementUnit):
    pass


class TraceHeaderRev0(Header):

    START_OFFSET_IN_BYTES = 1
    LENGTH_IN_BYTES = 240

    line_sequence_num = field(
        Int32, offset=1, default=0, documentation=
        """Trace sequence number within line — Numbers continue to increase if the same
        line continues across multiple SEG Y files. Highly recommended for all
        types of data. [Usually starts at one for each reel.]""")

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
        """Energy source point number — Used when more than one record occurs at the
        same effective surface location. It is recommended that the new entry
        defined in Trace Header bytes 197-202 be used for shotpoint number.""")

    ensemble_num = field(
        Int32, offset=21, default=0, documentation=
        "Ensemble number (i.e. CDP , CMP , CRP , etc)")

    ensemble_trace_num = field(
        NNInt32, offset=25, default=0, documentation=
        "Trace number within the ensemble — Each ensemble starts with trace number one.")

    trace_identification_code = field(
        Int16, offset=29, default=0, documentation=
        "Trace identification code")

    num_vertically_summed_traces = field(
        NNInt16, offset=31, default=1, documentation=
        "Number of vertically summed traces yielding this trace. (1 is one trace, 2 is two summed traces, etc.)")

    num_horizontally_stacked_traces = field(
        NNInt16, offset=33, default=1, documentation=
        "Number of horizontally stacked traces yielding this trace. (1 is one trace, 2 is two stacked traces, etc.)")

    data_use = field(
        DataUseField, offset=35, default=1,
        documentation=DataUse.__doc__)

    doc_nreceiver_offset = field(
        Int32, offset=37, default=0, documentation=
        """Distance from center of the source point to the center of the receiver group
        (negative if opposite to direction in which line is shot).""")

    receiver_group_elevation = field(
        Int32, offset=41, default=0, documentation=
        """Receiver group elevation (all elevations above the Vertical datum are
        positive and below are negative). The elevation_scalar applies to this
        value.""")

    surface_elevation_at_source = field(
        Int32, offset=45, default=0, documentation=
        "Surface elevation at source. The elevation_scalar applies to this value.")

    source_depth_below_surface = field(
        NNInt32, offset=49, default=0, documentation=
        "Source depth below surface (a positive number). The elevation_scalar applies to this value.")

    datum_elevation_at_receiver_group = field(
        NNInt32, offset=53, default=0, documentation=
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
        ScalarFactorField, offset=69, default=ScalarFactor.POS_1,
        documentation=
        """Scalar to be applied to the elevations and depths specified in:
        receiver_group_elevation, surface_elevation_at_source,
        source_depth_below_surface, datum_elevation_at_receiver_group,
        datum_elevation_at_source, water_depth_at_source and
        water_depth_at_group, to give the real value. Scalar = 1, +10, +100,
        +1000, or +10,000. If positive, scalar is used as a multiplier; if
        negative, scalar is used as a divisor."""
    )

    xy_scalar = field(
        ScalarFactorField, offset=71, default=ScalarFactor.POS_1, documentation=
        """Scalar to be applied to all coordinates specified in source_x, source_y,
        group_x, group_y, cdp_x and cdp_y to give the real value. Scalar = 1,
        +10, +100, +1000, or +10,000. If positive, scalar is used as a
        multiplier; if negative, scalar is used as divisor."""
    )

    source_x = field(
        Int32, offset=73, default=0, documentation=
        """Source coordinate - X. The xy_scalar applies to this value. The coordinate
        reference system should be identified through an extended header
        Location Data stanza. If the coordinate units are in seconds of arc,
        decimal degrees or DMS, the X values represent longitude. A positive
        value designates east of Greenwich Meridian and a negative value
        designates west."""
    )

    source_y = field(
        Int32, offset=77, default=0, documentation=
        """Source coordinate - Y. The xy_scalar applies to this value. The coordinate
        reference system should be identified through an extended header
        Location Data stanza. If the coordinate units are in seconds of arc,
        decimal degrees or DMS, the Y values represent latitude. A positive
        value designates north of the equator and a negative value designates
        south."""
    )

    group_x = field(
        Int32, offset=81, default=0, documentation=
        """Group coordinate - X. The xy_scalar applies to this value. The coordinate
        reference system should be identified through an extended header
        Location Data stanza. If the coordinate units are in seconds of arc,
        decimal degrees or DMS, the X values represent longitude. A positive
        value designates east of Greenwich Meridian and a negative value
        designates west."""
    )

    group_y = field(
        Int32, offset=85, default=0, documentation=
        """Source coordinate - Y. The xy_scalar applies to this value. The coordinate
        reference system should be identified through an extended header
        Location Data stanza. If the coordinate units are in seconds of arc,
        decimal degrees or DMS, the Y values represent latitude. A positive
        value designates north of the equator and a negative value designates
        south."""
    )

    coordinate_units = field(
        CoordinateUnitsField, offset=89, default=0,
        documentation=CoordinateUnits.__doc__
    )

    weathering_velocity = field(
        NNInt16, offset=91, default=0, documentation=
        "Weathering velocity. (ft/s or m/s as specified in Binary File Header bytes 3255- 3256)"  # TODO
    )

    subweathering_velocity = field(
        NNInt16, offset=93, default=0, documentation=
        "Subweathering velocity. (ft/s or m/s as specified in Binary File Header bytes 3255-3256)"  # TODO
    )

    uphole_time_at_source = field(
        NNInt16, offset=95, default=0, documentation=
        "Uphole time at source in milliseconds. The time_scalar applies to this value."
    )

    uphole_time_at_group = field(
        NNInt16, offset=97, default=0, documentation=
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

    total_static = field(
        Int16, offset=103, default=0, documentation=
        """Total static applied in milliseconds. (Zero if no static has been applied).
        The time_scalar applies to this value."""
    )

    lag_time_a = field(
        Int16, offset=105, default=0, documentation=
        """Lag time A. Time in milliseconds between end of 240-byte trace
        identification header and time break. The value is positive if time
        break occurs after the end of header; negative if time break occurs
        before the end of header. Time break is defined as the initiation pulse
        that may be recorded on an auxiliary trace or as otherwise specified by
        the recording system. The time_scalar applies to this value."""
    )

    lag_time_b = field(
        Int16, offset=107, default=0, documentation=
        """Lag Time B. Time in milliseconds between time break and the initiation time
        of the energy source. May be positive or negative. The time_scalar
        applies to this value."""
    )

    delay_recording_time = field(
        Int16, offset=109, default=0, documentation=
        """Delay recording time — Time in milliseconds between initiation time of
        energy source and the time when recording of data samples begins. In
        SEG Y rev 0 this entry was intended for deep-water work if data
        recording does not start at zero time. The entry can be negative to
        accommodate negative start times (i.e. data recorded before time zero,
        presumably as a result of static application to the data trace). If a
        non-zero value (negative or positive) is recorded in this entry, a
        comment to that effect should appear in the Textual File Header. The
        time_scalar applies to this value."""
    )

    mute_start_time = field(
        NNInt16, offset=111, default=0, documentation=
        "Mute time — Start time in milliseconds. The time_scalar applies to this value."
    )

    mute_end_time = field(
        NNInt16, offset=113, default=0, documentation=
        "Mute time — End time in milliseconds.  The time_scalar applies to this value."
    )

    num_samples = field(
        NNInt16, offset=115, default=0, documentation=
        "Number of samples in this trace. Highly recommended for all types of data."
    )

    sample_interval = field(
        Int16, offset=117, default=0, documentation=
        """Sample interval in microseconds (μs) for this trace. The number of bytes in
        a trace record must be consistent with the number of samples written in
        the trace header. This is important for all recording media; but it is
        particularly crucial for the correct processing of SEG Y data in disk
        files (see Appendix C). If the fixed length trace flag in bytes
        3503-3504 of the Binary File Header is set, the sample interval and
        #TODO: field names instead of byte offsets number of samples in every
        trace in the SEG Y file must be the same as the values recorded in the
        Binary File Header. If the fixed length trace flag is not set, the
        sample interval and number of samples may vary from trace to trace.
        Highly recommended for all types of data."""
    )

    gain_type_of_field_instruments = field(
        NNInt16, offset=119, default=0, documentation=
        "Gain type of field instruments. 1 = fixed, 2 = binary, 3 = floating point, 4 ... N = optional use."
    )

    instrument_gain_constant = field(
        Int16, offset=121, default=0, documentation=
        "Instrument gain constant (dB)."
    )

    instrument_initial_gain = field(
        Int16, offset=123, default=0, documentation=
        "Instrument early or initial gain (dB)."
    )

    correlated = field(
        CorrelatedField, offset=125, default=1,
        documentation=Correlated.__doc__
    )

    sweep_frequency_at_start = field(
        NNInt16, offset=127, default=0, documentation=
        "Sweep frequency at start (Hz)."
    )

    sweep_frequency_at_end = field(
        NNInt16, offset=129, default=0, documentation=
        "Sweep frequency at end (Hz)."
    )

    sweep_length = field(
        NNInt16, offset=131, default=0, documentation=
        "Sweep length in milliseconds."
    )

    sweep_type = field(
        SweepTypeField, offset=133, default=0,
        documentation=SweepType.__doc__
    )

    sweep_trace_taper_length_at_start = field(
        NNInt16, offset=135, default=0, documentation=
        "Sweep trace taper length at start in milliseconds."
    )

    sweep_trace_taper_length_at_end = field(
        NNInt16, offset=137, default=0, documentation=
        "Sweep trace taper length at end in milliseconds."
    )

    taper_type = field(
        TaperTypeField, offset=139, default=0,
        documentation=TaperType.__doc__
    )

    alias_filter_frequency = field(
        NNInt16, offset=141, default=0, documentation=
        "Alias filter frequency (Hz), if used."
    )

    alias_filter_slope = field(
        Int16, offset=143, default=0, documentation=
        "Alias filter slope (dB/octave)."
    )

    notch_filter_frequency = field(
        NNInt16, offset=145, default=0, documentation=
        "Notch filter frequency (Hz), if used."
    )

    notch_filter_slope = field(
        Int16, offset=147, default=0, documentation=
        "Notch filter slope (dB/octave)."
    )

    low_cut_frequency = field(
        NNInt16, offset=149, default=0, documentation=
        "Low-cut frequency (Hz), if used."
    )

    high_cut_frequency = field(
        NNInt16, offset=151, default=0, documentation=
        "High-cut frequency (Hz), if used."
    )

    low_cut_slope = field(
        Int16, offset=153, default=0, documentation=
        "Low-cut slope (dB/octave)."
    )

    high_cut_slope = field(
        Int16, offset=155, default=0, documentation=
        "High-cut slope (dB/octave)."
    )

    year_recorded = field(
        Int16, offset=157, default=0, documentation=
        """Year data recorded. The 1975 standard is unclear as to whether this should
        be recorded as a 2-digit or a 4-digit year and both have been used. For
        SEG Y revisions beyond rev 0, the year should be recorded as the
        complete 4-digit Gregorian calendar year (i.e. the year 2001 should be
        recorded as 2001 in base 10 (7D1 in base16))."""
    )

    day_of_year = field(
        DayOfYearField, offset=159, default=0,
        documentation=DayOfYearField.__doc__
    )

    hour_of_day = field(
        HourOfDayField, offset=161, default=0,
        documentation=HourOfDayField.__doc__
    )

    minute_of_hour = field(
        MinuteOfHourField, offset=163, default=0,
        documentation=MinuteOfHourField.__doc__
    )

    second_of_minute = field(
        SecondOfMinute, offset=165, default=0,
        documentation=SecondOfMinute.__doc__
    )

    time_basis_code = field(
        TimeBasisCodeField, offset=167, default=0,
        documentation=TimeBasisCode.__doc__
    )

    trace_weighting_factor = field(
        NNInt16, offset=169, default=0, documentation=
        "Trace weighting factor. Defined as 2**-N volts for the least significant bit. (N = 0, 1, ..., 32767)."
    )

    geophone_group_num_roll_switch_position_one = field(
        Int16, offset=171, default=0, documentation=
        "Geophone group number of roll switch position one."
    )

    geophone_group_num_first_trace_original_field = field(
        Int16, offset=173, default=0, documentation=
        "Geophone group number of trace number one within original field record."
    )

    geophone_group_num_last_trace_original_field = field(
        Int16, offset=175, default=0, documentation=
        "Geophone group number of last trace within original field record."
    )

    gap_size = field(
        NNInt16, offset=177, default=0, documentation=
        "Gap size. (Total number of groups dropped)."
    )

    over_travel = field(
        OverTravelField, offset=179, default=0,
        documentation=OverTravel.__doc__
    )


class TraceHeaderRev1(TraceHeaderRev0):

    cdp_x = field(
        Int32, offset=181, default=0, documentation=
        """X coordinate of ensemble (CDP) position of this trace. The coordinate
        reference system should be identified through an extended header
        Location Data stanza. The xy_scalar field applies to this value."""
    )

    cdp_y = field(
        Int32, offset=185, default=0, documentation=
        """Y coordinate of ensemble (CDP) position of this trace. The coordinate
        reference system should be identified through an extended header
        Location Data stanza. The xy_scalar field applies to this value."""
    )

    inline_number = field(
        Int32, offset=189, default=0, documentation=
        """In-line number for 3-D poststack data. If one in-line per SEG Y file is
        being recorded, this value should be the same for all traces in the
        file and the same value will be recorded in bytes 3205-3208 of the
        Binary File Header."""  # TODO: replace bytes with field name
    )

    crossline_number = field(
        Int32, offset=193, default=0, documentation=
        """Cross-line number for 3-D poststack data. This will typically be the same
        value as the ensemble (CDP) number in Trace Header ensemble_num field,
        but this does not have to be the case."""
    )

    shotpoint_number = field(
        Int32, offset=197, default=0, documentation=
        """Shotpoint number. This is probably only applicable to 2-D poststack data.
        Note that it is assumed that the shotpoint number refers to the source
        location nearest to the ensemble (CDP) location for a particular trace.
        If this is not the case, there should be a comment in the Textual File
        Header explaining what the shotpoint number actually refers to."""
    )

    shotpoint_scalar = field(
        Int16, offset=201, default=0, documentation=
        """Scalar to be applied to the shotpoint number in trace header field
        shotpoint_number to give the real value. If positive, scalar is used as
        a multiplier; if negative as a divisor; if zero the shotpoint number is
        not scaled (i.e. it is an integer. A typical value will be -10,
        allowing shotpoint numbers with one decimal digit to the right of the
        decimal point)."""
    )

    trace_unit = field(
        SampleUnitField, offset=203, default=0,
        documentation="Trace value measurement unit:\n{}".format(SampleUnit.__doc__)
    )

    transduction_constant_mantissa = field(
        Int32, offset=205, default=0, documentation=
        """Transduction Constant mantissa. The mantissa of the multiplicative constant
        used to convert the Data Trace samples to the Transduction Units
        (specified in Trace Header transduction_units field). The mantissa of
        the constant is encoded as a four-byte, two's complement integer. The
        constant value is given by transduction_constant_mantissa *
        10**transduction_constant_exponent."""
    )

    transduction_constant_exponent = field(
        Int16, offset=209, default=0, documentation=
        """Transduction Constant exponent. The base 10 exponent of the multiplicative
        constant used to convert the Data Trace samples to the Transduction
        Units (specified in Trace Header transduction_units field). The
        constant value is given by transduction_constant_mantissa *
        10**transduction_constant_exponent."""
    )

    transduction_units = field(
        SampleUnitField, offset=211, default=0, documentation=
        """Transduction Units. The unit of measurement of the Data Trace samples after
        they have been multiplied by the Transduction Constant specified in
        Trace Header fields transduction_constant_mantissa and
        transduction_constant_exponent.\n{}""".format(SampleUnit.__doc__)
    )

    device_trace_identifier = field(
        Int16, offset=213, default=0, documentation=
        """Device/Trace Identifier — The unit number or id number of the device
        associated with the Data Trace (i.e. 4368 for vibrator serial number
        4368 or 20316 for gun 16 on string 3 on vessel 2). This field allows
        traces to be associated across trace ensembles independently of the
        trace number (ensemble_trace_num field)."""
    )

    time_scalar = field(
        ScalarFactorField, offset=215, default=0, documentation=
        """Scalar to be applied to times specified in Trace Header fields
        uphole_time_at_source, uphole_time_at_group, source_static_correction,
        group_static_correction, total_static, lag_time_a, lag_time_b,
        delay_recording_time, mute_start_time, mute_end_time to give the true
        time value in milliseconds. Scalar = 1, +10, +100, +1000, or +10,000.
        If positive, scalar is used as a multiplier; if negative, scalar is
        used as divisor. A value of zero is assumed to be a scalar value of
        1."""
    )

    source_type = field(
        SourceTypeField, offset=217, default=0,
        documentation=SourceTypeField.__doc__
    )

    source_energy_direction = field(
        Int32, offset=219, default=0, documentation=  # TODO: This is six bytes. What is the format?
        """Source Energy Direction with respect to the source orientation. The positive
        orientation direction is defined in Bytes 217-218 of the Trace Header.
        The energy direction is encoded in tenths of degrees (i.e. 347.8° is
        encoded as 3478)."""
    )

    source_measurement_mantissa = field(
        Int32, offset=225, default=0, documentation=
        """Source Measurement mantissa. Describes the source effort used to generate
        the trace. The measurement can be simple, qualitative measurements such
        as the total weight of explosive used or the peak air gun pressure or
        the number of vibrators times the sweep duration. Although these simple
        measurements are acceptable, it is preferable to use true measurement
        units of energy or work. The constant is encoded as a four-byte, two's
        complement integer (source_measurement_mantissa) and a two-byte, two's
        complement integer source_measurement_exponent) which is the power of
        ten exponent (i.e. source_measurement_mantissa *
        10**source_measurement_exponent)."""
    )

    source_measurement_exponent = field(
        Int16, offset=229, default=0, documentation=
        """Source Measurement exponent. Describes the source effort used to generate
        the trace. The measurement can be simple, qualitative measurements such
        as the total weight of explosive used or the peak air gun pressure or
        the number of vibrators times the sweep duration. Although these simple
        measurements are acceptable, it is preferable to use true measurement
        units of energy or work. The constant is encoded as a four-byte, two's
        complement integer (source_measurement_mantissa) and a two-byte, two's
        complement integer source_measurement_exponent) which is the power of
        ten exponent (i.e. source_measurement_mantissa *
        10**source_measurement_exponent)."""
    )

    source_measurement_unit = field(
        SourceMeasurementUnitField, offset=231, default=0,
        documentation=SourceMeasurementUnit.__doc__
    )
