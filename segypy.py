"""
A Python module for reading/writing/manipulating
SEG-Y formatted files

segy.readSegy                : Read SEGY file
segy.read_reel_header           : Get SEGY header
segy.read_trace_header      : Get SEGY Trace header
segy.read_all_trace_headers  : Get all SEGY Trace headers
segy.getSegyTrace            : Get SEGY Trace header and trace data for one trace

segy.writeSegy               : Write a data to a SEGY file
segy.writeSegyStructure      : Writes a segpy data structure to a SEGY file

segy.read_binary_value        : Get a value from a binary string
segy.ibm2ieee        : Convert IBM floats to IEEE

segy.version         : The version of SegyPY
segy.verbose         : Amount of verbose information to the screen
"""
#
# segpy : A Python module for reading and writing SEG-Y formatted data
#
# Forked by Robert Smallshire from the original segypy by
#
# (C) Thomas Mejer Hansen, 2005-2006
#
# with contributions from Pete Forman and Andrew Squelch 2007
import os

import sys
import struct
import logging

from numpy import transpose
from numpy import reshape
from numpy import zeros
from numpy import arange

from revisions import canonicalize_revision
from header_definition import HEADER_DEF
from trace_header_definition import TRACE_HEADER_DEF
from ibm_float import ibm2ieee2

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('segpy.segypy')

version = '0.3.1'

REEL_HEADER_NUM_BYTES = 3600
TRACE_HEADER_NUM_BYTES = 240

l_char = struct.calcsize('c')
l_uchar = struct.calcsize('B')
l_float = struct.calcsize('f')


DATA_SAMPLE_FORMAT = {1: 'ibm',
                      2: 'l',
                      3: 'h',
                      5: 'f',
                      8: 'B'}

CTYPES = {'l': 'l', 'long':   'l', 'int32':  'l',
          'L': 'L', 'ulong':  'L', 'uint32': 'L',
          'h': 'h', 'short':  'h', 'int16':  'h',
          'H': 'H', 'ushort': 'H', 'uint16': 'H',
          'c': 'c', 'char':   'c',
          'B': 'B', 'uchar':  'B',
          'f': 'f', 'float':  'f',
          'ibm': 'ibm'}

# TODO This is redundant with data in the SH_def below
CTYPE_DESCRIPTION = {'ibm': 'IBM float',
                     'l':   '32 bit integer',
                     'h':   '16 bit integer',
                     'f':   'IEEE float',
                     'B':   '8 bit char'}


def size_in_bytes(ctype):
    if ctype == 'l' and struct.calcsize(ctype) == 8:
        return 4  # 64-bit issue?
    return struct.calcsize(ctype) if ctype != 'ibm' else struct.calcsize('f')


def get_default_segy_header(ntraces=100, ns=100):
    """
    header = getDefaultSegyHeader()
    """
    # TraceSequenceLine
    header = {"Job": {"pos": 3200, "type": "int32", "def": 0}}

    for key in HEADER_DEF.keys():

        tmpkey = HEADER_DEF[key]
        if 'def' in tmpkey:
            val = tmpkey['def']
        else:
            val = 0
        header[key] = val

    header["ntraces"] = ntraces
    header["ns"] = ns

    return header


def get_default_segy_trace_headers(ntraces=100, ns=100, dt=1000):
    """
    SH = getDefaultSegyTraceHeader()
    """
    # INITIALIZE DICTIONARY
    trace_header = {"TraceSequenceLine": {"pos": 0, "type": "int32"}}

    for key in TRACE_HEADER_DEF.keys():

        tmpkey = TRACE_HEADER_DEF[key] # TODO: What is going on here?
        trace_header[key] = zeros(ntraces)

    for a in range(ntraces):
        trace_header["TraceSequenceLine"][a] = a + 1
        trace_header["TraceSequenceFile"][a] = a + 1
        trace_header["FieldRecord"][a] = 1000
        trace_header["TraceNumber"][a] = a + 1
        trace_header["ns"][a] = ns
        trace_header["dt"][a] = dt
    return trace_header


def read_trace_header(f, reel_header, trace_header_name='cdp', endian='>'):
    """
    read_trace_header(reel_header, TraceHeaderName)
    """

    bps = get_byte_per_sample(reel_header)

    # MAKE SOME LOOKUP TABLE THAT HOLDS THE LOCATION OF HEADERS
    trace_header_pos = TRACE_HEADER_DEF[trace_header_name]["pos"]

    # TODO: Be consistent between 'type' and 'format' here.
    trace_header_format = TRACE_HEADER_DEF[trace_header_name]["type"]
    ntraces = reel_header["ntraces"]
    trace_header_values = zeros(ntraces)
    binary_reader = create_binary_reader(f, trace_header_format, endian)
    start_pos = trace_header_pos + REEL_HEADER_NUM_BYTES
    stride = reel_header["ns"] * bps + TRACE_HEADER_NUM_BYTES
    end_pos = start_pos + (ntraces - 1) * stride + 1
    for i, pos in enumerate(xrange(start_pos, end_pos, stride)):
        trace_header_values[i] = binary_reader(pos)
    return trace_header_values


# TODO: Get the parameter ordering of reel_header and f to be consistent
def read_all_trace_headers(f, reel_header):
    trace_headers = {'filename': reel_header["filename"]}

    logger.debug('read_all_trace_headers : '
                 'trying to get all segy trace headers')

    for key in TRACE_HEADER_DEF.keys():
        trace_header = read_trace_header(f, reel_header, key)
        trace_headers[key] = trace_header
        logger.info("read_all_trace_headers :  " + key)

    return trace_headers


def file_length(f):
    pos = f.tell()
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    f.seek(pos, os.SEEK_SET)
    return file_size


def _filename(f):
    return f.name if hasattr(f, 'name') else '<unknown>'


def read_segy(f, endian='>'):
    """
    data, header, trace_headers = read_reel_header(f)
    """

    # data = open(filename, 'rb').read()

    filename = _filename(f)
    file_size = file_length(f)

    # file_size = len(data)
    logger.debug("readSegy : Length of data : {0}".format(file_size))

    reel_header = read_reel_header(f,
                                   endian)  # modified by A Squelch

    # GET TRACE
    index = REEL_HEADER_NUM_BYTES
    bytes_per_sample = get_byte_per_sample(reel_header)
    num_data = (file_size - REEL_HEADER_NUM_BYTES) / bytes_per_sample

    data, reel_header, trace_headers = read_traces(f,
                                                   reel_header,
                                                   num_data,
                                                   bytes_per_sample,
                                                   index,
                                                   endian)

    logger.debug("readSegy :  Read segy data")  # modified by A Squelch

    return data, reel_header, trace_headers


def read_traces(f,
                reel_header,
                num_data,
                bytes_per_sample,
                index,
                endian='>'):  # added by A Squelch
    """Read the trace data.

    values, SegyHeader, SegyTraceHeaders = read_traces(data,
                                                       reel_header,
                                                       num_data,
                                                       bytes_per_sample,
                                                       index)
    """

    # Calculate number of dummy samples needed to account for Trace Headers
    num_dummy_samples = TRACE_HEADER_NUM_BYTES / bytes_per_sample
    logger.debug("read_traces : num_dummy_samples = " + str(num_dummy_samples))

    # READ ALL SEGY TRACE HEADERS
    trace_headers = read_all_trace_headers(f, reel_header)

    logger.info("read_traces : Reading segy data")

    dsf = reel_header["DataSampleFormat"]
    ctype = DATA_SAMPLE_FORMAT[dsf]
    description = CTYPE_DESCRIPTION[ctype]
    logger.debug("read_traces : Assuming DSF = {0}, {1}".format(
        dsf, description))
    values, _ = read_binary_value(f, index, ctype, endian, num_data)

    logger.debug("read_traces : - reshaping")
    values = reshape(values,
                     (reel_header['ntraces'],
                      reel_header['ns'] + num_dummy_samples))
    logger.debug("read_traces : - stripping header dummy data")
    values = values[:, num_dummy_samples:
                    (reel_header['ns'] + num_dummy_samples)]
    logger.debug("read_traces : - transposing")
    values = transpose(values)

    # SOMEONE NEEDS TO IMPLEMENT A NICER WAY DO DEAL WITH DSF = 8
    if reel_header["DataSampleFormat"] == 8:
        for i in arange(reel_header['ntraces']):
            for j in arange(reel_header['ns']):
                if values[i][j] > 128:
                    values[i][j] = values[i][j] - 256

    logger.debug("read_traces : Finished reading segy data")

    return values, reel_header, trace_headers


def read_reel_header(f, endian='>'):
    """
    reel_header = read_reel_header(file_handle)
    """
    filename = _filename(f)
    reel_header = {'filename': filename}
    for key in HEADER_DEF.keys():
        pos = HEADER_DEF[key]["pos"]
        format = HEADER_DEF[key]["type"]

        reel_header[key], index = read_binary_value(f, pos, format, endian)

        logger.debug(str(pos) + " " +
                     str(format) +
                     "  Reading " + key +
                     "=" + str(reel_header[key]))

    # SET NUMBER OF BYTES PER DATA SAMPLE
    bps = get_byte_per_sample(reel_header)

    file_size = file_length(f)
    ntraces = (file_size - REEL_HEADER_NUM_BYTES) / \
              (reel_header['ns'] * bps + TRACE_HEADER_NUM_BYTES)
    reel_header["ntraces"] = ntraces

    logger.debug('read_reel_header : successfully read ' + filename)

    return reel_header


def write_segy(filename, data, dt=1000, trace_header_in=None, header_in=None):
    """
    write_segy(filename, data, dt)

    Write SEGY

    See also read_segy

    (c) 2005, Thomas Mejer Hansen

    MAKE OPTIONAL INPUT FOR ALL SEGYHTRACEHEADER VALUES

    """
    if header_in is None:
        header_in = {}
    if trace_header_in is None:
        trace_header_in = {}

    logger.debug("writeSegy : Trying to write " + filename)

    N = data.shape
    ns = N[0]
    ntraces = N[1]
    print ntraces, ns

    header = get_default_segy_header(ntraces, ns)
    trace_header = get_default_segy_trace_headers(ntraces, ns, dt)

    # Add trace_header_in, if exists...
    for key in trace_header_in.keys():
        print key
        for a in range(ntraces):
            trace_header[key] = trace_header_in[key][a]

    # Add header_in, if exists...
    for key in header_in.keys():
        print key
        header[key] = header_in[key]

    write_segy_structure(filename, data, header, trace_header)


def write_segy_structure(filename,
                         data,
                         header,
                         trace_header,
                         endian='>'):  # modified by A Squelch
    """
    writeSegyStructure(filename, data, header, trace_header)

    Write SEGY file using SegyPy data structures

    See also readSegy

    (c) 2005, Thomas Mejer Hansen

    """

    logger.debug("writeSegyStructure : Trying to write " + filename)

    f = open(filename, 'wb')

    # VERBOSE INF
    revision = canonicalize_revision(header["SegyFormatRevisionNumber"])
    dsf = header["DataSampleFormat"]

    try:  # block added by A Squelch
        data_descriptor = HEADER_DEF["DataSampleFormat"]["descr"][revision][dsf]
    except KeyError:
        logging.critical("  An error has occurred interpreting a SEGY binary"
                         "header key")
        logging.critical("  Please check the Endian setting for this "
                         "file: {0}".format(header["filename"]))
        sys.exit()

    logger.debug("writeSegyStructure : SEG-Y revision = " + str(revision))
    logger.debug("writeSegyStructure : DataSampleFormat = " +
                 str(dsf) +
                 "(" + data_descriptor + ")")

    # WRITE SEGY HEADER

    for key in HEADER_DEF.keys():
        pos = HEADER_DEF[key]["pos"]
        format = HEADER_DEF[key]["type"]
        value = header[key]
        put_value(value, f, pos, format, endian)

    # SEGY TRACES
    ctype = HEADER_DEF['DataSampleFormat']['datatype'][revision][dsf]
    bps = HEADER_DEF['DataSampleFormat']['bps'][revision][dsf]

    sizeT = TRACE_HEADER_NUM_BYTES + header['ns'] * bps

    for itrace in range(header['ntraces']):
        index = REEL_HEADER_NUM_BYTES + itrace * sizeT
        logger.debug('Writing Trace #' +
                     str(itrace + 1) +
                     '/' + str(header['ntraces']))
        # WRITE SEGY TRACE HEADER
        for key in TRACE_HEADER_DEF.keys():
            pos = index + TRACE_HEADER_DEF[key]["pos"]
            format = TRACE_HEADER_DEF[key]["type"]
            value = trace_header[key][itrace]
            logger.debug(str(pos) + " " +
                         str(format) +
                         "  Writing " + key +
                         "=" + str(value))
            put_value(value, f, pos, format, endian)

        # Write Data
        cformat = endian + ctype
        for s in range(header['ns']):
            strVal = struct.pack(cformat, data[s, itrace])
            f.seek(index +
                   TRACE_HEADER_NUM_BYTES +
                   s * struct.calcsize(cformat))
            f.write(strVal)

    f.close()


def put_value(value, fileid, index, ctype='l', endian='>', number=1):
    """
    putValue(data, index, ctype, endian, number)
    """
    ctype = CTYPES[ctype]

    cformat = endian + ctype*number

    logger.debug('putValue : cformat :  ' + cformat + ' ctype = ' + ctype)

    strVal = struct.pack(cformat, value)
    fileid.seek(index)
    fileid.write(strVal)

    return 1


def create_binary_reader(f, ctype='l', endian='>'):
    """Create a unary callable which reads a given binary data type from a file.
    """
    ctype = CTYPES[ctype]
    size = size_in_bytes(ctype)

    cformat = endian + ctype

    def reader(index):
        f.seek(index, os.SEEK_SET)
        data = f.read(size)
        # TODO: Check the content of data before proceeding
        value = struct.unpack(cformat, data)
        return value[0]

    return reader


def read_binary_value(f, index, ctype='l', endian='>', number=1):
    """
    read_binary_value(data, index, ctype, endian, number)
    """

    ctype = CTYPES[ctype]

    size = size_in_bytes(ctype)

    cformat = endian + ctype * number

    logger.debug('read_binary_value : cformat :  ' + cformat)

    index_end = index + size * number

    f.seek(index, os.SEEK_SET)
    data = f.read(size * number)
    if ctype == 'ibm':
        # ASSUME IBM FLOAT DATA
        value = range(number)
        for i in arange(number):
            index_ibm = i * 4
            value[i] = ibm2ieee2(data[index_ibm: index_ibm + 4])
        # this returns an array as opposed to a tuple
    else:
        # TODO: Check the content of data before proceeding
        value = struct.unpack(cformat, data)

    if ctype == 'B':
        logger.warning('read_binary_value : '
                       'Inefficient use of 1 byte Integer...', 1)

    logger.debug('read_binary_value : ' +
                 'start = ' + str(index) +
                 ' size = ' + str(size) +
                 ' number = ' + str(number) +
                 ' value = ' + str(value) +
                 ' cformat = ' + str(cformat))

    if number == 1:
        return value[0], index_end
    else:
        return value, index_end


def get_byte_per_sample(header):
    revision = canonicalize_revision(header["SegyFormatRevisionNumber"])
    dsf = header["DataSampleFormat"]

    try:  # block added by A Squelch
        bps = HEADER_DEF["DataSampleFormat"]["bps"][revision][dsf]
    except KeyError:
        # TODO: This should not be a critical failure - should just convert
        # exception
        logging.critical("  An error has occurred interpreting a SEGY "
                         "binary header key")
        logging.critical("Please check the Endian setting for "
                         "this file: {0}".format(header["filename"]))
        sys.exit()

    logger.debug("getBytePerSample :  bps = " + str(bps))

    return bps


def main():
    filename = r'C:\Users\rjs\opendtectroot\Blake_Ridge_Hydrates_3D' \
               r'\stack_final_scaled50_int8.sgy'
    with open(filename, 'rb') as segy:
        data, header, trace_header = read_segy(segy)


if __name__ == '__main__':
    main()
