
"""
A python module for reading/writing/manipulating
SEG-Y formatted filed

segy.readSegy                : Read SEGY file
segy.getSegyHeader           : Get SEGY header
segy.getSegyTraceHeader      : Get SEGY Trace header
segy.getAllSegyTraceHeaders  : Get all SEGY Trace headers
segy.getSegyTrace            : Get SEGY Trace header and trace data for one trace

segy.writeSegy               : Write a data to a SEGY file
segy.writeSegyStructure      : Writes a segpy data structure to a SEGY file

segy.getValue        : Get a value from a binary string
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


import sys
import struct
import logging

from numpy import transpose
from numpy import reshape
from numpy import zeros
from numpy import arange

from revisions import SEGY_REVISION_0, SEGY_REVISION_1
from header_definition import SH_def
from trace_header_definition import STH_def

logger = logging.getLogger('segpy.segypy')

version = '0.3.1'   # modified by A Squelch

REEL_HEADER_NUM_BYTES = 3600
TRACE_HEADER_NUM_BYTES = 240

l_char = struct.calcsize('c')
l_uchar = struct.calcsize('B')
l_float = struct.calcsize('f')


DATA_SAMPLE_FORMAT = { 1: 'ibm',
                       2: 'l',
                       3: 'h',
                       5: 'f',
                       8: 'B' }

CTYPES = {'l': 'l', 'long'  : 'l', 'int32':  'l',
          'L': 'L', 'ulong' : 'L', 'uint32': 'L',
          'h': 'h', 'short' : 'h', 'int16':  'h',
          'H': 'H', 'ushort': 'H', 'uint16': 'H',
          'c': 'c', 'char'  : 'c',
          'B': 'B', 'uchar' : 'B',
          'f': 'f', 'float' : 'f',
          'ibm': 'ibm'}

# TODO This is redundant with data in the SH_def below
CTYPE_DESCRIPTION = { 'ibm' : 'IBM float',
                      'l'   : '32 bit integer',
                      'h'   : '16 bit integer',
                      'f'   : 'IEEE float',
                      'B'   : '8 bit char' }

def size_in_bytes(ctype):
    return struct.calcsize(ctype) if ctype != 'ibm' else struct.calcsize('f')


def getDefaultSegyHeader(ntraces=100, ns=100):
    """Remove unused import.
    SH = getDefaultSegyHeader()
    """
    # INITIALIZE DICTIONARYTraceSequenceLine
    SH = {"Job": {"pos": 3200, "type": "int32", "def": 0}}

    for key in SH_def.keys(): 

        tmpkey = SH_def[key]
        if tmpkey.has_key('def'):
            val = tmpkey['def']
        else:
            val = 0
        SH[key] = val

    SH["ntraces"] = ntraces
    SH["ns"] = ns


    return SH


def getDefaultSegyTraceHeaders(ntraces=100, ns=100, dt=1000):
    """
    SH = getDefaultSegyTraceHeader()
    """
    # INITIALIZE DICTIONARY
    STH = {"TraceSequenceLine": {"pos": 0, "type": "int32"}}

    for key in STH_def.keys(): 

        tmpkey = STH_def[key]
        STH[key] = zeros(ntraces)

    for a in range(ntraces):            
        STH["TraceSequenceLine"][a] = a + 1
        STH["TraceSequenceFile"][a] = a + 1
        STH["FieldRecord"][a] = 1000
        STH["TraceNumber"][a] = a + 1
        STH["ns"][a] = ns
        STH["dt"][a] = dt
    return STH


def getSegyTraceHeader(SH, THN='cdp', data='none', endian='>'):  # modified by A Squelch
    """
    getSegyTraceHeader(SH, TraceHeaderName)
    """

    bps = getBytePerSample(SH)

    if data == 'none':
        data = open(SH["filename"], 'rb').read()


    # MAKE SOME LOOKUP TABLE THAT HOLDS THE LOCATION OF HEADERS
    THpos = STH_def[THN]["pos"]
    THformat = STH_def[THN]["type"]
    ntraces = SH["ntraces"]
    thv = zeros(ntraces)
    for itrace in range(1, ntraces + 1, 1):

        pos = THpos + REEL_HEADER_NUM_BYTES + (SH["ns"] * bps + TRACE_HEADER_NUM_BYTES) * (itrace - 1)

        logger.debug("getSegyTraceHeader : Reading trace header " + THN + " " + str(itrace)  + " of " + str(ntraces) + " " +str(pos))
        thv[itrace - 1], index = getValue(data, pos, THformat, endian, 1)
        logger.debug("getSegyTraceHeader : " + THN + "=" + str(thv[itrace - 1]))

    return thv


def getLastSegyTraceHeader(SH, THN='cdp', data='none', endian='>'):  # added by A Squelch
    """
    getLastSegyTraceHeader(SH, TraceHeaderName)
    """

    bps = getBytePerSample(SH)

    if data == 'none':
        data = open(SH["filename"]).read()

    # SET PARAMETERS THAT DEFINE THE LOCATION OF THE LAST HEADER
    # AND THE TRACE NUMBER KEY FIELD
    THpos = STH_def[THN]["pos"]
    THformat = STH_def[THN]["type"]
    ntraces = SH["ntraces"]

    pos = THpos + REEL_HEADER_NUM_BYTES + (SH["ns"] * bps + TRACE_HEADER_NUM_BYTES) * (ntraces - 1)

    logger.debug("getLastSegyTraceHeader : Reading last trace header " + THN + " " + str(pos))
    thv, index = getValue(data, pos, THformat, endian, 1)
    logger.debug("getLastSegyTraceHeader : " + THN + "=" + str(thv))

    return thv


def getAllSegyTraceHeaders(SH, data='none'):
    SegyTraceHeaders = {'filename': SH["filename"]}

    logger.debug('getAllSegyTraceHeaders : trying to get all segy trace headers')


    if data == 'none':
        data = open(SH["filename"], 'rb').read()

    for key in STH_def.keys():      

        sth = getSegyTraceHeader(SH, key, data)      
        SegyTraceHeaders[key] = sth

        logger.debug("getAllSegyTraceHeaders :  " + key)

    return SegyTraceHeaders


def readSegy(filename, endian='>'):  # modified by A Squelch
    """
    Data, SegyHeader, SegyTraceHeaders = getSegyHeader(filename)
    """

    logger.debug("readSegy : Trying to read " + filename)

    data = open(filename, 'rb').read()

    filesize = len(data)

    SH = getSegyHeader(filename, endian)  # modified by A Squelch

    bps = getBytePerSample(SH)

    ntraces = (filesize - REEL_HEADER_NUM_BYTES) / (SH['ns'] * bps + TRACE_HEADER_NUM_BYTES)

    logger.debug("readSegy : Length of data : " + str(filesize))

    SH["ntraces"] = ntraces

    logger.debug("readSegy : ntraces = " + str(ntraces) + " nsamples = " + str(SH['ns']))


    # GET TRACE
    index = REEL_HEADER_NUM_BYTES
    nd = (filesize - REEL_HEADER_NUM_BYTES) / bps

    Data, SH, SegyTraceHeaders = readSegyData(data, SH, nd, bps, index, endian)

    logger.debug("readSegy :  Read segy data")  # modified by A Squelch

    return Data, SH, SegyTraceHeaders    


def readSegyData(data, SH, nd, bps, index, endian='>'):  # added by A Squelch
    """
    Data, SegyHeader, SegyTraceHeaders = readSegyData(data, SH, nd, bps, index)

    This function separated out from readSegy so that it can also be
    called from other external functions - by A Squelch.
    """

    # Calculate number of dummy samples needed to account for Trace Headers
    ndummy_samples = TRACE_HEADER_NUM_BYTES / bps
    logger.debug("readSegyData : ndummy_samples = " + str(ndummy_samples))

    # READ ALL SEGY TRACE HEADERS
    STH = getAllSegyTraceHeaders(SH, data)

    logger.debug("readSegyData : Reading segy data")

    # READ ALL DATA EXCEPT FOR SEGY HEADER
    revision = SH["SegyFormatRevisionNumber"]

    dsf = SH["DataSampleFormat"]


    try:  # block added by A Squelch
        DataDescr = SH_def["DataSampleFormat"]["descr"][revision][dsf]
    except KeyError:
        # TODO: This should not be critical - we should just convert the exception
        logger.critical("  An error has occurred interpreting a SEGY binary header key")
        logger.critical("  Please check the Endian setting for this file: ", SH["filename"])
        sys.exit()

    logger.debug("readSegyData : SEG-Y revision = " + str(revision))
    logger.debug("readSegyData : DataSampleFormat = " + str(dsf) + "(" + DataDescr + ")")

    dsf = SH["DataSampleFrmat"]
    ctype = DATA_SAMPLE_FORMAT[dsf]
    description = CTYPE_DESCRIPTION[ctype]
    logger.debug("readSegyData : Assuming DSF = {0}, {1}".format(dsf, description))
    Data1 = getValue(data, index, ctype, endian, nd)

    Data = Data1[0]

    logger.debug("readSegyData : - reshaping")
    Data = reshape(Data, (SH['ntraces'], SH['ns']+ndummy_samples))
    logger.debug("readSegyData : - stripping header dummy data")
    Data = Data[: , ndummy_samples: (SH['ns']+ndummy_samples)]
    logger.debug("readSegyData : - transposing")
    Data = transpose(Data)

    # SOMEONE NEEDS TO IMPLEMENT A NICER WAY DO DEAL WITH DSF = 8
    if SH["DataSampleFormat"] == 8:
        for i in arange(SH['ntraces']):
            for j in arange(SH['ns']):
                if Data[i][j] > 128:
                    Data[i][j] = Data[i][j] - 256

    logger.debug("readSegyData : Finished reading segy data")

    return Data, SH, STH


def getSegyTrace(SH, itrace, endian='>'):  # modified by A Squelch
    """
    SegyTraceHeader, SegyTraceData = getSegyTrace(SegyHeader, itrace)
        itrace : trace number to read
        THIS DEF IS NOT UPDATED. NOT READY TO USE
    """    
    data = open(SH["filename"], 'rb').read()

    bps = getBytePerSample(SH)


    # GET TRACE HEADER
    SegyTraceHeader = []

    # GET TRACE
    index = 3200 + (itrace - 1) * (TRACE_HEADER_NUM_BYTES + SH['ns'] * bps) + TRACE_HEADER_NUM_BYTES
    SegyTraceData = getValue(data, index, 'float', endian, SH['ns'])
    return SegyTraceHeader, SegyTraceData


def getSegyHeader(filename, endian='>'):  # modified by A Squelch
    """
    SegyHeader = getSegyHeader(filename)
    """
    data = open(filename, 'rb').read()

    SegyHeader = {'filename': filename}
    for key in SH_def.keys():
        pos = SH_def[key]["pos"]
        format = SH_def[key]["type"]

        SegyHeader[key], index = getValue(data, pos, format, endian)

        logger.debug(str(pos) + " " + str(format) + "  Reading " + key + "=" + str(SegyHeader[key]))

    # SET NUMBER OF BYTES PER DATA SAMPLE
    bps = getBytePerSample(SegyHeader)

    filesize = len(data)
    ntraces = (filesize - REEL_HEADER_NUM_BYTES) / (SegyHeader['ns'] * bps + TRACE_HEADER_NUM_BYTES)
    SegyHeader["ntraces"] = ntraces

    logger.debug('getSegyHeader : successfully read ' + filename)

    return SegyHeader


def writeSegy(filename, Data, dt = 1000, STHin={}, SHin={}):
    """
    writeSegy(filename, Data, dt)

    Write SEGY 

    See also readSegy

    (c) 2005, Thomas Mejer Hansen

    MAKE OPTIONAL INPUT FOR ALL SEGYHTRACEHEADER VALUES

    """

    logger.debug("writeSegy : Trying to write " + filename)

    N = Data.shape
    ns = N[0]
    ntraces = N[1]
    print ntraces, ns

    SH = getDefaultSegyHeader(ntraces, ns)
    STH = getDefaultSegyTraceHeaders(ntraces, ns, dt)

    # ADD STHin, if exists...
    for key in STHin.keys():
        print key
        for a in range(ntraces):
            STH[key] = STHin[key][a]

    # ADD SHin, if exists...
    for key in SHin.keys():
        print key
        SH[key] = SHin[key]


    writeSegyStructure(filename, Data, SH, STH)


def writeSegyStructure(filename, Data, SH, STH, endian='>'):  # modified by A Squelch
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
        logging.critical("  An error has ocurred interpreting a SEGY binary header key")
        logging.critical("  Please check the Endian setting for this file: {0}".format(SH["filename"]))
        sys.exit()

    logger.debug("writeSegyStructure : SEG-Y revision = " + str(revision))
    logger.debug("writeSegyStructure : DataSampleFormat = " + str(dsf) + "(" + DataDescr + ")")

    # WRITE SEGY HEADER

    for key in SH_def.keys():     
        pos = SH_def[key]["pos"]
        format = SH_def[key]["type"]
        value = SH[key]
        putValue(value, f, pos, format, endian)

    # SEGY TRACES


    ctype = SH_def['DataSampleFormat']['datatype'][revision][dsf]
    bps = SH_def['DataSampleFormat']['bps'][revision][dsf]


    sizeT = TRACE_HEADER_NUM_BYTES + SH['ns'] * bps

    for itrace in range(SH['ntraces']):        
        index = REEL_HEADER_NUM_BYTES + itrace * sizeT
        logger.debug('Writing Trace #' + str(itrace + 1) + '/' + str(SH['ntraces']))
        # WRITE SEGY TRACE HEADER
        for key in STH_def.keys():     
            pos = index+STH_def[key]["pos"]
            format = STH_def[key]["type"]
            value = STH[key][itrace]
            logger.debug(str(pos) + " " + str(format) + "  Writing " + key + "=" + str(value))
            putValue(value, f, pos, format, endian)

        # Write Data    
        cformat = endian + ctype
        for s in range(SH['ns']):
            strVal = struct.pack(cformat, Data[s, itrace])
            f.seek(index + TRACE_HEADER_NUM_BYTES + s * struct.calcsize(cformat))
            f.write(strVal)

    f.close


def putValue(value, fileid, index, ctype='l', endian='>', number=1):
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


def getValue(data, index, ctype='l', endian='>', number=1):
    """
    getValue(data, index, ctype, endian, number)
    """

    ctype = CTYPES[ctype]
    size = size_in_bytes(ctype)

    cformat = endian + ctype * number

    logger.debug('getValue : cformat :  ' + cformat)

    index_end = index + size * number

    if ctype == 'ibm':
        # ASSUME IBM FLOAT DATA
        Value = range(number)        
        for i in arange(number):
            index_ibm = i * 4 + index
            Value[i] = ibm2ieee2(data[index_ibm: index_ibm + 4])
        # this returns an array as opposed to a tuple
    else:
        # ALL OTHER TYPES OF DATA
        Value = struct.unpack(cformat, data[index: index_end])

    if ctype == 'B':
        logger.warning('getValue : Inefficient use of 1 byte Integer...', 1)

    logger.debug('getValue : ' + 'start = ' + str(index) + ' size = ' + str(size) + ' number = ' + str(number) + ' Value = ' + str(Value) + ' cformat = ' + str(cformat))

    if number == 1:
        return Value[0], index_end
    else:
        return Value, index_end


##############
# MISC FUNCTIONS
def ibm2Ieee(ibm_float):
    """
    ibm2Ieee(ibm_float)
    Used by permission
    (C) Secchi Angelo
    with thanks to Howard Lightstone and Anton Vredegoor. 
    """
    i = struct.unpack('>I', ibm_float)[0]
    sign = [1, -1][bool(i & 0x100000000L)]
    characteristic = ((i >> 24) & 0x7f) - 64
    fraction = (i & 0xffffff) / float(0x1000000L)
    return sign * 16 ** characteristic * fraction



def ibm2ieee2(ibm_float):
    """
    ibm2ieee2(ibm_float)
    Used by permission
    (C) Secchi Angelo
    with thanks to Howard Lightstone and Anton Vredegoor. 
    """
    dividend = float(16 ** 6)

    if ibm_float == 0:
        return 0.0
    istic, a, b, c = struct.unpack('>BBBB', ibm_float)
    if istic >= 128:
        sign= -1.0
        istic -= 128
    else:
        sign = 1.0
    mant= float(a << 16) + float(b << 8) + float(c)
    return sign * 16 ** (istic - 64) * (mant / dividend)


def getBytePerSample(SH):
    revision = SH["SegyFormatRevisionNumber"]

    dsf = SH["DataSampleFormat"]

    try:  # block added by A Squelch
        bps = SH_def["DataSampleFormat"]["bps"][revision][dsf]
    except KeyError:
        # TODO: This should not be a critical failure - should just convert exception
        logging.critical("  An error has occurred interpreting a SEGY binary header key")
        logging.critical("Please check the Endian setting for this file: {0}".format(SH["filename"]))
        sys.exit()

    logger.debug("getBytePerSample :  bps = " + str(bps))

    return bps
