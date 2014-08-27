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

from revisions import SEGY_REVISION_1
from header_definition import SH_def
from trace_header_definition import STH_def
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
    SH = getDefaultSegyHeader()
    """
    # TraceSequenceLine
    SH = {"Job": {"pos": 3200, "type": "int32", "def": 0}}

    for key in SH_def.keys():

        tmpkey = SH_def[key]
        if 'def' in tmpkey:
            val = tmpkey['def']
        else:
            val = 0
        SH[key] = val

    SH["ntraces"] = ntraces
    SH["ns"] = ns

    return SH


def get_default_segy_trace_headers(ntraces=100, ns=100, dt=1000):
    """
    SH = getDefaultSegyTraceHeader()
    """
    # INITIALIZE DICTIONARY
    STH = {"TraceSequenceLine": {"pos": 0, "type": "int32"}}

    for key in STH_def.keys():

        tmpkey = STH_def[key] # TODO: What is going on here?
        STH[key] = zeros(ntraces)

    for a in range(ntraces):
        STH["TraceSequenceLine"][a] = a + 1
        STH["TraceSequenceFile"][a] = a + 1
        STH["FieldRecord"][a] = 1000
        STH["TraceNumber"][a] = a + 1
        STH["ns"][a] = ns
        STH["dt"][a] = dt
    return STH


def read_trace_header(f, reel_header, trace_header_name='cdp', endian='>'):
    """
    read_trace_header(reel_header, TraceHeaderName)
    """

    bps = get_byte_per_sample(reel_header)

    # MAKE SOME LOOKUP TABLE THAT HOLDS THE LOCATION OF HEADERS
    trace_header_pos = STH_def[trace_header_name]["pos"]

    # TODO: Be consistent between 'type' and 'format' here.
    trace_header_format = STH_def[trace_header_name]["type"]
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

    for key in STH_def.keys():
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


def read_segy(f, filename, endian='>'):
    """
    Data, SegyHeader, trace_headers = read_reel_header(f)
    """

    # data = open(filename, 'rb').read()

    file_size = file_length(f)

    # file_size = len(data)
    logger.debug("readSegy : Length of data : {0}".format(file_size))

    reel_header = read_reel_header(f,
                                   filename,
                                   endian)  # modified by A Squelch

    # GET TRACE
    index = REEL_HEADER_NUM_BYTES
    bytes_per_sample = get_byte_per_sample(reel_header)
    num_data = (file_size - REEL_HEADER_NUM_BYTES) / bytes_per_sample

    Data, reel_header, trace_headers = read_traces(f,
                                                   reel_header,
                                                   num_data,
                                                   bytes_per_sample,
                                                   index,
                                                   endian)

    logger.debug("readSegy :  Read segy data")  # modified by A Squelch

    return Data, reel_header, trace_headers


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


def read_reel_header(f, filename, endian='>'):
    """
    reel_header = read_reel_header(filename)
    """
    # data = open(filename, 'rb').read()

    reel_header = {'filename': filename}
    for key in SH_def.keys():
        pos = SH_def[key]["pos"]
        format = SH_def[key]["type"]

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


def write_segy(filename, Data, dt=1000, STHin=None, SHin=None):
    """
    writeSegy(filename, Data, dt)

    Write SEGY

    See also readSegy

    (c) 2005, Thomas Mejer Hansen

    MAKE OPTIONAL INPUT FOR ALL SEGYHTRACEHEADER VALUES

    """
    if SHin is None: SHin = {}
    if STHin is None: STHin = {}

    logger.debug("writeSegy : Trying to write " + filename)

    N = Data.shape
    ns = N[0]
    ntraces = N[1]
    print ntraces, ns

    SH = get_default_segy_header(ntraces, ns)
    STH = get_default_segy_trace_headers(ntraces, ns, dt)

    # ADD STHin, if exists...
    for key in STHin.keys():
        print key
        for a in range(ntraces):
            STH[key] = STHin[key][a]

    # ADD SHin, if exists...
    for key in SHin.keys():
        print key
        SH[key] = SHin[key]

    write_segy_structure(filename, Data, SH, STH)


def write_segy_structure(filename,
                         Data,
                         SH,
                         STH,
                         endian='>'):  # modified by A Squelch
    """
    writeSegyStructure(filename, Data, SegyHeader, SegyTraceHeaders)

    Write SEGY file using SegyPy data structures

    See also readSegy

    (c) 2005, Thomas Mejer Hansen

    """

    logger.debug("writeSegyStructure : Trying to write " + filename)

    f = open(filename, 'wb')

    # VERBOSE INF
    revision = SH["SegyFormatRevisionNumber"]
    dsf = SH["DataSampleFormat"]

    try:  # block added by A Squelch
        DataDescr = SH_def["DataSampleFormat"]["descr"][revision][dsf]
    except KeyError:
        logging.critical("  An error has ocurred interpreting a SEGY binary"
                         "header key")
        logging.critical("  Please check the Endian setting for this "
                         "file: {0}".format(SH["filename"]))
        sys.exit()

    logger.debug("writeSegyStructure : SEG-Y revision = " + str(revision))
    logger.debug("writeSegyStructure : DataSampleFormat = " +
                 str(dsf) +
                 "(" + DataDescr + ")")

    # WRITE SEGY HEADER

    for key in SH_def.keys():
        pos = SH_def[key]["pos"]
        format = SH_def[key]["type"]
        value = SH[key]
        put_value(value, f, pos, format, endian)

    # SEGY TRACES
    ctype = SH_def['DataSampleFormat']['datatype'][revision][dsf]
    bps = SH_def['DataSampleFormat']['bps'][revision][dsf]

    sizeT = TRACE_HEADER_NUM_BYTES + SH['ns'] * bps

    for itrace in range(SH['ntraces']):
        index = REEL_HEADER_NUM_BYTES + itrace * sizeT
        logger.debug('Writing Trace #' +
                     str(itrace + 1) +
                     '/' + str(SH['ntraces']))
        # WRITE SEGY TRACE HEADER
        for key in STH_def.keys():
            pos = index + STH_def[key]["pos"]
            format = STH_def[key]["type"]
            value = STH[key][itrace]
            logger.debug(str(pos) + " " +
                         str(format) +
                         "  Writing " + key +
                         "=" + str(value))
            put_value(value, f, pos, format, endian)

        # Write Data
        cformat = endian + ctype
        for s in range(SH['ns']):
            strVal = struct.pack(cformat, Data[s, itrace])
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
        Value = range(number)
        for i in arange(number):
            index_ibm = i * 4
            Value[i] = ibm2ieee2(data[index_ibm: index_ibm + 4])
        # this returns an array as opposed to a tuple
    else:
        # TODO: Check the content of data before proceeding
        Value = struct.unpack(cformat, data)

    if ctype == 'B':
        logger.warning('read_binary_value : '
                       'Inefficient use of 1 byte Integer...', 1)

    logger.debug('read_binary_value : ' +
                 'start = ' + str(index) +
                 ' size = ' + str(size) +
                 ' number = ' + str(number) +
                 ' Value = ' + str(Value) +
                 ' cformat = ' + str(cformat))

    if number == 1:
        return Value[0], index_end
    else:
        return Value, index_end


def get_byte_per_sample(SH):
    revision = SH["SegyFormatRevisionNumber"]

    if revision == 100:
        revision = SEGY_REVISION_1

    dsf = SH["DataSampleFormat"]

    try:  # block added by A Squelch
        bps = SH_def["DataSampleFormat"]["bps"][revision][dsf]
    except KeyError:
        # TODO: This should not be a critical failure - should just convert
        # exception
        logging.critical("  An error has occurred interpreting a SEGY "
                         "binary header key")
        logging.critical("Please check the Endian setting for "
                         "this file: {0}".format(SH["filename"]))
        sys.exit()

    logger.debug("getBytePerSample :  bps = " + str(bps))

    return bps

if __name__ == '__main__':
    filename = r'C:\Users\rjs\opendtectroot\Blake_Ridge_Hydrates_3D'\
               r'\stack_final_scaled50_int8.sgy'
    with open(filename, 'rb') as segy:
        Data, SH, SegyTraceHeaders = read_segy(segy, filename)
