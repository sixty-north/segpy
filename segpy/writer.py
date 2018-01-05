from segpy.encoding import ASCII, is_supported_encoding, UnsupportedEncodingError
from segpy.packer import make_header_packer
from segpy.trace_header import TraceHeaderRev1
from segpy.toolkit import (write_textual_reel_header, write_binary_reel_header,
                           write_trace_header, write_trace_samples,
                           write_extended_textual_headers)


def write_segy(fh,
               dataset,
               encoding=None,
               trace_header_format=TraceHeaderRev1,
               endian='>',
               progress=None):
    """
    Args:
        fh: A file-like object open for binary write, positioned to write the textual reel header.

        dataset: An object implementing the interface of segpy.dataset.Dataset, such as a SegYReader.

        trace_header_format: The class which defines the layout of the trace header. Defaults to TraceHeaderRev1.

        encoding: Optional encoding for text data. Typically 'cp037' for EBCDIC or 'ascii' for ASCII. If omitted, the
            seg_y_data object will be queries for an encoding property.

        endian: Big endian by default. If omitted, the dataset object will be queried for an encoding property.

        progress: A unary callable which will be passed a number
            between zero and one indicating the progress made. If
            provided, this callback will be invoked at least once with
            an argument equal to one.

    Raises:
        UnsupportedEncodingError: If the specified encoding is neither ASCII nor EBCDIC
        UnicodeError: If textual data provided cannot be encoded into the required encoding.
    """

    progress_callback = progress if progress is not None else lambda p: None

    if not callable(progress_callback):
        raise TypeError("write_segy(): progress callback must be callable")

    encoding = encoding or (hasattr(dataset, 'encoding') and dataset.encoding) or ASCII

    if not is_supported_encoding(encoding):
        raise UnsupportedEncodingError("Writing SEG Y", encoding)

    write_textual_reel_header(fh, dataset.textual_reel_header, encoding)
    write_binary_reel_header(fh, dataset.binary_reel_header, endian)
    write_extended_textual_headers(fh, dataset.extended_textual_header, encoding)

    trace_header_packer = make_header_packer(trace_header_format, endian)

    num_traces = dataset.num_traces()

    for trace_index in dataset.trace_indexes():
        write_trace_header(fh, dataset.trace_header(trace_index), trace_header_packer)
        write_trace_samples(fh, dataset.trace_samples(trace_index), dataset.data_sample_format, endian=endian)
        progress_callback(trace_index / num_traces)

    progress_callback(1)
