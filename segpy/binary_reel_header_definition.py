"""
SEG Y Header Definition
"""

from segpy.revisions import SEGY_REVISION_0, SEGY_REVISION_1

HEADER_DEF = {"Job": {"pos": 3200, "type": "int32", "def": 0}}
HEADER_DEF["Line"] = {"pos": 3204, "type": "int32", "def": 0}
HEADER_DEF["Reel"] = {"pos": 3208, "type": "int32", "def": 0}
HEADER_DEF["DataTracePerEnsemble"] = {"pos": 3212, "type": "int16", "def": 0}
HEADER_DEF["AuxiliaryTracePerEnsemble"] = {"pos": 3214, "type": "int16", "def": 0}
HEADER_DEF["dt"] = {"pos": 3216, "type": "uint16", "def": 1000}
HEADER_DEF["dtOrig"] = {"pos": 3218, "type": "uint16", "def": 1000}
HEADER_DEF["ns"] = {"pos": 3220, "type": "uint16", "def": 0}
HEADER_DEF["nsOrig"] = {"pos": 3222, "type": "uint16", "def": 0}
HEADER_DEF["DataSampleFormat"] = {"pos": 3224, "type": "int16", "def": 5}
HEADER_DEF["DataSampleFormat"]["descr"] = {SEGY_REVISION_0: {
    1: "IBM Float",
    2: "32 bit Integer",
    3: "16 bit Integer",
    8: "8 bit Integer"}}

HEADER_DEF["DataSampleFormat"]["descr"][SEGY_REVISION_1] = {
    1: "IBM Float",
    2: "32 bit Integer",
    3: "16 bit Integer",
    5: "IEEE",
    8: "8 bit Integer"}

HEADER_DEF["DataSampleFormat"]["bps"] = {SEGY_REVISION_0: {
    1: 4,
    2: 4,
    3: 2,
    8: 1}}
HEADER_DEF["DataSampleFormat"]["bps"][SEGY_REVISION_1] = {
    1: 4,
    2: 4,
    3: 2,
    5: 4,
    8: 1}
HEADER_DEF["DataSampleFormat"]["datatype"] = {SEGY_REVISION_0: {
    1: 'ibm',
    2: 'l',
    3: 'h',
    8: 'B'}}
HEADER_DEF["DataSampleFormat"]["datatype"][SEGY_REVISION_1] = {
    1: 'ibm',
    2: 'l',
    3: 'h',
    5: 'f',
    8: 'B'}

HEADER_DEF["EnsembleFold"] = {"pos": 3226, "type": "int16", "def": 0}
HEADER_DEF["TraceSorting"] = {"pos": 3228, "type": "int16", "def": 0}
HEADER_DEF["VerticalSumCode"] = {"pos": 3230, "type": "int16", "def": 0}
HEADER_DEF["SweepFrequencyStart"] = {"pos": 3232, "type": "int16", "def": 0}
HEADER_DEF["SweepFrequencyEnd"] = {"pos": 3234, "type": "int16", "def": 0}
HEADER_DEF["SweepLength"] = {"pos": 3236, "type": "int16", "def": 0}
HEADER_DEF["SweepType"] = {"pos": 3238, "type": "int16", "def": 0}
HEADER_DEF["SweepChannel"] = {"pos": 3240, "type": "int16", "def": 0}
HEADER_DEF["SweepTaperLengthStart"] = {"pos": 3242, "type": "int16", "def": 0}
HEADER_DEF["SweepTaperLengthEnd"] = {"pos": 3244, "type": "int16", "def": 0}
HEADER_DEF["TaperType"] = {"pos": 3246, "type": "int16", "def": 0}
HEADER_DEF["CorrelatedDataTraces"] = {"pos": 3248, "type": "int16", "def": 0}
HEADER_DEF["BinaryGain"] = {"pos": 3250, "type": "int16", "def": 0}
HEADER_DEF["AmplitudeRecoveryMethod"] = {"pos": 3252, "type": "int16", "def": 0}
HEADER_DEF["MeasurementSystem"] = {"pos": 3254, "type": "int16", "def": 0}
HEADER_DEF["ImpulseSignalPolarity"] = {"pos": 3256, "type": "int16", "def": 0}
HEADER_DEF["VibratoryPolarityCode"] = {"pos": 3258, "type": "int16", "def": 0}
HEADER_DEF["Unassigned1"] = {"pos": 3260, "type": "int16", "n": 120, "def": 0}
HEADER_DEF["SegyFormatRevisionNumber"] = {
    "pos": 3500, "type": "uint16", "def": 100}
HEADER_DEF["FixedLengthTraceFlag"] = {"pos": 3502, "type": "uint16", "def": 0}
HEADER_DEF["NumberOfExtTextualHeaders"] = {"pos": 3504, "type": "uint16", "def": 0}
HEADER_DEF["Unassigned2"] = {"pos": 3506, "type": "int16", "n": 47, "def": 0}
