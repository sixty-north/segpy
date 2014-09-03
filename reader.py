from __future__ import print_function

from portability import seekable
from util import file_length, filename_from_handle
from datatypes import DATA_SAMPLE_FORMAT, CTYPE_DESCRIPTION, CTYPES, size_in_bytes
from toolkit import (extract_revision,
                     bytes_per_sample,
                     read_reel_header,
                     catalog_traces,
                     read_binary_values,
                     compile_trace_header_format,
                     TraceHeader,
                     REEL_HEADER_NUM_BYTES,
                     TRACE_HEADER_NUM_BYTES)


def create_reader(fh, endian='>', progress=None):
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
    if fh.encoding is not None:
        raise TypeError(
            "SegYReader must be provided with a binary mode file object")

    if not seekable(fh):
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

    reel_header = read_reel_header(fh, endian)
    revision = extract_revision(reel_header)
    bps = bytes_per_sample(reel_header, revision)

    trace_offset_catalog, trace_length_catalog, cdp_catalog, line_catalog = catalog_traces(fh, bps, endian, progress)

    if cdp_catalog is not None and line_catalog is None:
        return SegYReader2D(fh, reel_header, trace_offset_catalog, trace_length_catalog,
                            cdp_catalog, endian)

    if cdp_catalog is None and line_catalog is not None:
        return SegYReader3D(fh, reel_header, trace_offset_catalog, trace_length_catalog,
                            line_catalog, endian)

    return SegYReader(fh, reel_header, trace_offset_catalog, endian)


class SegYReader(object):

    """A basic SEG Y reader.

    Use to obtain read the reel header, the trace headers or trace
    values. Traces can be accessed only by trace index.
    """

    def __init__(self, fh, reel_header, trace_offset_catalog, trace_length_catalog, endian='>'):
        """Initialize a SegYReader around a file-like-object.

        Note:
            Usually a SegYReader is most easily constructed using the
            create_reader() function.

        Args:
            fh: A file-like object, which must support seeking and
            support binary reading.

            reel_header: A dictionary containing reel header data.

            trace_catalog: A mapping from zero-based trace index to
                the byte-offset to individual traces within the file.

            trace_length_catalog: A mapping from zero-based trace index to the
                number of samples in that trace.

            endian: '>' for big-endian data (the standard and default), '<' for
                little-endian (non-standard)

        """
        self._fh = fh
        self._endian = endian
        self._trace_header_format = compile_trace_header_format(self._endian)

        self._reel_header = reel_header
        self._trace_offset_catalog = trace_offset_catalog
        self._trace_length_catalog = trace_length_catalog

        self._revision = extract_revision(self._reel_header)
        self._bytes_per_sample = bytes_per_sample(
            self._reel_header, self.revision)

    def trace_indexes(self):
        """An iterator over zero-based trace indexes.

        Returns:
            An iterator which yields integers in the range zero to
            num_traces() - 1
        """
        return iter(self._trace_offset_catalog)

    def num_traces(self):
        """The number of traces"""
        return len(self._trace_offset_catalog)

    def read_trace(self, trace_index, start=None, stop=None):
        """Read a specific trace.

        Args:
            trace_index: An integer in the range zero to num_traces() - 1

            start: Optional zero-based start sample index. The default
                is to read from the first (i.e. zeroth) sample.

            stop: Optional zero-based stop sample index. Following Python
                slice convention this is one beyond the end.

        Returns:
            A sequence of numeric trace samples.

        Example:

            first_trace_samples = segy_reader.read_trace(0)
            part_of_second_trace_samples = segy_reader.read_trace(1, 1000, 2000)
        """
        if not (0 <= trace_index < self.num_traces()):
            raise ValueError("Trace index out of range.")

        num_samples_in_trace = self._trace_length_catalog[trace_index]

        start_sample = start if start is not None else 0
        stop_sample = stop if stop is not None else num_samples_in_trace

        if not (0 <= stop_sample <= num_samples_in_trace):
            raise ValueError("read_trace(): stop value {} out of range 0 to {}"
                             .format(stop, num_samples_in_trace))

        if not (0 <= start_sample <= stop_sample):
            raise ValueError("read_trace(): start value {} out of range 0 to {}"
                             .format(start, stop_sample))

        dsf = self._reel_header['DataSampleFormat']
        ctype = DATA_SAMPLE_FORMAT[dsf]
        start_pos = (self._trace_offset_catalog[trace_index]
                     + TRACE_HEADER_NUM_BYTES
                     + start_sample * size_in_bytes(CTYPES[ctype]))
        num_samples_to_read = stop_sample - start_sample

        trace_values = read_binary_values(
            self._fh, start_pos, ctype, num_samples_to_read, self._endian)
        return trace_values

    def read_trace_header(self, trace_index):
        """Read a specific trace.

        Args:
            trace_index: An integer in the range zero to num_traces() - 1

        Returns:
            A TraceHeader corresponding to the requested trace.

        Example:

            first_trace_header, first_trace_samples = segy_reader.read_trace(0)
        """
        if not (0 <= trace_index < self.num_traces()):
            raise ValueError("Trace index {} out of range".format(trace_index))
        pos = self._trace_offset_catalog[trace_index]
        self._fh.seek(pos)
        data = self._fh.read(TRACE_HEADER_NUM_BYTES)
        trace_header = TraceHeader._make(
            self._trace_header_format.unpack(data))
        return trace_header

    @property
    def dimensionality(self):
        """The spatial dimensionality of the data.

        Returns:
            3 for 3D seismic volumes, 2 for 2D seismic lines, 1 for a
            single trace, otherwise 0.

        """
        return self._dimensionality()

    def _dimensionality(self):
        return 1 if self.num_traces() == 1 else 0

    @property
    def reel_header(self):
        """The reel header, sometimes known as the binary header.

        Returns:
            A dictionary containing data from the reel header.
        """
        return self._reel_header

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
        """The number of bytes per trace sample.
        """
        return self._bytes_per_sample

    @property
    def data_sample_format(self):
        """The data type of the samples in machine-readable form.

        Returns:
            One of the values from datatypes.DATA_SAMPLE_FORMAT
        """
        return DATA_SAMPLE_FORMAT[self._reel_header['DataSampleFormat']]

    @property
    def data_sample_format_description(self):
        """A descriptive human-readable description of the data sample format
        """
        return CTYPE_DESCRIPTION[CTYPES[self.data_sample_format]]


class SegYReader3D(SegYReader):
    """A reader for 3D seismic data.

    In addition to the capabilities provided by the SegYReader base
    class, this reader provides an index to facilitate random access
    to individual traces via crossline and inline co-ordinates.
    """

    def __init__(self,
                 fh,
                 reel_header,
                 trace_offset_catalog,
                 trace_length_catalog,
                 line_catalog,
                 endian='>'):
        """Initialize a SegYReader3D around a file-like-object.

        Note:
            Usually a SegYReader is most easily constructed using the
            create_reader() function.

        Args:
            fh: A file-like object, which must support seeking and
                support binary reading.

            reel_header: A dictionary containing reel header data.

            trace_offset_catalog: A mapping from zero-based trace indexes to
                the byte-offset to individual traces within the file.

            trace_length_catalog: A mapping from zero-based trace indexes to
                the number of samples in that trace.

            line_catalog: A mapping from (xline, inline) tuples to
                trace_indexes.

            endian: '>' for big-endian data (the standard and default), '<' for
                little-endian (non-standard)
        """
        super(SegYReader3D, self).__init__(
            fh, reel_header, trace_offset_catalog, trace_length_catalog, endian)
        self._line_catalog = line_catalog

    def _dimensionality(self):
        return 3

    def num_inlines(self):
        """The number of distinct inlines in the survey
        """
        try:
            return self._line_catalog.j_max - self._line_catalog.j_min
        except AttributeError:
            # TODO: Memoize
            return len(set(j for i, j in self._line_catalog))

    def num_xlines(self):
        """The number of distinct crosslines in the survey
        """
        try:
            return self._line_catalog.i_max - self._line_catalog.i_min
        except AttributeError:
            # TODO: Memoize
            return len(set(i for i, j in self._line_catalog))

    def inline_xline_numbers(self):
        """An iterator over all (xline_number, inline_number) tuples
        corresponding to traces.
        """
        return iter(self._line_catalog)

    def trace_index(self, xline, inline):
        """Obtain the trace index given an xline and a inline.

        Note:
            Do not assume that all combinations of crossline and
            inline co-ordinates are valid.  The volume may not be
            rectangular.  Valid values can be obtained from the
            inline_xline_numbers() iterator.

            Furthermore, inline and crossline numbers should not be
            relied upon to be zero- or one-based indexes (although
            they may be).

        Args:
            xline: A crossline number.
            inline: An inline number.

        Returns:
            A trace index which can be used with read_trace().
        """
        return self._line_catalog[(xline, inline)]


class SegYReader2D(SegYReader):

    def __init__(self,
                 fh,
                 reel_header,
                 trace_offset_catalog,
                 trace_length_catalog,
                 cdp_catalog,
                 endian='>'):
        """Initialize a SegYReader2D around a file-like-object.

        Note:
            Usually a SegYReader is most easily constructed using the
            create_reader() function.

        Args:
            fh: A file-like object, which must support seeking and
                support binary reading.

            reel_header: A dictionary containing reel header data.

            trace_catalog_offset: A mapping from zero-based trace index to
                the byte-offset to individual traces within the file.

            trace_length_catalog: A mapping from zero-based trace indexes to
                the number of samples in that trace.

            cdp_catalog: A mapping from CDP numbers to trace_indexes.

            endian: '>' for big-endian data (the standard and default), '<' for
                little-endian (non-standard)
        """
        super(SegYReader2D, self).__init__(
            fh, reel_header, trace_offset_catalog, trace_length_catalog, endian)
        self._cdp_catalog = cdp_catalog

    def _dimensionality(self):
        return 2

    def cdp_numbers(self):
        """An iterator over all cdp numbers corresponding to traces.
        """
        return iter(self._cdp_catalog)

    def num_cdps(self):
        return len(self._cdp_catalog)

    def trace_index(self, cdp_number):
        """Obtain the trace index given an xline and a inline.

        Note:
            Do not assume that all combinations of crossline and
            inline co-ordinates are valid.  The volume may not be
            rectangular.  Valid values can be obtained from the
            inline_xline_numbers() iterator.

            Furthermore, inline and crossline numbers should not be
            relied upon to be zero- or one-based indexes (although
            they may be).

        Args:
            xline: A crossline number.
            inline: An inline number.

        Returns:
            A trace index which can be used with read_trace().
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

        #trace_index = segy_reader.trace_index(20, 300)
        #trace_data = segy_reader.read_trace(trace_index, 200, 800)
        pass


if __name__ == '__main__':
    main()
