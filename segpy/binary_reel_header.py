from segpy.header import FormatMeta, field
from segpy.types import Int32, Int16


class BinaryReelHeader(metaclass=FormatMeta):

    START_OFFSET_IN_BYTES = 3201
    LENGTH_IN_BYTES = 400

    job_id_num = field(
        Int32, offset=3201, default=0, documentation=
        "Job identification number")

    line_num = field(
        Int32, offset=3205, default=0, documentation=
        "Line number. For 3-D poststack data, this will typically contain the in-line number."
    )

    reel_num = field(
        Int32, offset=3209, default=0, documentation=
        "Reel number."
    )

    data_traces_per_ensemble = field(
        Int16, offset=3213, default=0, documentation=
        "Number of data traces per ensemble. Mandatory for prestack data."
    )

    auxiliary_traces_per_ensemble = field(
        Int16, offset=3215, default=0, documentation=
        "Number of auxiliary traces per ensemble. Mandatory for prestack data."
    )

    sample_interval = field(
        Int16, offset=3217, default=0, documentation=
        "Sample interval in microseconds (μs). Mandatory for all data types."
    )

    original_field_sample_interval = field(
        Int16, offset=3219, default=0, documentation=
        "Sample interval in microseconds (μs) of original field recording."
    )

    num_samples = field(
        Int16, offset=3221, default=0, documentation=
        "Number of samples per data trace. Mandatory for all types of data. "
        "Note: The sample interval and number of samples in the Binary File Header should be for the primary set of "
        "seismic data traces in the file."
    )

    original_field_num_samples = field(
        Int16, offset=3223, default=0, documentation=
        "Number of samples per data trace for original field recording."
    )

    data_sample_format = field(
        Int16, offset=3225, default=5, documentation=
        "Data sample format code. Mandatory for all data. "
        "1 = 4-byte IBM floating-point, "
        "2 = 4-byte, two's complement integer, "
        "3 = 2-byte, two's complement integer, "
        "4 = 4-byte fixed-point with gain (obsolete), "
        "5 = 4-byte IEEE floating-point, "
        "6 = Not currently used, "
        "7 = Not currently used, "
        "8 = 1-byte, two's complement integer."
    )

    ensemble_fold = field(
        Int16, offset=3227, default=0, documentation=
        "Ensemble fold. The expected number of data traces per trace ensemble (e.g. the CMP fold). "
        "Highly recommended for all types of data."
    )

    trace_sorting = field(
        Int16, offset=3229, default=0, documentation=
        "Trace sorting code (i.e. type of ensemble) : "
        "-1 = Other (should be explained in user Extended Textual File Header stanza, "
        "0 = Unknown, "
        "1 = As recorded (no sorting), "
        "2 = CDP ensemble, "
        "3 = Single fold continuous profile 4 = Horizontally stacked, "
        "5 = Common source point, "
        "6 = Common receiver point, "
        "7 = Common offset point, "
        "8 = Common mid-point, "
        "9 = Common conversion point. "
        "Highly recommended for all types of data."
    )

    vertical_sum_code = field(
        Int16, offset=3231, default=0, documentation=
        "Vertical sum code: "
        "1 = no sum, "
        "2 = two sum, "
        "..., "
        "N=M-1 sum (M=2to32,767)."
    )

    sweep_frequency_at_start = field(
        Int16, offset=3233, default=0, documentation=
        "Sweep frequency at start (Hz)."
    )

    sweep_frequency_at_end = field(
        Int16, offset=3235, default=0, documentation=
        "Sweep frequency at end (Hz)."
    )

    sweep_length = field(
        Int16, offset=3237, default=0, documentation=
        "Sweep length in milliseconds."
    )

    sweep_type = field(
        Int16, offset=3239, default=0, documentation=
        "Sweep type: 1 = linear, 2 = parabolic, 3 = exponential 4 = other."
    )

    sweep_trace_number = field(
        Int16, offset=3241, default=0, documentation=
        "Trace number of sweep channel."
    )

    sweep_trace_taper_length_at_start = field(
        Int16, offset=3243, default=0, documentation=
        "Sweep trace taper length at start in milliseconds."
    )

    sweep_trace_taper_length_at_end = field(
        Int16, offset=3245, default=0, documentation=
        "Sweep trace taper length at end in milliseconds."
    )

    taper_type = field(
        Int16, offset=3247, default=0, documentation=
        "Taper type: 1 = linear, 2 = cos2, 3 = other"
    )

    correlated_data_traces = field(
        Int16, offset=3249, default=0, documentation=
        "Correlated data traces: "
        "1 = no, "
        "2 = yes"
    )

    binary_gain_recovered = field(
        Int16, offset=3251, default=0, documentation=
        "Binary gain recovered: "
        "1 = no, "
        "2 = yes"
    )

    amplitude_recovery_method = field(
        Int16, offset=3253, default=0, documentation=
        "Amplitude recovery method: "
        "1 = none, "
        "2 = spherical divergence, "
        "3 = AGC, "
        "4 = other"
    )

    measurement_system = field(
        Int16, offset=3255, default=0, documentation=
        "Measurement system: Highly recommended for all types of data. "
        "If Location Data stanzas are included in the file, this entry must agree with the Location Data stanza. "
        "If there is a disagreement, the last Location Data stanza is the controlling authority. "
        "1 = Meters, "
        "2 = Feet"
    )

    impulse_signal_polarity = field(
        Int16, offset=3257, default=0, documentation=
        "Impulse signal polarity : "
        "1 = Increase in pressure or upward geophone case movement gives negative number on tape, "
        "2 = Increase in pressure or upward geophone case movement gives positive number on tape. "
    )

    vibratory_polarity_code = field(
        Int16, offset=3259, default=0, documentation=
        "Vibratory polarity code: "
        "Seismic signal lags pilot signal by: "
        "1 = 337.5° to 22.5°, "
        "2 = 22.5° to 67.5°, "
        "3 = 67.5° to 112.5°, "
        "4 = 112.5° to 157.5°, "
        "5 = 157.5° to 202.5°, "
        "6 = 202.5°to 247.5°,  "
        "7 = 247.5° to 292.5°, "
        "8 = 292.5° to 337.5°.")

    format_revision_num = field(
        Int16, offset=3501, default=0x100, documentation=
        "SEG Y Format Revision Number. "
        "This is a 16-bit unsigned value with a Q- point between the first and second bytes. "
        "Thus for SEG Y Revision 1.0, as defined in this document, this will be recorded as 010016. This field is "
        "mandatory for all versions of SEG Y, although a value of zero indicates “traditional” SEG Y conforming to "
        "the 1975 standard."
    )

    fixed_length_trace_flag = field(
        Int16, offset=3503, default=0, documentation=
        "Fixed length trace flag. A value of one indicates that all traces in this SEG Y file are guaranteed to have "
        "the same sample interval and number of samples, as specified in Textual File Header bytes 3217-3218 and "
        "3221-3222. A value of zero indicates that the length of the traces in the file may vary and the number of "
        "samples in bytes 115-116 of the Trace Header must be examined to determine the actual length of each trace. "
        "This field is mandatory for all versions of SEG Y, although a value of zero indicates “traditional” SEG Y "
        "conforming to the 1975 standard."
    )

    num_extended_textual_headers = field(
        Int16, offset=3505, default=0, documentation=
        "Number of 3200-byte, Extended Textual File Header records following the Binary Header. "
        "A value of zero indicates there are no Extended Textual File Header records (i.e. this file has no Extended "
        "Textual File Header(s)). A value of -1 indicates that there are a variable number of Extended Textual File "
        "Header records and the end of the Extended Textual File Header is denoted by an ((SEG: EndText)) stanza in "
        "the final record. A positive value indicates that there are exactly that many Extended Textual File Header "
        "records. Note that, although the exact number of Extended Textual File Header records may be a useful piece "
        "of information, it will not always be known at the time the Binary Header is written and it is not mandatory "
        "that a positive value be recorded here. This field is mandatory for all versions of SEG Y, although a value "
        "of zero indicates “traditional” SEG Y conforming to the 1975 standard."
    )

