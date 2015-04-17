from segpy.revisions import SEGY_REVISION_0, SEGY_REVISION_1

TRACE_HEADER_DEF = {"TraceSequenceLine": {"pos": 0, "type": "int32"}}
TRACE_HEADER_DEF["TraceSequenceFile"] = {"pos": 4, "type": "int32"}
TRACE_HEADER_DEF["FieldRecord"] = {"pos": 8, "type": "int32"}
TRACE_HEADER_DEF["TraceNumber"] = {"pos": 12, "type": "int32"}
TRACE_HEADER_DEF["EnergySourcePoint"] = {"pos": 16, "type": "int32"}
TRACE_HEADER_DEF["cdp"] = {"pos": 20, "type": "int32"}
TRACE_HEADER_DEF["cdpTrace"] = {"pos": 24, "type": "int32"}
TRACE_HEADER_DEF["TraceIdentificationCode"] = {"pos": 28, "type": "int16"}
TRACE_HEADER_DEF["TraceIdentificationCode"]["descr"] = {SEGY_REVISION_0: {
    1: "Seismic data",
    2: "Dead",
    3: "Dummy",
    4: "Time Break",
    5: "Uphole",
    6: "Sweep",
    7: "Timing",
    8: "Water Break"}}
TRACE_HEADER_DEF["TraceIdentificationCode"]["descr"][SEGY_REVISION_1] = {
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
TRACE_HEADER_DEF["NSummedTraces"] = {"pos": 30, "type": "int16"}
TRACE_HEADER_DEF["NStackedTraces"] = {"pos": 32, "type": "int16"}
TRACE_HEADER_DEF["DataUse"] = {"pos": 34, "type": "int16"}
TRACE_HEADER_DEF["DataUse"]["descr"] = {0: {
    1: "Production",
    2: "Test"}}
TRACE_HEADER_DEF["DataUse"]["descr"][1] = TRACE_HEADER_DEF["DataUse"]["descr"][0]
TRACE_HEADER_DEF["offset"] = {"pos": 36, "type": "int32"}
TRACE_HEADER_DEF["ReceiverGroupElevation"] = {"pos": 40, "type": "int32"}
TRACE_HEADER_DEF["SourceSurfaceElevation"] = {"pos": 44, "type": "int32"}
TRACE_HEADER_DEF["SourceDepth"] = {"pos": 48, "type": "int32"}
TRACE_HEADER_DEF["ReceiverDatumElevation"] = {"pos": 52, "type": "int32"}
TRACE_HEADER_DEF["SourceDatumElevation"] = {"pos": 56, "type": "int32"}
TRACE_HEADER_DEF["SourceWaterDepth"] = {"pos": 60, "type": "int32"}
TRACE_HEADER_DEF["GroupWaterDepth"] = {"pos": 64, "type": "int32"}
TRACE_HEADER_DEF["ElevationScalar"] = {"pos": 68, "type": "int16"}
TRACE_HEADER_DEF["SourceGroupScalar"] = {"pos": 70, "type": "int16"}
TRACE_HEADER_DEF["SourceX"] = {"pos": 72, "type": "int32"}
TRACE_HEADER_DEF["SourceY"] = {"pos": 76, "type": "int32"}
TRACE_HEADER_DEF["GroupX"] = {"pos": 80, "type": "int32"}
TRACE_HEADER_DEF["GroupY"] = {"pos": 84, "type": "int32"}
TRACE_HEADER_DEF["CoordinateUnits"] = {"pos": 88, "type": "int16"}
TRACE_HEADER_DEF["CoordinateUnits"]["descr"] = {SEGY_REVISION_0: {
    1: "Length (meters or feet)",
    2: "Seconds of arc"}}
TRACE_HEADER_DEF["CoordinateUnits"]["descr"][SEGY_REVISION_1] = {
    1: "Length (meters or feet)",
    2: "Seconds of arc",
    3: "Decimal degrees",
    4: "Degrees, minutes, seconds (DMS)"}
TRACE_HEADER_DEF["WeatheringVelocity"] = {"pos": 90, "type": "int16"}
TRACE_HEADER_DEF["SubWeatheringVelocity"] = {"pos": 92, "type": "int16"}
TRACE_HEADER_DEF["SourceUpholeTime"] = {"pos": 94, "type": "int16"}
TRACE_HEADER_DEF["GroupUpholeTime"] = {"pos": 96, "type": "int16"}
TRACE_HEADER_DEF["SourceStaticCorrection"] = {"pos": 98, "type": "int16"}
TRACE_HEADER_DEF["GroupStaticCorrection"] = {"pos": 100, "type": "int16"}
TRACE_HEADER_DEF["TotalStaticApplied"] = {"pos": 102, "type": "int16"}
TRACE_HEADER_DEF["LagTimeA"] = {"pos": 104, "type": "int16"}
TRACE_HEADER_DEF["LagTimeB"] = {"pos": 106, "type": "int16"}
TRACE_HEADER_DEF["DelayRecordingTime"] = {"pos": 108, "type": "int16"}
TRACE_HEADER_DEF["MuteTimeStart"] = {"pos": 110, "type": "int16"}
TRACE_HEADER_DEF["MuteTimeEND"] = {"pos": 112, "type": "int16"}
TRACE_HEADER_DEF["ns"] = {"pos": 114, "type": "uint16"}
TRACE_HEADER_DEF["dt"] = {"pos": 116, "type": "uint16"}
TRACE_HEADER_DEF["GainType"] = {"pos": 118, "type": "int16"}
TRACE_HEADER_DEF["GainType"]["descr"] = {SEGY_REVISION_0: {
    1: "Fixes",
    2: "Binary",
    3: "Floating point"}}
TRACE_HEADER_DEF["GainType"]["descr"][SEGY_REVISION_1] = TRACE_HEADER_DEF[
    "GainType"]["descr"][SEGY_REVISION_0]
TRACE_HEADER_DEF["InstrumentGainConstant"] = {"pos": 120, "type": "int16"}
TRACE_HEADER_DEF["InstrumentInitialGain"] = {"pos": 122, "type": "int16"}
TRACE_HEADER_DEF["Correlated"] = {"pos": 124, "type": "int16"}
TRACE_HEADER_DEF["Correlated"]["descr"] = {SEGY_REVISION_0: {
    1: "No",
    2: "Yes"}}
TRACE_HEADER_DEF["Correlated"]["descr"][SEGY_REVISION_1] = TRACE_HEADER_DEF[
    "Correlated"]["descr"][SEGY_REVISION_0]

TRACE_HEADER_DEF["SweepFrequencyStart"] = {"pos": 126, "type": "int16"}
TRACE_HEADER_DEF["SweepFrequencyEnd"] = {"pos": 128, "type": "int16"}
TRACE_HEADER_DEF["SweepLength"] = {"pos": 130, "type": "int16"}
TRACE_HEADER_DEF["SweepType"] = {"pos": 132, "type": "int16"}
TRACE_HEADER_DEF["SweepType"]["descr"] = {SEGY_REVISION_0: {
    1: "linear",
    2: "parabolic",
    3: "exponential",
    4: "other"}}
TRACE_HEADER_DEF["SweepType"]["descr"][SEGY_REVISION_1] = TRACE_HEADER_DEF[
    "SweepType"]["descr"][SEGY_REVISION_0]

TRACE_HEADER_DEF["SweepTraceTaperLengthStart"] = {"pos": 134, "type": "int16"}
TRACE_HEADER_DEF["SweepTraceTaperLengthEnd"] = {"pos": 136, "type": "int16"}
TRACE_HEADER_DEF["TaperType"] = {"pos": 138, "type": "int16"}
TRACE_HEADER_DEF["TaperType"]["descr"] = {SEGY_REVISION_0: {
    1: "linear",
    2: "cos2c",
    3: "other"}}
TRACE_HEADER_DEF["TaperType"]["descr"][SEGY_REVISION_1] = TRACE_HEADER_DEF[
    "TaperType"]["descr"][SEGY_REVISION_0]

TRACE_HEADER_DEF["AliasFilterFrequency"] = {"pos": 140, "type": "int16"}
TRACE_HEADER_DEF["AliasFilterSlope"] = {"pos": 142, "type": "int16"}
TRACE_HEADER_DEF["NotchFilterFrequency"] = {"pos": 144, "type": "int16"}
TRACE_HEADER_DEF["NotchFilterSlope"] = {"pos": 146, "type": "int16"}
TRACE_HEADER_DEF["LowCutFrequency"] = {"pos": 148, "type": "int16"}
TRACE_HEADER_DEF["HighCutFrequency"] = {"pos": 150, "type": "int16"}
TRACE_HEADER_DEF["LowCutSlope"] = {"pos": 152, "type": "int16"}
TRACE_HEADER_DEF["HighCutSlope"] = {"pos": 154, "type": "int16"}
TRACE_HEADER_DEF["YearDataRecorded"] = {"pos": 156, "type": "int16"}
TRACE_HEADER_DEF["DayOfYear"] = {"pos": 158, "type": "int16"}
TRACE_HEADER_DEF["HourOfDay"] = {"pos": 160, "type": "int16"}
TRACE_HEADER_DEF["MinuteOfHour"] = {"pos": 162, "type": "int16"}
TRACE_HEADER_DEF["SecondOfMinute"] = {"pos": 164, "type": "int16"}
TRACE_HEADER_DEF["TimeBaseCode"] = {"pos": 166, "type": "int16"}
TRACE_HEADER_DEF["TimeBaseCode"]["descr"] = {SEGY_REVISION_0: {
    1: "Local",
    2: "GMT",
    3: "Other"}}
TRACE_HEADER_DEF["TimeBaseCode"]["descr"][SEGY_REVISION_1] = {
    1: "Local",
    2: "GMT",
    3: "Other",
    4: "UTC"}
TRACE_HEADER_DEF["TraceWeightingFactor"] = {"pos": 168, "type": "int16"}
TRACE_HEADER_DEF["GeophoneGroupNumberRoll1"] = {"pos": 170, "type": "int16"}
TRACE_HEADER_DEF["GeophoneGroupNumberFirstTraceOrigField"] = {
    "pos": 172, "type": "int16"}
TRACE_HEADER_DEF["GeophoneGroupNumberLastTraceOrigField"] = {
    "pos": 174, "type": "int16"}
TRACE_HEADER_DEF["GapSize"] = {"pos": 176, "type": "int16"}
TRACE_HEADER_DEF["OverTravel"] = {"pos": 178, "type": "int16"}
TRACE_HEADER_DEF["OverTravel"]["descr"] = {SEGY_REVISION_0: {
    1: "down (or behind)",
    2: "up (or ahead)",
    3: "other"}}
TRACE_HEADER_DEF["OverTravel"]["descr"][SEGY_REVISION_1] = TRACE_HEADER_DEF[
    "OverTravel"]["descr"][SEGY_REVISION_0]


TRACE_HEADER_DEF["cdpX"] = {"pos": 180, "type": "int32"}
TRACE_HEADER_DEF["cdpY"] = {"pos": 184, "type": "int32"}
TRACE_HEADER_DEF["Inline3D"] = {"pos": 188, "type": "int32"}
TRACE_HEADER_DEF["Crossline3D"] = {"pos": 192, "type": "int32"}
TRACE_HEADER_DEF["ShotPoint"] = {"pos": 196, "type": "int32"}
TRACE_HEADER_DEF["ShotPointScalar"] = {"pos": 200, "type": "int16"}
TRACE_HEADER_DEF["TraceValueMeasurementUnit"] = {"pos": 202, "type": "int16"}
TRACE_HEADER_DEF["TraceValueMeasurementUnit"]["descr"] = {SEGY_REVISION_1: {
    -1: "Other",
    0: "Unknown (should be described in Data Sample "
       "Measurement Units Stanza)",
    1: "Pascal (Pa)",
    2: "Volts (V)",
    3: "Millivolts (v)",
    4: "Amperes (A)",
    5: "Meters (m)",
    6: "Meters Per Second (m/s)",
    7: "Meters Per Second squared (m/&s2)Other",
    8: "Newton (N)",
    9: "Watt (W)"}}
TRACE_HEADER_DEF["TransductionConstantMantissa"] = {"pos": 204, "type": "int32"}
TRACE_HEADER_DEF["TransductionConstantPower"] = {"pos": 208, "type": "int16"}
TRACE_HEADER_DEF["TransductionUnit"] = {"pos": 210, "type": "int16"}
TRACE_HEADER_DEF["TransductionUnit"]["descr"] = TRACE_HEADER_DEF[
    "TraceValueMeasurementUnit"]["descr"]
TRACE_HEADER_DEF["TraceIdentifier"] = {"pos": 212, "type": "int16"}
TRACE_HEADER_DEF["ScalarTraceHeader"] = {"pos": 214, "type": "int16"}
TRACE_HEADER_DEF["SourceType"] = {"pos": 216, "type": "int16"}
TRACE_HEADER_DEF["SourceType"]["descr"] = {SEGY_REVISION_1: {
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

TRACE_HEADER_DEF["SourceEnergyDirectionMantissa"] = {"pos": 218, "type": "int32"}
TRACE_HEADER_DEF["SourceEnergyDirectionExponent"] = {"pos": 222, "type": "int16"}
TRACE_HEADER_DEF["SourceMeasurementMantissa"] = {"pos": 224, "type": "int32"}
TRACE_HEADER_DEF["SourceMeasurementExponent"] = {"pos": 228, "type": "int16"}
TRACE_HEADER_DEF["SourceMeasurementUnit"] = {"pos": 230, "type": "int16"}
TRACE_HEADER_DEF["SourceMeasurementUnit"]["descr"] = {1: {
    -1: "Other (should be described in Source Measurement Unit stanza)",
    0: "Unknown",
    1: "Joule (J)",
    2: "Kilowatt (kW)",
    3: "Pascal (Pa)",
    4: "Bar (Bar)",
    5: "Newton (N)",
    6: "Kilograms (kg)"}}
TRACE_HEADER_DEF["UnassignedInt1"] = {"pos": 232, "type": "int32"}
TRACE_HEADER_DEF["UnassignedInt2"] = {"pos": 236, "type": "int32"}
