from revisions import SEGY_REVISION_0, SEGY_REVISION_1

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
