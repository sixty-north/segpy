
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

logger = logging.getLogger('segpy.segypy')

# SOME GLOBAL PARAMETERS
version = '0.3.1'   # modified by A Squelch

SEGY_REVISION_0 = 0x0000
SEGY_REVISION_1 = 0x0100

REEL_HEADER_NUM_BYTES = 3600
TRACE_HEADER_NUM_BYTES = 240

l_char = struct.calcsize('c')
l_uchar = struct.calcsize('B')
l_float = struct.calcsize('f')


CTYPES = {'l': 'l', 'long': 'l', 'int32': 'l',
          'L': 'L', 'ulong': 'L', 'uint32': 'L',
          'h': 'h', 'short': 'h', 'int16': 'h',
          'H': 'H', 'ushort': 'H', 'uint16': 'H',
          'c': 'c', 'char': 'c',
          'B': 'B', 'uchar': 'B',
          'f': 'f', 'float': 'f',
          'ibm': None}

def size_in_bytes(ctype):
    return struct.calcsize(ctype) if ctype != 'ibm' else struct.calcsize('f')

##############
# INIT

##############
#  Initialize SEGY HEADER 
SH_def = {"Job": {"pos": 3200, "type": "int32", "def": 0}}
SH_def["Line"]=            {"pos": 3204, "type": "int32", "def": 0}
SH_def["Reel"]=            {"pos": 3208, "type": "int32", "def": 0}
SH_def["DataTracePerEnsemble"]=    {"pos": 3212, "type": "int16", "def": 0}
SH_def["AuxiliaryTracePerEnsemble"] = {"pos": 3214, "type": "int16", "def": 0}
SH_def["dt"]=            {"pos": 3216, "type": "uint16", "def": 1000}
SH_def["dtOrig"]=        {"pos": 3218, "type": "uint16", "def": 1000}
SH_def["ns"] = {"pos": 3220, "type": "uint16", "def": 0}
SH_def["nsOrig"] = {"pos": 3222, "type": "uint16", "def": 0}
SH_def["DataSampleFormat"] = {"pos": 3224, "type": "int16", "def": 5}
SH_def["DataSampleFormat"]["descr"] = {SEGY_REVISION_0: {
    1: "IBM Float", 
    2: "32 bit Integer", 
    3: "16 bit Integer", 
    8: "8 bit Integer"}}

SH_def["DataSampleFormat"]["descr"][SEGY_REVISION_1] = {
    1: "IBM Float", 
    2: "32 bit Integer", 
    3: "16 bit Integer", 
    5: "IEEE",
    8: "8 bit Integer"}

SH_def["DataSampleFormat"]["bps"] = {SEGY_REVISION_0: {
    1: 4, 
    2: 4, 
    3: 2, 
    8: 1}}
SH_def["DataSampleFormat"]["bps"][SEGY_REVISION_1] = {
    1: 4, 
    2: 4, 
    3: 2, 
    5: 4, 
    8: 1}
SH_def["DataSampleFormat"]["datatype"] = {SEGY_REVISION_0: {
    1: 'ibm', 
    2: 'l', 
    3: 'h', 
    8: 'B'}}
SH_def["DataSampleFormat"]["datatype"][SEGY_REVISION_1] = {
    1: 'ibm', 
    2: 'l', 
    3: 'h', 
#    5: 'float', 
    5: 'f', 
    8: 'B'}

SH_def["EnsembleFold"] = {"pos": 3226, "type": "int16", "def": 0}
SH_def["TraceSorting"] = {"pos": 3228, "type": "int16", "def": 0}
SH_def["VerticalSumCode"] = {"pos": 3230, "type": "int16", "def": 0}
SH_def["SweepFrequencyEnd"] = {"pos": 3234, "type": "int16", "def": 0}
SH_def["SweepLength"] = {"pos": 3236, "type": "int16", "def": 0}
SH_def["SweepType"] = {"pos": 3238, "type": "int16", "def": 0}
SH_def["SweepChannel"] = {"pos": 3240, "type": "int16", "def": 0}
SH_def["SweepTaperLengthStart"] = {"pos": 3242, "type": "int16", "def": 0}
SH_def["SweepTaperLengthEnd"] = {"pos": 3244, "type": "int16", "def": 0}
SH_def["TaperType"] = {"pos": 3246, "type": "int16", "def": 0}
SH_def["CorrelatedDataTraces"] = {"pos": 3248, "type": "int16", "def": 0}
SH_def["BinaryGain"] = {"pos": 3250, "type": "int16", "def": 0}
SH_def["AmplitudeRecoveryMethod"] = {"pos": 3252, "type": "int16", "def": 0}
SH_def["MeasurementSystem"] = {"pos": 3254, "type": "int16", "def": 0}
SH_def["ImpulseSignalPolarity"] = {"pos": 3256, "type": "int16", "def": 0}
SH_def["VibratoryPolarityCode"] = {"pos": 3258, "type": "int16", "def": 0}
SH_def["Unassigned1"] = {"pos": 3260, "type": "int16", "n": 120, "def": 0}
SH_def["SegyFormatRevisionNumber"] = {"pos": 3500, "type": "uint16", "def": 100}
SH_def["FixedLengthTraceFlag"] = {"pos": 3502, "type": "uint16", "def": 0}
SH_def["NumberOfExtTextualHeaders"] = {"pos": 3504, "type": "uint16", "def": 0}
SH_def["Unassigned2"] = {"pos": 3506, "type": "int16", "n": 47, "def": 0}

##############
#  Initialize SEGY TRACE HEADER SPECIFICATION
STH_def = {"TraceSequenceLine": {"pos": 0, "type": "int32"}}
STH_def["TraceSequenceFile"]=    {"pos": 4, "type": "int32"}
STH_def["FieldRecord"]=        {"pos": 8, "type": "int32"}
STH_def["TraceNumber"]=        {"pos": 12, "type": "int32"}
STH_def["EnergySourcePoint"]=    {"pos": 16, "type": "int32"} 
STH_def["cdp"]=            {"pos": 20, "type": "int32"}
STH_def["cdpTrace"]=        {"pos": 24, "type": "int32"}
STH_def["TraceIdentificationCode"] = {"pos": 28 , "type": "uint16"}
STH_def["TraceIdentificationCode"]["descr"] = {SEGY_REVISION_0: {
    1: "Seismic data", 
    2: "Dead", 
    3: "Dummy", 
    4: "Time Break", 
    5: "Uphole", 
    6: "Sweep", 
    7: "Timing", 
    8: "Water Break"}}
STH_def["TraceIdentificationCode"]["descr"][SEGY_REVISION_1] = {
    -1: "Other",
     0: "Unknown",
     1: "Seismic data",
     2: "Dead",
     3: "Dummy",
     4: "Time break",
     5: "Uphole",
     6: "Sweep",
     7: "Timing",
     8: "Waterbreak",
     9: "Near-field gun signature",
    10: "Far-field gun signature",
    11: "Seismic pressure sensor",
    12: "Multicomponent seismic sensor - Vertical component",
    13: "Multicomponent seismic sensor - Cross-line component",
    14: "Multicomponent seismic sensor - In-line component",
    15: "Rotated multicomponent seismic sensor - Vertical component",
    16: "Rotated multicomponent seismic sensor - Transverse component",
    17: "Rotated multicomponent seismic sensor - Radial component",
    18: "Vibrator reaction mass",
    19: "Vibrator baseplate",
    20: "Vibrator estimated ground force",
    21: "Vibrator reference",
    22: "Time-velocity pairs"}
STH_def["NSummedTraces"] = {"pos": 30 , "type": "int16"}
STH_def["NStackedTraces"] = {"pos": 32 , "type": "int16"}
STH_def["DataUse"] = {"pos": 34 , "type": "int16"}
STH_def["DataUse"]["descr"] = {0: {
    1: "Production", 
    2: "Test"}}
STH_def["DataUse"]["descr"][1] = STH_def["DataUse"]["descr"][0]
STH_def["offset"] = {"pos": 36 , "type": "int32"}
STH_def["ReceiverGroupElevation"] = {"pos": 40 , "type": "int32"}
STH_def["SourceSurfaceElevation"] = {"pos": 44 , "type": "int32"}
STH_def["SourceDepth"] = {"pos": 48 , "type": "int32"}
STH_def["ReceiverDatumElevation"] = {"pos": 52 , "type": "int32"}
STH_def["SourceDatumElevation"] = {"pos": 56 , "type": "int32"}
STH_def["SourceWaterDepth"] = {"pos": 60 , "type": "int32"}
STH_def["GroupWaterDepth"] = {"pos": 64 , "type": "int32"}
STH_def["ElevationScalar"] = {"pos": 68 , "type": "int16"}
STH_def["SourceGroupScalar"] = {"pos": 70 , "type": "int16"}
STH_def["SourceX"] = {"pos": 72 , "type": "int32"}
STH_def["SourceY"] = {"pos": 76 , "type": "int32"}
STH_def["GroupX"] = {"pos": 80 , "type": "int32"}
STH_def["GroupY"] = {"pos": 84 , "type": "int32"}
STH_def["CoordinateUnits"] = {"pos": 88 , "type": "int16"}
STH_def["CoordinateUnits"]["descr"] = {SEGY_REVISION_0: {
    1: "Length (meters or feet)",
    2: "Seconds of arc"}}
STH_def["CoordinateUnits"]["descr"][SEGY_REVISION_1] = {
    1: "Length (meters or feet)",
    2: "Seconds of arc",
    3: "Decimal degrees",
    4: "Degrees, minutes, seconds (DMS)"}    
STH_def["WeatheringVelocity"] = {"pos": 90 , "type": "int16"}
STH_def["SubWeatheringVelocity"] = {"pos": 92 , "type": "int16"}
STH_def["SourceUpholeTime"] = {"pos": 94 , "type": "int16"}
STH_def["GroupUpholeTime"] = {"pos": 96 , "type": "int16"}
STH_def["SourceStaticCorrection"] = {"pos": 98 , "type": "int16"}
STH_def["GroupStaticCorrection"] = {"pos": 100 , "type": "int16"}
STH_def["TotalStaticApplied"] = {"pos": 102 , "type": "int16"}
STH_def["LagTimeA"] = {"pos": 104 , "type": "int16"}
STH_def["LagTimeB"] = {"pos": 106 , "type": "int16"}
STH_def["DelayRecordingTime"] = {"pos": 108 , "type": "int16"}
STH_def["MuteTimeStart"] = {"pos": 110 , "type": "int16"}
STH_def["MuteTimeEND"] = {"pos": 112 , "type": "int16"}
STH_def["ns"] = {"pos": 114 , "type": "uint16"}
STH_def["dt"] = {"pos": 116 , "type": "uint16"}
STH_def["GainType"] = {"pos": 119 , "type": "int16"}
STH_def["GainType"]["descr"] = {SEGY_REVISION_0: {
    1: "Fixes", 
    2: "Binary",
    3: "Floating point"}}
STH_def["GainType"]["descr"][SEGY_REVISION_1] = STH_def["GainType"]["descr"][SEGY_REVISION_0]
STH_def["InstrumentGainConstant"] = {"pos": 120 , "type": "int16"}
STH_def["InstrumentInitialGain"] = {"pos": 122 , "type": "int16"}
STH_def["Correlated"] = {"pos": 124 , "type": "int16"}
STH_def["Correlated"]["descr"] = {SEGY_REVISION_0: {
    1: "No", 
    2: "Yes"}}
STH_def["Correlated"]["descr"][SEGY_REVISION_1] = STH_def["Correlated"]["descr"][SEGY_REVISION_0]

STH_def["SweepFrequencyStart"] = {"pos": 126 , "type": "int16"}
STH_def["SweepFrequencyEnd"] = {"pos": 128 , "type": "int16"}
STH_def["SweepLength"] = {"pos": 130 , "type": "int16"}
STH_def["SweepType"] = {"pos": 132 , "type": "int16"}
STH_def["SweepType"]["descr"] = {SEGY_REVISION_0: {
    1: "linear", 
    2: "parabolic",
    3: "exponential",
    4: "other"}}
STH_def["SweepType"]["descr"][SEGY_REVISION_1] = STH_def["SweepType"]["descr"][SEGY_REVISION_0]

STH_def["SweepTraceTaperLengthStart"] = {"pos": 134 , "type": "int16"}
STH_def["SweepTraceTaperLengthEnd"] = {"pos": 136 , "type": "int16"}
STH_def["TaperType"] = {"pos": 138 , "type": "int16"}
STH_def["TaperType"]["descr"] = {SEGY_REVISION_0: {
    1: "linear", 
    2: "cos2c",
    3: "other"}}
STH_def["TaperType"]["descr"][SEGY_REVISION_1] = STH_def["TaperType"]["descr"][SEGY_REVISION_0]

STH_def["AliasFilterFrequency"] = {"pos": 140 , "type": "int16"}
STH_def["AliasFilterSlope"] = {"pos": 142 , "type": "int16"}
STH_def["NotchFilterFrequency"] = {"pos": 144 , "type": "int16"}
STH_def["NotchFilterSlope"] = {"pos": 146 , "type": "int16"}
STH_def["LowCutFrequency"] = {"pos": 148 , "type": "int16"}
STH_def["HighCutFrequency"] = {"pos": 150 , "type": "int16"}
STH_def["LowCutSlope"] = {"pos": 152 , "type": "int16"}
STH_def["HighCutSlope"] = {"pos": 154 , "type": "int16"}
STH_def["YearDataRecorded"] = {"pos": 156 , "type": "int16"}
STH_def["DayOfYear"] = {"pos": 158 , "type": "int16"}
STH_def["HourOfDay"] = {"pos": 160 , "type": "int16"}
STH_def["MinuteOfHour"] = {"pos": 162 , "type": "int16"}
STH_def["SecondOfMinute"] = {"pos": 164 , "type": "int16"}
STH_def["TimeBaseCode"] = {"pos": 166 , "type": "int16"}
STH_def["TimeBaseCode"]["descr"] = {SEGY_REVISION_0: {
    1: "Local", 
    2: "GMT", 
    3: "Other"}}
STH_def["TimeBaseCode"]["descr"][SEGY_REVISION_1] = {
    1: "Local", 
    2: "GMT", 
    3: "Other", 
    4: "UTC"}
STH_def["TraceWeightingFactor"] = {"pos": 168 , "type": "int16"}
STH_def["GeophoneGroupNumberRoll1"] = {"pos": 170 , "type": "int16"}
STH_def["GeophoneGroupNumberFirstTraceOrigField"] = {"pos": 172 , "type": "int16"}
STH_def["GeophoneGroupNumberLastTraceOrigField"] = {"pos": 174 , "type": "int16"}
STH_def["GapSize"] = {"pos": 176 , "type": "int16"}
STH_def["OverTravel"] = {"pos": 178 , "type": "int16"}
STH_def["OverTravel"]["descr"] = {SEGY_REVISION_0: {
    1: "down (or behind)", 
    2: "up (or ahead)",
    3: "other"}}
STH_def["OverTravel"]["descr"][SEGY_REVISION_1] = STH_def["OverTravel"]["descr"][SEGY_REVISION_0]


STH_def["cdpX"] = {"pos": 180 , "type": "int32"}
STH_def["cdpY"] = {"pos": 184 , "type": "int32"}
STH_def["Inline3D"] = {"pos": 188 , "type": "int32"}
STH_def["Crossline3D"] = {"pos": 192 , "type": "int32"}
STH_def["ShotPoint"] = {"pos": 192 , "type": "int32"}
STH_def["ShotPointScalar"] = {"pos": 200 , "type": "int16"}
STH_def["TraceValueMeasurementUnit"] = {"pos": 202 , "type": "int16"}
STH_def["TraceValueMeasurementUnit"]["descr"] = {SEGY_REVISION_1: {
    -1: "Other", 
    0: "Unknown (should be described in Data Sample Measurement Units Stanza) ", 
    1: "Pascal (Pa)", 
    2: "Volts (V)", 
    3: "Millivolts (v)", 
    4: "Amperes (A)",
    5: "Meters (m)", 
    6: "Meters Per Second (m/s)", 
    7: "Meters Per Second squared (m/&s2)Other", 
    8: "Newton (N)", 
    9: "Watt (W)"}}
STH_def["TransductionConstantMantissa"] = {"pos": 204 , "type": "int32"}
STH_def["TransductionConstantPower"] = {"pos": 208 , "type": "int16"}
STH_def["TransductionUnit"] = {"pos": 210 , "type": "int16"}
STH_def["TransductionUnit"]["descr"]  = STH_def["TraceValueMeasurementUnit"]["descr"] 
STH_def["TraceIdentifier"] = {"pos": 212 , "type": "int16"}
STH_def["ScalarTraceHeader"] = {"pos": 214 , "type": "int16"}
STH_def["SourceType"] = {"pos": 216 , "type": "int16"}
STH_def["SourceType"]["descr"] = {SEGY_REVISION_1: {
    -1: "Other (should be described in Source Type/Orientation stanza)",
     0: "Unknown",
     1: "Vibratory - Vertical orientation",
     2: "Vibratory - Cross-line orientation",
     3: "Vibratory - In-line orientation",
     4: "Impulsive - Vertical orientation",
     5: "Impulsive - Cross-line orientation",
     6: "Impulsive - In-line orientation",
     7: "Distributed Impulsive - Vertical orientation",
     8: "Distributed Impulsive - Cross-line orientation",
     9: "Distributed Impulsive - In-line orientation"}}

STH_def["SourceEnergyDirectionMantissa"] = {"pos": 218 , "type": "int32"}
STH_def["SourceEnergyDirectionExponent"] = {"pos": 222 , "type": "int16"}
STH_def["SourceMeasurementMantissa"] = {"pos": 224 , "type": "int32"}
STH_def["SourceMeasurementExponent"] = {"pos": 228 , "type": "int16"}
STH_def["SourceMeasurementUnit"] = {"pos": 230 , "type": "int16"}
STH_def["SourceMeasurementUnit"]["descr"] = {1: {
    -1: "Other (should be described in Source Measurement Unit stanza)",
     0: "Unknown",
     1: "Joule (J)",
     2: "Kilowatt (kW)",
     3: "Pascal (Pa)",
     4: "Bar (Bar)",
     5: "Newton (N)",
     6: "Kilograms (kg)"}}
STH_def["UnassignedInt1"] = {"pos": 232 , "type": "int32"}
STH_def["UnassignedInt2"] = {"pos": 236 , "type": "int32"}


##############
# FUNCTIONS



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

    if SH["DataSampleFormat"] == 1:
        logger.debug("readSegyData : Assuming DSF = 1, IBM FLOATS")
        Data1 = getValue(data, index, 'ibm', endian, nd)
    elif SH["DataSampleFormat"] == 2:
        logger.debug("readSegyData : Assuming DSF = " + str(SH["DataSampleFormat"]) + ", 32bit INT")
        Data1 = getValue(data, index, 'l', endian, nd)
    elif SH["DataSampleFormat"] == 3:
        logger.debug("readSegyData : Assuming DSF = " + str(SH["DataSampleFormat"]) + ", 16bit INT")
        Data1 = getValue(data, index, 'h', endian, nd)
    elif SH["DataSampleFormat"] == 5:
        logger.debug("readSegyData : Assuming DSF = " + str(SH["DataSampleFormat"]) + ", IEEE")
        Data1 = getValue(data, index, 'float', endian, nd)
    elif SH["DataSampleFormat"] == 8:
        logger.debug("readSegyData : Assuming DSF = " + str(SH["DataSampleFormat"]) + ", 8bit CHAR")
        Data1 = getValue(data, index, 'B', endian, nd)
    else:
        logger.debug("readSegyData : DSF = " + str(SH["DataSampleFormat"]) + ", NOT SUPPORTED")

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
