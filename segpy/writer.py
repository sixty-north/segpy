from segpy.encoding import ASCII, is_supported_encoding, UnsupportedEncodingError
from segpy.packer import make_header_packer
from segpy.trace_header import TraceHeaderRev1
from segpy.util import file_length, filename_from_handle, hash_for_file
from segpy.toolkit import (extract_revision, 
                           bytes_per_sample, 
                           read_binary_reel_header, 
                           read_textual_reel_header,
                           read_extended_textual_headers,
                           catalog_traces,
                           catalog_fixed_length_traces,
                           write_textual_reel_header, 
                           write_binary_reel_header,
                           write_trace_header, write_trace_samples,
                           write_extended_textual_headers,
                           guess_textual_header_encoding,
                           read_trace_header,
                           REEL_HEADER_NUM_BYTES,
                           TRACE_HEADER_NUM_BYTES,
                           TEXTUAL_HEADER_NUM_BYTES)
from segpy.reader import SegYReader, SegYReader2D, SegYReader3D, _locate_cache_file, _load_reader_from_cache, _save_reader_to_cache

def create_writer(fh, encoding=None, trace_header_format=TraceHeaderRev1, endian='>', progress=None, cache_directory=None, fast=False):
    """Create a SegYWriter (or one of its subclasses) based on performing
    a scan of SEG Y data.

    This function is the preferred method for creating SegYWriter
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

        trace_header_format: An optional class defining the layout of the
            trace header. Defaults to TraceHeaderRev1.

        endian: '>' for big-endian data (the standard and default), '<'
                for little-endian (non-standard)

        progress: A unary callable which will be passed a number
            between zero and one indicating the progress made. If
            provided, this callback will be invoked at least once with
            an argument equal to one.

        cache_directory: The directory for the cache file. Relative paths
            are interpreted as being relative to the directory containing
            the SEG Y file. Absolute paths are used as is. If
            cache_directory is None, caching is disabled.
            
        fast: Boolean flag to try a quick fixed length catalog before inline or
            CDP catalogs.

    Raises:
        ValueError: ``fh`` is unsuitable for some reason, such as not
                    being open, not being seekable, not being in
                    binary mode, or being too short.

    Returns:
        A SegYWriter object. Depending on the exact type of the
        SegYWriter returned different capabilities may be
        available. Inspect the returned object to determine these
        capabilities, or be prepared for capabilities not defined in
        the SegYWriter base class to be unavailable.  The underlying
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
            "SegYWriter must be provided with a binary mode file object")

    if not fh.seekable():
        raise TypeError(
            "SegYWriter must be provided with a seekable file object")

    if fh.closed:
        raise ValueError(
            "SegYWriter must be provided with an open file object")

    num_file_bytes = file_length(fh)
    if num_file_bytes < REEL_HEADER_NUM_BYTES:
        raise ValueError(
            "SEG Y file {!r} of {} bytes is too short".format(
                filename_from_handle(fh),
                num_file_bytes))

    if endian not in ('<', '>'):
        raise ValueError("Unrecognised endian value {!r}".format(endian))

    reader = None
    cache_file_path = None

    if cache_directory is not None:
        sha1 = hash_for_file(fh, encoding, trace_header_format, endian)
        seg_y_path = filename_from_handle(fh)
        cache_file_path = _locate_cache_file(seg_y_path, cache_directory, sha1)
        if cache_file_path is not None:
            reader = _load_reader_from_cache(cache_file_path, seg_y_path)

    if reader is None:
        reader = _make_writer(fh, encoding, trace_header_format, endian, progress, fast=fast)
        if cache_directory is not None:
            _save_reader_to_cache(reader, cache_file_path)

    return reader

def _make_writer(fh, encoding, trace_header_format, endian, progress, fast=False):
    if encoding is None:
        encoding = guess_textual_header_encoding(fh)
    if encoding is None:
        encoding = ASCII
    textual_reel_header = read_textual_reel_header(fh, encoding)
    binary_reel_header = read_binary_reel_header(fh, endian)
    extended_textual_header = read_extended_textual_headers(fh, binary_reel_header, encoding)
    revision = extract_revision(binary_reel_header)
    bps = bytes_per_sample(binary_reel_header, revision)
    if fast:
        try:
            trace_offset_catalog, trace_length_catalog, cdp_catalog, line_catalog = catalog_fixed_length_traces(fh, binary_reel_header, trace_header_format,endian, progress)
        except:
            trace_offset_catalog, trace_length_catalog, cdp_catalog, line_catalog = catalog_traces(fh, bps, trace_header_format,endian, progress)
    else: 
        try:
            trace_offset_catalog, trace_length_catalog, cdp_catalog, line_catalog = catalog_traces(fh, bps, trace_header_format,endian, progress)
        except:
            fh.seek(REEL_HEADER_NUM_BYTES)
            trace_offset_catalog, trace_length_catalog, cdp_catalog, line_catalog = catalog_fixed_length_traces(fh, binary_reel_header, trace_header_format,endian, progress)
    
                                                                                           
    if line_catalog is not None:
        return SegYWriter3D(fh, textual_reel_header, binary_reel_header, extended_textual_header, trace_offset_catalog,
                            trace_length_catalog, line_catalog, trace_header_format, encoding, endian)
    if cdp_catalog is not None:
        return SegYWriter2D(fh, textual_reel_header, binary_reel_header, extended_textual_header, trace_offset_catalog,
                            trace_length_catalog, cdp_catalog, trace_header_format, encoding, endian)

    return SegYWriter(fh, textual_reel_header, binary_reel_header, extended_textual_header, trace_offset_catalog,
                      trace_length_catalog, trace_header_format, encoding, endian)

class SegYWriter(SegYReader):
    """
    Mixin that extends SegyReader with Writing capabilities
    """
    
    def trace_position(self,trace_index):
        if not (0 <= trace_index < self.num_traces()):
            raise ValueError("Trace index out of range.")
        return self._trace_offset_catalog[trace_index]
        
    def write_trace_header(self,trace_index,trace_header,force=True):
        """
        Write a trace header in place
        """
        pos=self.trace_position(trace_index)
        try:
            read_trace_header(self._fh, self._trace_header_packer, pos=pos)
        except Exception as e:
            print ("Could not read a trace header from trace_index={}, skipping writting. Pass force=False to force. Exception: {}".format(trace_index),e)
        else:
            write_trace_header(self._fh,trace_header,self._trace_header_packer,pos)
        
    def write_binary_reel_header(self,binary_reel_header):
        self._fh.seek(REEL_HEADER_NUM_BYTES)
        write_binary_reel_header(self._fh, binary_reel_header, self.endian)
        
    def write_textual_reel_header(self,textual_reel_header):
        self._fh.seek(0)
        write_textual_reel_header(self._fh, textual_reel_header, self.encoding)
        
    def write_extended_textual_headers(self,extended_textual_header):
        self._fh.seek(TEXTUAL_HEADER_NUM_BYTES)
        write_extended_textual_headers(self._fh, extended_textual_header, self.encoding)
        
    def write_trace_samples(self,trace_index,samples):
        num_samples_in_trace = self.num_trace_samples(trace_index)
        start_pos = (self.trace_position(trace_index) + TRACE_HEADER_NUM_BYTES)
        if not num_samples_in_trace==len(samples):
            raise ValueError(
            "Length of samples {} does not fit in trace size {}".format(len(samples),num_samples_in_trace))
        
        write_trace_samples(self._fh, samples, self.data_sample_format, pos=start_pos, endian='>')


class SegYWriter2D(SegYReader2D,SegYWriter):
    pass


class SegYWriter3D(SegYReader3D,SegYWriter):
    pass

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
    
    with open(filename, 'r+b') as segy_file:
        segy_reader = create_writer(segy_file, progress=ProgressBar(30))
        
        trace_header = segy_reader.trace_header(0)
        trace_header.shotpoint_scalar=trace_header.shotpoint_scalar
        segy_reader.write_trace_header(0,trace_header)
        
        binary_reel_header = segy_reader.binary_reel_header
        binary_reel_header.num_samples=binary_reel_header.num_samples
        segy_reader.write_binary_reel_header(binary_reel_header)
        
        trace_samples=segy_reader.trace_samples(0)
        segy_reader.write_trace_samples(0,trace_samples)

    with open(filename, 'rb') as segy_file:
        segy_reader = create_writer(segy_file, progress=ProgressBar(30))
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
