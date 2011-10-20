"""
SEG Y Header Definition
"""

from revisions import SEGY_REVISION_0, SEGY_REVISION_1

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
