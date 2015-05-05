from __future__ import print_function
from segpy.encoding import ASCII
from segpy.packer import HeaderPacker

from segpy.trace_header import TraceHeaderRev1
from segpy.util import file_length, filename_from_handle
from segpy.datatypes import DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE, SEG_Y_TYPE_DESCRIPTION, SEG_Y_TYPE_TO_CTYPE, size_in_bytes
from segpy.toolkit import (extract_revision,
                           bytes_per_sample,
                           read_binary_reel_header,
                           read_trace_header,
                           catalog_traces,
                           read_binary_values,
                           REEL_HEADER_NUM_BYTES,
                           TRACE_HEADER_NUM_BYTES,
                           read_textual_reel_header,
                           read_extended_textual_headers,
                           guess_textual_header_encoding)


def create_reader(fh, encoding=None, trace_header_format=TraceHeaderRev1, endian='>', progress=None):
    """Create a SegYReader (or one of its subclasses) based on performing
    a scan of SEG Y data.

    This function is the preferred method for creating SegYReader
    objects. It reads basic header information and attempts to build
    indexes for traces, CDP numbers (for 2D surveys), and inline and
    cross line co-ordinates (for 3D surveys) to facilitate subsequent
    random-access to traces.

    Args:
        fh: A file-like-object open in binary mode positioned such
            that the beginning of the reel header will be the next
            byte to be read. For disk-based SEG Y files, this is the
            beginning of the file.

        encoding: An optional text encoding for the textual headers. If
            None (the default) a heuristic will be used to guess the
            header encoding.

        trace_header_format: The class defining the layout of the trace header.

        endian: '>' for big-endian data (the standard and default), '<'
                for little-endian (non-standard)

        progress: A unary callable which will be passed a number
            between zero and one indicating the progress made. If
            provided, this callback will be invoked at least once with
            an argument equal to one.

    Raises:
        ValueError: ``fh`` is unsuitable for some reason, such as not
                    being open, not being seekable, not being in
                    binary mode, or being too short.

    Returns:
        A SegYReader object. Depending on the exact type of the
        SegYReader returned different capabilities may be
        available. Inspect the returned object to determine these
        capabilities, or be prepared for capabilities not defined in
        the SegYReader base class to be unavailable.  The underlying
        file-like object must remain open for the duration of use of
        the returned reader object. It is the caller's responsibility
        to close the underlying file.

    Example:

        with open('my_seismic_data.sgy', 'rb') as fh:
            reader = create_reader(fh)
            print(reader.num_traces())

    """
    if hasattr(fh, 'encoding') and fh.encoding is not None:
        raise TypeError(
            "SegYReader must be provided with a binary mode file object")

    if not fh.seekable():
        raise TypeError(
            "SegYReader must be provided with a seekable file object")

    if fh.closed:
        raise ValueError(
            "SegYReader must be provided with an open file object")

    num_file_bytes = file_length(fh)
    if num_file_bytes < REEL_HEADER_NUM_BYTES:
        raise ValueError(
            "SEG Y file {!r} of {} bytes is too short".format(
                filename_from_handle(fh),
                num_file_bytes))

    if endian not in ('<', '>'):
        raise ValueError("Unrecognised endian value {!r}".format(endian))

    if encoding is None:
        encoding = guess_textual_header_encoding(fh)

    if encoding is None:
        encoding = ASCII

    textual_reel_header = read_textual_reel_header(fh, encoding)
    binary_reel_header = read_binary_reel_header(fh, endian)
    extended_textual_header = read_extended_textual_headers(fh, binary_reel_header, encoding)
    revision = extract_revision(binary_reel_header)
    bps = bytes_per_sample(binary_reel_header, revision)

    trace_offset_catalog, trace_length_catalog, cdp_catalog, line_catalog = catalog_traces(fh, bps, trace_header_format,
                                                                                           endian, progress)

    if cdp_catalog is not None and line_catalog is None:
        return SegYReader2D(fh, textual_reel_header, binary_reel_header, extended_textual_header, trace_offset_catalog,
                            trace_length_catalog, cdp_catalog, trace_header_format, encoding, endian)

    if cdp_catalog is None and line_catalog is not None:
        return SegYReader3D(fh, textual_reel_header, binary_reel_header, extended_textual_header, trace_offset_catalog,
                            trace_length_catalog, line_catalog, trace_header_format, encoding, endian)

    return SegYReader(fh, textual_reel_header, binary_reel_header, extended_textual_header, trace_offset_catalog,
                      trace_length_catalog, trace_header_format, encoding, endian)


class SegYReader(object):
    """A basic SEG Y reader.

    Use to obtain read the reel header, the trace_samples headers or trace_samples
    values. Traces can be accessed only by trace_samples index.
    """

    def __init__(self,
                 fh,
                 textual_reel_header,
                 binary_reel_header,
                 extended_textual_headers,
                 trace_offset_catalog,
                 trace_length_catalog,
                 trace_header_format,
                 encoding,
                 endian='>'):
        """Initialize a SegYReader around a file-like-object.

                Note:
            Usually a SegYReader is most easily constructed using the
            create_reader() function.

        Args:
            fh: A file-like object, which must support seeking and
            support binary reading.

            textual_reel_header: A sequence of forty 80-character Unicode strings
                containing header data.

            binary_reel_header: A dictionary containing reel header data.

            extended_textual_headers: A sequence of sequences of Unicode strings.

            trace_offset_catalog: A mapping from zero-based trace_samples index to
                the byte-offset to individual traces within the file.

            trace_length_catalog: A mapping from zero-based trace_samples index to the
                number of samples in that trace_samples.

            trace_header_format: The class defining the layout of the trace header.

            encoding: Either ASCII or EBCDIC.

            endian: '>' for big-endian data (the standard and default), '<' for
                little-endian (non-standard)

        """
        self._fh = fh
        self._endian = endian
        self._encoding = encoding

        self._textual_reel_header = textual_reel_header
        self._binary_reel_header = binary_reel_header
        self._extended_textual_headers = extended_textual_headers

        self._trace_header_packer = HeaderPacker(trace_header_format, endian)

        self._trace_offset_catalog = trace_offset_catalog
        self._trace_length_catalog = trace_length_catalog

        self._revision = extract_revision(self._binary_reel_header)
        self._bytes_per_sample = bytes_per_sample(
            self._binary_reel_header, self.revision)

    def trace_indexes(self):
        """An iterator over zero-based trace_samples indexes.

        Returns:
            An iterator which yields integers in the range zero to
            num_traces() - 1
        """
        return iter(self._trace_offset_catalog)

    def num_traces(self):
        """The number of traces"""
        return len(self._trace_offset_catalog)

    def max_num_trace_samples(self):
        """The number of samples in the trace_samples with the most samples."""
        return self._trace_length_catalog.value_max()

    def num_trace_samples(self, trace_index):
        """The number of samples in the specified trace_samples."""
        return self._trace_length_catalog[trace_index]

    def trace_samples(self, trace_index, start=None, stop=None):
        """Read a specific trace_samples.

        Args:
            trace_index: An integer in the range zero to num_traces() - 1

            start: Optional zero-based start sample index. The default
                is to read from the first (i.e. zeroth) sample.

            stop: Optional zero-based stop sample index. Following Python
                slice convention this is one beyond the end.

        Returns:
            A sequence of numeric trace_samples samples.

        Example:

            first_trace_samples = segy_reader.trace_samples(0)
            part_of_second_trace_samples = segy_reader.trace_samples(1, 1000, 2000)
        """
        if not (0 <= trace_index < self.num_traces()):
            raise ValueError("Trace index out of range.")

        num_samples_in_trace = self.num_trace_samples(trace_index)

        start_sample = start if start is not None else 0
        stop_sample = stop if stop is not None else num_samples_in_trace

        if not (0 <= stop_sample <= num_samples_in_trace):
            raise ValueError("trace_samples(): stop value {} out of range 0 to {}"
                             .format(stop, num_samples_in_trace))

        if not (0 <= start_sample <= stop_sample):
            raise ValueError("trace_samples(): start value {} out of range 0 to {}"
                             .format(start, stop_sample))

        dsf = self._binary_reel_header.data_sample_format
        seg_y_type = DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE[dsf]
        start_pos = (self._trace_offset_catalog[trace_index]
                     + TRACE_HEADER_NUM_BYTES
                     + start_sample * size_in_bytes(SEG_Y_TYPE_TO_CTYPE[seg_y_type]))
        num_samples_to_read = stop_sample - start_sample

        trace_values = read_binary_values(
            self._fh, start_pos, seg_y_type, num_samples_to_read, self._endian)
        return trace_values

    def trace_header(self, trace_index):
        """Read a specific trace_samples.

        Args:
            trace_index: An integer in the range zero to num_traces() - 1

        Returns:
            A TraceHeader corresponding to the requested trace_samples.

        Example:

            first_trace_header, first_trace_samples = segy_reader.trace_samples(0)
        """
        if not (0 <= trace_index < self.num_traces()):
            raise ValueError("Trace index {} out of range".format(trace_index))
        pos = self._trace_offset_catalog[trace_index]
        trace_header = read_trace_header(self._fh, self._trace_header_packer, pos)
        return trace_header

    @property
    def dimensionality(self):
        """The spatial dimensionality of the data.

        Returns:
            3 for 3D seismic volumes, 2 for 2D seismic lines, 1 for a
            single trace_samples, otherwise 0.

        """
        return self._dimensionality()

    def _dimensionality(self):
        return 1 if self.num_traces() == 1 else 0

    @property
    def textual_reel_header(self):
        """The textual real header.

        An immutable sequence of forty Unicode strings each 80 characters long.
        """
        return self._textual_reel_header

    @property
    def binary_reel_header(self):
        """The binary reel header.

        A dictionary containing data from the reel header.
        """
        return self._binary_reel_header

    @property
    def extended_textual_header(self):
        """A sequence of sequences of Unicode strings.

        If there were no headers, the sequence will be empty.
        """
        return self._extended_textual_headers


    @property
    def filename(self):
        """The filename.

        Returns:
            The filename if it could be determined, otherwise '<unknown>'
        """
        return filename_from_handle(self._fh)

    @property
    def revision(self):
        """The SEG Y revision.

        Returns:
            Either datatypes.SEGY_REVISION_0 or datatypes.SEGY_REVISION_1
        """
        return self._revision

    @property
    def bytes_per_sample(self):
        """The number of bytes per trace_samples sample.
        """
        return self._bytes_per_sample

    @property
    def data_sample_format(self):
        """The data type of the samples in machine-readable form.

        Returns:
            One of the values from datatypes.DATA_SAMPLE_FORMAT
        """
        return DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE[self._binary_reel_header.data_sample_format]

    @property
    def data_sample_format_description(self):
        """A descriptive human-readable description of the data sample format
        """
        return SEG_Y_TYPE_DESCRIPTION[self.data_sample_format]

    @property
    def encoding(self):
        """The encoding, of the data in the underlying file. Either ASCII ('ascii'),
           EBCDIC ('cp037') or None."""
        return self._encoding

    @property
    def endian(self):
        """The endianness of the data in the underlying file. Either '>' for big-endian or '<' for
           little endian or None."""
        return self._endian


class SegYReader3D(SegYReader):
    """A reader for 3D seismic data.

    In addition to the capabilities provided by the SegYReader base
    class, this reader provides an index to facilitate random access
    to individual traces via crossline and inline co-ordinates.
    """

    def __init__(self,
                 fh,
                 textual_reel_header,
                 binary_reel_header,
                 extended_textual_headers,
                 trace_offset_catalog,
                 trace_length_catalog,
                 line_catalog,
                 trace_header_format,
                 encoding,
                 endian='>'):
        """Initialize a SegYReader3D around a file-like-object.

                Note:
            Usually a SegYReader is most easily constructed using the
            create_reader() function.

        Args:
            fh: A file-like object, which must support seeking and
                support binary reading.

            binary_reel_header: A dictionary containing reel header data.

            trace_offset_catalog: A mapping from zero-based trace_samples indexes to
                the byte-offset to individual traces within the file.

            trace_length_catalog: A mapping from zero-based trace_samples indexes to
                the number of samples in that trace_samples.

            line_catalog: A mapping from (xline, inline) tuples to
                trace_indexes.

            trace_header_format: The class defining the layout of the trace header.

            encoding: Either ASCII or EBCDIC.

            endian: '>' for big-endian data (the standard and default), '<' for
                little-endian (non-standard)
        """
        super(SegYReader3D, self).__init__(fh, textual_reel_header, binary_reel_header, extended_textual_headers,
                                           trace_offset_catalog, trace_length_catalog, trace_header_format,
                                           encoding, endian)
        self._line_catalog = line_catalog
        self._num_inlines = None
        self._num_xlines = None

    def _dimensionality(self):
        return 3

    def inline_range(self):
        """A range encompassing inline numbers.

        The number of inlines within this range can be found with len(reader.inline_range()).

        Returns:
            A range() object with start set to the first inline number and stop set to
            one beyond the last inline number. The range always has a step of one, although
            this should not be taken as meaning that any intermediate inline number generated
            by the range is valid.
        """
        start = self._line_catalog.key_min()[0]
        stop = self._line_catalog.key_max()[0] + 1
        return range(start, stop)

    def num_inlines(self):
        """The number of distinct inlines in the survey.

        This number is not necessarily the same as the value returned by
        len(reader.inline_range()) as there may be missing inlines within the range.
        """
        if self._num_inlines is None:
            try:
                self._num_inlines = self._line_catalog.i_max - self._line_catalog.i_min + 1
            except AttributeError:
                self._num_inlines = len(set(i for i, j in self._line_catalog))
        return self._num_inlines

    def xline_range(self):
        """A range encompassing crossline numbers.

        The number of crosslines within this range can be found with len(reader.crossline_range()).

        Returns:
            A range() object with start set to the first crossline number and stop set to
            one beyond the last crossline number. The range always has a step of one, although
            this should not be taken as meaning that any intermediate crossline number generated
            by the range is valid.
        """
        start = self._line_catalog.key_min()[1]
        stop = self._line_catalog.key_max()[1] + 1
        return range(start, stop)

    def num_xlines(self):
        """The number of distinct crosslines in the survey.

        This number is not necessarily the same as the value returned by
        len(reader.xline_range()) as there may be missing crosslines within the range.
        """
        if self._num_xlines is None:
            try:
                self._num_xlines = self._line_catalog.j_max - self._line_catalog.j_min + 1
            except AttributeError:
                self._num_xlines = len(set(j for i, j in self._line_catalog))
        return self._num_xlines

    def inline_xline_numbers(self):
        """An iterator over all  (inline_number, xline_number) tuples
        corresponding to traces.
        """
        return iter(self._line_catalog)

    def has_trace_index(self, inline_xline):
        """Determine whether a specific trace_samples exists.

        Args:
            inline_xline: A 2-tuple of inline number, crossline number.

        Returns:
            True if the specified trace_samples exists, otherwise False.
        """
        return inline_xline in self._line_catalog

    def trace_index(self, inline_xline):
        """Obtain the trace_samples index given an xline and a inline.

        Note:
            Do not assume that all combinations of crossline and
            inline co-ordinates are valid.  The volume may not be
            rectangular.  Valid values can be obtained from the
            inline_xline_numbers() iterator.

            Furthermore, inline and crossline numbers should not be
            relied upon to be zero- or one-based indexes (although
            they may be).

        Args:
            inline_xline: A 2-tuple of inline number, crossline number.

        Returns:
            A trace_samples index which can be used with trace_samples().
        """
        return self._line_catalog[inline_xline]


class SegYReader2D(SegYReader):
    def __init__(self,
                 fh,
                 textual_reel_header,
                 binary_reel_header,
                 extended_textual_headers,
                 trace_offset_catalog,
                 trace_length_catalog,
                 cdp_catalog,
                 trace_header_format,
                 encoding,
                 endian='>'):
        """Initialize a SegYReader2D around a file-like-object.

        Note:
            Usually a SegYReader is most easily constructed using the
            create_reader() function.

        Args:
            fh: A file-like object, which must support seeking and
                support binary reading.

            binary_reel_header: A dictionary containing reel header data.

            trace_catalog_offset: A mapping from zero-based trace_samples index to
                the byte-offset to individual traces within the file.

            trace_length_catalog: A mapping from zero-based trace_samples indexes to
                the number of samples in that trace_samples.

            cdp_catalog: A mapping from CDP numbers to trace_indexes.

            trace_header_format: The class defining the layout of the trace header.

            encoding: Either ASCII or EBCDIC.

            endian: '>' for big-endian data (the standard and default), '<' for
                little-endian (non-standard)
        """
        super(SegYReader2D, self).__init__(fh, textual_reel_header, binary_reel_header, extended_textual_headers,
                                           trace_offset_catalog, trace_length_catalog, trace_header_format,
                                           encoding, endian)
        self._cdp_catalog = cdp_catalog

    def _dimensionality(self):
        return 2

    def cdp_numbers(self):
        """An iterator over all cdp numbers corresponding to traces.
        """
        return iter(self._cdp_catalog)

    def cdp_range(self):
        """A range encompassing CDP numbers.

        The number of CDPs within this range can be found with len(reader.cdp_range()).

        Returns:
            A range() object with start set to the first CDP number and stop set to
            one beyond the last CDP number. The range always has a step of one, although
            this should not be taken as meaning that any intermediate CDP number generated
            by the range is valid.
        """
        start = self._cdp_catalog.value_min()
        stop = self._cdp_catalog.value_max() + 1
        return range(start, stop)

    def num_cdps(self):
        """The number of distinct CDPs.

        This number is not necessarily the same as the value returned by
        len(reader.cdp_range()) as there may be missing CDPs.
        """
        return len(self._cdp_catalog)

    def has_trace_index(self, cdp_number):
        """Determine whether a specified trace_samples exists.

        Args:
            cdp_number: A CDP number.

        Returns:
            True if the trace_samples exists, otherwise False.
        """
        return self._cdp_catalog[cdp_number]

    def trace_index(self, cdp_number):
        """Obtain the trace_samples index given an xline and a inline.

        Args:
            cdp_number: A CDP number.

        Returns:
            A trace_samples index which can be used with trace_samples().
        """
        return self._cdp_catalog[cdp_number]


def main(argv=None):
    import sys

    if argv is None:
        argv = sys.argv[1:]

    class ProgressBar(object):

        def __init__(self, num_chars, character='.'):
            self._num_chars = num_chars
            self._character = character
            self._ratchet = 0

        def __call__(self, proportion):
            existing = self._num_marks(self._ratchet)
            required = self._num_marks(proportion)
            print(self._character * (required - existing), end='')
            self._ratchet = proportion

        def _num_marks(self, p):
            return int(round(p * self._num_chars))

    filename = argv[0]

    with open(filename, 'rb') as segy_file:
        segy_reader = create_reader(segy_file, progress=ProgressBar(30))
        print()
        print("Filename:             ", segy_reader.filename)
        print("SEG Y revision:       ", segy_reader.revision)
        print("Number of traces:     ", segy_reader.num_traces())
        print("Data format:          ",
              segy_reader.data_sample_format_description)
        print("Dimensionality:       ", segy_reader.dimensionality)

        try:
            print("Number of CDPs:       ", segy_reader.num_cdps())
        except AttributeError:
            pass

        try:
            print("Number of inlines:    ", segy_reader.num_inlines())
            print("Number of crosslines: ", segy_reader.num_xlines())
        except AttributeError:
            pass

        print("=== BEGIN TEXTUAL REEL HEADER ===")
        for line in segy_reader.textual_reel_header:
            print(line[3:])
        print("=== END TEXTUAL REEL HEADER ===")
        print()
        print("=== BEGIN EXTENDED TEXTUAL HEADER ===")
        print(segy_reader.extended_textual_header)
        print("=== END EXTENDED TEXTUAL_HEADER ===")


if __name__ == '__main__':
    main()
