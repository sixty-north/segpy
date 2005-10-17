"""
A python module for reading/writing/manipuating 
SEG-Y formatted filed

segy.readSegy		: Read SEGY file
segy.getSegyHeader  	: Get SEGY header 
segy.getSegyTraceHeader : Get SEGY Trace header 
segy.getAllSegyTraceHeaders : Get all SEGY Trace headers 
segy.getSegyTrace		: Get SEGY Trace heder and trace data for one trace

segy.getValue 		: Get a value from a binary string
segy.ibm2ieee		: Convert IBM floats to IEEE

segy.version 		: The version of SegyPY
segy.verbose 		: Amount of verbose information to the scree
"""
#
# segypy : A Python module for reading and writing SEG-Y formatted data
#
# (C) Thomas Mejer Hansen, 2005
#


import struct

pref_numeric_module='numarray' # FAST ON LARGE FILES
#pref_numeric_module='Numeric' 
if (pref_numeric_module=='Numeric'):
	# IMPORT SEPCIFIC FUNCTIONS FROM Numeric
	print('SegyPY : Using Numeric module')
	from Numeric import transpose
	from Numeric import resize
	from Numeric import reshape
	from Numeric import zeros
	from Numeric import arange
	
else:
	# IMPORT SEPCIFIC FUNCTIONS FROM numarray
	print('SegyPY : Using numarray module')
	from numarray import transpose
	from numarray import resize
	from numarray import reshape
	from numarray import zeros
	from numarray import arange

# SOME GLOBAL PARAMETERS
version=0.2
verbose=1;

endian='>' # Big Endian
#endian='<' # Little Endian
#endian='=' # Native

l_int = struct.calcsize('i')
l_uint = struct.calcsize('I')
l_long = struct.calcsize('l')
l_ulong = struct.calcsize('L')
l_short = struct.calcsize('h')
l_ushort = struct.calcsize('H')
l_char = struct.calcsize('c')
l_uchar = struct.calcsize('B')
l_float = struct.calcsize('f')


##############
# INIT

##############
#  Initialize SEGY HEADER 
SH_def = {"Job": {"pos": 3200,"type":"int32","def":0}}
SH_def["Line"]=			{"pos": 3204,"type":"int32","def":0}
SH_def["Reel"]=			{"pos": 3208,"type":"int32","def":0}
SH_def["DataTracePerEnsemble"]=	{"pos": 3212,"type":"int16","def":0}
SH_def["AuxiliaryTracePerEnsemble"]={"pos": 3214,"type":"int16","def":0}
SH_def["dt"]=			{"pos": 3216,"type":"uint16","def":1000}
SH_def["dtOrig"]=		{"pos": 3218,"type":"uint16","def":1000}
SH_def["ns"]={"pos": 3220,"type":"uint16","def":0}
SH_def["nsOrig"]={"pos": 3222,"type":"uint16","def":0} 
SH_def["DataSampleFormat"]={"pos": 3224,"type":"int16","def":5} 
SH_def["DataSampleFormat"]["descr"]={0:{
	1: "IBM Float", 
	2: "32 bit Integer", 
	3: "16 bit Integer", 
	8: "8 bit Integer"}}

SH_def["DataSampleFormat"]["descr"][1]={
	1: "IBM Float", 
	2: "32 bit Integer", 
	3: "16 bit Integer", 
	5: "IEEE",
	8: "8 bit Integer"}

SH_def["DataSampleFormat"]["bps"]={0:{
	1: 4, 
	2: 4, 
	3: 2, 
	8: 1}}
SH_def["DataSampleFormat"]["bps"][1]={
	1: 4, 
	2: 4, 
	3: 2, 
	5: 4, 
	8: 1}
SH_def["DataSampleFormat"]["datatype"]={0:{
	1: 'ibm', 
	2: 'l', 
	3: 'h', 
	8: 'B'}}
SH_def["DataSampleFormat"]["datatype"][1]={
	1: 'ibm', 
	2: 'l', 
	3: 'h', 
#	5: 'float', 
	5: 'f', 
	8: 'B'}

SH_def["EnsembleFold"]={"pos": 3226,"type":"int16","def":0}
SH_def["TraceSorting"]={"pos": 3228,"type":"int16","def":0}
SH_def["VerticalSumCode"]={"pos": 3230,"type":"int16","def":0}
SH_def["SweepFrequencyEnd"]={"pos": 3234,"type":"int16","def":0}
SH_def["SweepLength"]={"pos": 3236,"type":"int16","def":0}
SH_def["SweepType"]={"pos": 3238,"type":"int16","def":0}
SH_def["SweepChannel"]={"pos": 3240,"type":"int16","def":0}
SH_def["SweepTaperlengthStart"]={"pos": 3242,"type":"int16","def":0}
SH_def["SweepTaperLengthEnd"]={"pos": 3244,"type":"int16","def":0} 
SH_def["TaperType"]={"pos": 3246,"type":"int16","def":0}
SH_def["CorrelatedDataTraces"]={"pos": 3248,"type":"int16","def":0}
SH_def["BinaryGain"]={"pos": 3250,"type":"int16","def":0}
SH_def["AmplitudeRecoveryMethod"]={"pos": 3252,"type":"int16","def":0}
SH_def["MeasurementSystem"]={"pos": 3254,"type":"int16","def":0} 
SH_def["ImpulseSignalPolarity"]={"pos": 3256,"type":"int16","def":0}
SH_def["VibratoryPolarityCode"]={"pos": 3258,"type":"int16","def":0}
SH_def["Unassigned1"]={"pos": 3260,"type":"int16", "n":120,"def":0}
SH_def["SegyFormatRevisionNumber"]={"pos": 3500,"type":"uint16","def":100}
SH_def["FixedLengthTraceFlag"]={"pos": 3502,"type":"uint16","def":0} 
SH_def["NumberOfExtTextualHeaders"]={"pos": 3504,"type":"uint16","def":0}
SH_def["Unassigned2"]={"pos": 3506,"type":"int16", "n":47,"def":0} 

##############
#  Initialize SEGY TRACE HEADER SPECIFICATION
STH_def = {"TraceSequenceLine": {"pos": 0,"type":"int32"}}
STH_def["TraceSequenceFile"]=	{"pos": 4,"type":"int32"}
STH_def["FieldRecord"]=		{"pos": 8, "type":"int32"}
STH_def["TraceNumber"]=		{"pos": 12,"type":"int32"}
STH_def["EnergySourcePoint"]=	{"pos": 16,"type":"int32"} 
STH_def["cdp"]=			{"pos": 20,"type":"int32"}
STH_def["cdpTrace"]=		{"pos": 24,"type":"int32"}
STH_def["TraceIdenitifactionCode"]={"pos":28 ,"type":"uint16"} #'int16'); % 28
STH_def["TraceIdenitifactionCode"]["descr"]={0:{
	1: "Seismic data", 
	2: "Dead", 
	3: "Dummy", 
	4: "Time Break", 
	5: "Uphole", 
	6: "Sweep", 
	7: "Timing", 
	8: "Water Break"}}
STH_def["TraceIdenitifactionCode"]["descr"][1]={
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
	22: "Time-velocity pairs"}STH_def["NSummedTraces"]={"pos":30 ,"type":"int16"} #'int16'); % 30
STH_def["NStackedTraces"]={"pos":32 ,"type":"int16"} #'int16'); % 32
STH_def["DataUse"]={"pos":34 ,"type":"int16"} #'int16'); % 34
STH_def["DataUse"]["descr"]={0: {
	1: "Production", 
	2: "Test"}}
STH_def["DataUse"]["descr"][1]=STH_def["DataUse"]["descr"][0]
STH_def["offset"]={"pos":36 ,"type":"int32"} #'int32');             %36
STH_def["ReceiverGroupElevation"]={"pos":40 ,"type":"int32"} #'int32');             %40
STH_def["SourceSurfaceElevation"]={"pos":44 ,"type":"int32"} #'int32');             %44
STH_def["SourceDepth"]={"pos":48 ,"type":"int32"} #'int32');             %48
STH_def["ReceiverDatumElevation"]={"pos":52 ,"type":"int32"} #'int32');             %52
STH_def["SourceDatumElevation"]={"pos":56 ,"type":"int32"} #'int32');             %56
STH_def["SourceWaterDepth"]={"pos":60 ,"type":"int32"} #'int32');  %60
STH_def["GroupWaterDepth"]={"pos":64 ,"type":"int32"} #'int32');  %64
STH_def["ElevationScalar"]={"pos":68 ,"type":"int16"} #'int16');  %68
STH_def["SourceGroupScalar"]={"pos":70 ,"type":"int16"} #'int16');  %70
STH_def["SourceX"]={"pos":72 ,"type":"int32"} #'int32');  %72
STH_def["SourceY"]={"pos":76 ,"type":"int32"} #'int32');  %76
STH_def["GroupX"]={"pos":80 ,"type":"int32"} #'int32');  %80
STH_def["GroupY"]={"pos":84 ,"type":"int32"} #'int32');  %84
STH_def["CoordinateUnits"]={"pos":88 ,"type":"int16"} #'int16');  %88
STH_def["CoordinateUnits"]["descr"]={1: {
	1: "Length (meters or feet)",
	2: "Seconds of arc"}}
STH_def["CoordinateUnits"]["descr"][1]={
	1: "Length (meters or feet)",
	2: "Seconds of arc",
	3: "Decimal degrees",
	4: "Degrees, minutes, seconds (DMS)"}	
STH_def["WeatheringVelocity"]={"pos":90 ,"type":"int16"} #'int16');  %90
STH_def["SubWeatheringVelocity"]={"pos":92 ,"type":"int16"} #'int16');  %92
STH_def["SourceUpholeTime"]={"pos":94 ,"type":"int16"} #'int16');  %94
STH_def["GroupUpholeTime"]={"pos":96 ,"type":"int16"} #'int16');  %96
STH_def["SourceStaticCorrection"]={"pos":98 ,"type":"int16"} #'int16');  %98
STH_def["GroupStaticCorrection"]={"pos":100 ,"type":"int16"} #'int16');  %100
STH_def["TotalStaticApplied"]={"pos":102 ,"type":"int16"} #'int16');  %102
STH_def["LagTimeA"]={"pos":104 ,"type":"int16"} #'int16');  %104
STH_def["LagTimeB"]={"pos":106 ,"type":"int16"} #'int16');  %106
STH_def["DelayRecordingTime"]={"pos":108 ,"type":"int16"} #'int16');  %108
STH_def["MuteTimeStart"]={"pos":110 ,"type":"int16"} #'int16');  %110
STH_def["MuteTimeEND"]={"pos":112 ,"type":"int16"} #'int16');  %112
STH_def["ns"]={"pos":114 ,"type":"uint16"} #'uint16');  %114
STH_def["dt"]={"pos":116 ,"type":"uint16"} #'uint16');  %116
STH_def["GainType"]={"pos":119 ,"type":"int16"} #'int16');  %118
STH_def["GainType"]["descr"]={0: {
	1: "Fixes", 
	2: "Binary",
	3: "Floating point"}}
STH_def["GainType"]["descr"][1]=STH_def["GainType"]["descr"][0]
STH_def["InstrumentGainConstant"]={"pos":120 ,"type":"int16"} #'int16');  %120
STH_def["InstrumentInitialGain"]={"pos":122 ,"type":"int16"} #'int16');  %%122
STH_def["Correlated"]={"pos":124 ,"type":"int16"} #'int16');  %124
STH_def["Correlated"]["descr"]={0: {
	1: "No", 
	2: "Yes"}}
STH_def["Correlated"]["descr"][1]=STH_def["Correlated"]["descr"][0]

STH_def["SweepFrequenceStart"]={"pos":126 ,"type":"int16"} #'int16');  %126
STH_def["SweepFrequenceEnd"]={"pos":128 ,"type":"int16"} #'int16');  %128
STH_def["SweepLength"]={"pos":130 ,"type":"int16"} #'int16');  %130
STH_def["SweepType"]={"pos":132 ,"type":"int16"} #'int16');  %132
STH_def["SweepType"]["descr"]={0: {
	1: "linear", 
	2: "parabolic",
	3: "exponential",
	4: "other"}}
STH_def["SweepType"]["descr"][1]=STH_def["SweepType"]["descr"][0]

STH_def["SweepTraceTaperLengthStart"]={"pos":134 ,"type":"int16"} #'int16');  %134
STH_def["SweepTraceTaperLengthEnd"]={"pos":136 ,"type":"int16"} #'int16');  %136
STH_def["TaperType"]={"pos":138 ,"type":"int16"} #'int16');  %138
STH_def["TaperType"]["descr"]={0: {
	1: "linear", 
	2: "cos2c",
	3: "other"}}
STH_def["TaperType"]["descr"][1]=STH_def["TaperType"]["descr"][0]

STH_def["AliasFilterFrequency"]={"pos":140 ,"type":"int16"} #'int16');  %140
STH_def["AliasFilterSlope"]={"pos":142 ,"type":"int16"} #'int16');  %142
STH_def["NotchFilterFrequency"]={"pos":144 ,"type":"int16"} #'int16');  %144
STH_def["NotchFilterSlope"]={"pos":146 ,"type":"int16"} #'int16');  %146
STH_def["LowCutFrequency"]={"pos":148 ,"type":"int16"} #'int16');  %148
STH_def["HighCutFrequency"]={"pos":150 ,"type":"int16"} #'int16');  %150
STH_def["LowCutSlope"]={"pos":152 ,"type":"int16"} #'int16');  %152
STH_def["HighCutSlope"]={"pos":154 ,"type":"int16"} #'int16');  %154
STH_def["YearDataRecorded"]={"pos":156 ,"type":"int16"} #'int16');  %156
STH_def["DayOfYear"]={"pos":158 ,"type":"int16"} #'int16');  %158
STH_def["HourOfDay"]={"pos":160 ,"type":"int16"} #'int16');  %160
STH_def["MinuteOfHour"]={"pos":162 ,"type":"int16"} #'int16');  %162
STH_def["SecondOfMinute"]={"pos":164 ,"type":"int16"} #'int16');  %164
STH_def["TimeBaseCode"]={"pos":166 ,"type":"int16"} #'int16');  %166
STH_def["TimeBaseCode"]["descr"]={0: {
	1: "Local", 
	2: "GMT", 
	3: "Other"}}
STH_def["TimeBaseCode"]["descr"][1]={
	1: "Local", 
	2: "GMT", 
	3: "Other", 
	4: "UTC"}
STH_def["TraceWeightningFactor"]={"pos":168 ,"type":"int16"} #'int16');  %170
STH_def["GeophoneGroupNumberRoll1"]={"pos":170 ,"type":"int16"} #'int16');  %172
STH_def["GeophoneGroupNumberFirstTraceOrigField"]={"pos":172 ,"type":"int16"} #'int16');  %174
STH_def["GeophoneGroupNumberLastTraceOrigField"]={"pos":174 ,"type":"int16"} #'int16');  %176
STH_def["GapSize"]={"pos":176 ,"type":"int16"} #'int16');  %178
STH_def["OverTravel"]={"pos":178 ,"type":"int16"} #'int16');  %178
STH_def["OverTravel"]["descr"]={0: {
	1: "down (or behind)", 
	2: "up (or ahead)",
	3: "other"}}
STH_def["OverTravel"]["descr"][1]=STH_def["OverTravel"]["descr"][0]


STH_def["cdpX"]={"pos":180 ,"type":"int32"} #'int32');  %180
STH_def["cdpY"]={"pos":184 ,"type":"int32"} #'int32');  %184
STH_def["Inline3D"]={"pos":188 ,"type":"int32"} #'int32');  %188
STH_def["Crossline3D"]={"pos":192 ,"type":"int32"} #'int32');  %192
STH_def["ShotPoint"]={"pos":192 ,"type":"int32"} #'int32');  %196
STH_def["ShotPointScalar"]={"pos":200 ,"type":"int16"} #'int16');  %200
STH_def["TraceValueMeasurementUnit"]={"pos":202 ,"type":"int16"} #'int16');  %202
STH_def["TraceValueMeasurementUnit"]["descr"] = {1: {
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
STH_def["TransductionConstantMantissa"]={"pos":204 ,"type":"int32"} #'int32');  %204
STH_def["TransductionConstantPower"]={"pos":208 ,"type":"int16"} #'int16'); %208
STH_def["TransductionUnit"]={"pos":210 ,"type":"int16"} #'int16');  %210
STH_def["TransductionUnit"]["descr"]  = STH_def["TraceValueMeasurementUnit"]["descr"] 
STH_def["TraceIdentifier"]={"pos":212 ,"type":"int16"} #'int16');  %212
STH_def["ScalarTraceHeader"]={"pos":214 ,"type":"int16"} #'int16');  %214
STH_def["SourceType"]={"pos":216 ,"type":"int16"} #'int16');  %216
STH_def["SourceType"]["descr"] = {1: {
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

STH_def["SourceEnergyDirectionMantissa"]={"pos":218 ,"type":"int32"} #'int32');  %218
STH_def["SourceEnergyDirectionExponent"]={"pos":222 ,"type":"int16"} #'int16');  %222
STH_def["SourceMeasurementMantissa"]={"pos":224 ,"type":"int32"} #'int32');  %224
STH_def["SourceMeasurementExponent"]={"pos":228 ,"type":"int16"} #'int16');  %228
STH_def["SourceMeasurementUnit"]={"pos":230 ,"type":"int16"} #'int16');  %230
STH_def["SourceMeasurementUnit"]["descr"] = {1: {
	-1: "Other (should be described in Source Measurement Unit stanza)",
 	0: "Unknown",
 	1: "Joule (J)",
 	2: "Kilowatt (kW)",
 	3: "Pascal (Pa)",
 	4: "Bar (Bar)",
 	4: "Bar-meter (Bar-m)",
 	5: "Newton (N)",
 	6: "Kilograms (kg)"}}
STH_def["UnassignedInt1"]={"pos":232 ,"type":"int32"} #'int32');  %232
STH_def["UnassignedInt2"]={"pos":236 ,"type":"int32"} #'int32');  %236


##############
# FUNCTIONS

def imageSegy(Data):
	"""
	imageSegy(Data)
	Image segy Data
	"""
	import pylab
	pylab.imshow(Data)
	pylab.title('pymat test')
	pylab.grid(True)
	pylab.show()

def wiggle(Data,SH,skipt=1,maxval=8,lwidth=.1):
	"""
	wiggle(Data,SH)
	"""
	import pylab
		
	t = range(SH['ns'])
# 	t = range(SH['ns'])*SH['dt']/1000000;

	for i in range(0,SH['ntraces'],skipt):
#		trace=zeros(SH['ns']+2)
#		dtrace=Data[:,i]
#		trace[1:SH['ns']]=Data[:,i]
#		trace[SH['ns']+1]=0
		trace=Data[:,i]
		trace[0]=0
		trace[SH['ns']-1]=0	
		pylab.plot(i+trace/maxval,t,color='black',linewidth=lwidth)
		for a in range(len(trace)):
			if (trace[a]<0):
				trace[a]=0;
		# pylab.fill(i+Data[:,i]/maxval,t,color='k',facecolor='g')
		pylab.fill(i+Data[:,i]/maxval,t,'k',linewidth=0)
	pylab.title(SH['filename'])
	pylab.grid(True)
	pylab.show()


def getDefaultSegyHeader(ntraces=100,ns=100):
	"""
	SH=getDefaultSegyHeader()
	"""
	# INITIALIZE DICTIONARY
	SH = {"Job": {"pos": 3200,"type":"int32","def":0}}
		
	for key in SH_def.keys(): 

		tmpkey = SH_def[key]
		if (tmpkey.has_key('def')):
			val=tmpkey['def']
		else:
			val=0
		SH[key]=val

	SH["ntraces"]=ntraces;
	SH["ns"]=ns;
	
		
	return SH
def getDefaultSegyTraceHeaders(ntraces=100,ns=100,dt=1000):
	"""
	SH=getDefaultSegyTraceHeader()
	"""
	# INITIALIZE DICTIONARY
	STH = {"TraceSequenceLine": {"pos": 0,"type":"int32"}}
		
	for key in STH_def.keys(): 

		tmpkey = STH_def[key]
		if (tmpkey.has_key('def')):
			val=tmpkey['def']
		else:
			val=0
		STH[key]=zeros(ntraces)
			
	for a in range(ntraces):			
		STH["TraceSequenceLine"][a]=a+1
		STH["TraceSequenceFile"][a]=a+1
		STH["FieldRecord"][a]=1000
		STH["TraceNumber"][a]=a+1
		STH["ns"][a]=ns
		STH["dt"][a]=dt
	return STH


def getSegyTraceHeader(SH,THN='cdp',data='none'):
	"""
	getSegyTraceHeader(SH,TraceHeaderName)
	"""

	bps=getBytePerSample(SH)

	if (data=='none'):
		data = open(SH["filename"]).read()
		

	# MAKE SOME LOOKUP TABLE THAT HOLDS THE LOCATION OF HEADERS
#	THpos=TraceHeaderPos[THN]
	THpos=STH_def[THN]["pos"]
	THformat=STH_def[THN]["type"]
	ntraces=SH["ntraces"]
	thv = zeros(ntraces)
	for itrace in range(1,ntraces+1,1):
		i=itrace

		pos=THpos+3600+(SH["ns"]*bps+240)*(itrace-1);

		txt="getSegyTraceHeader : Reading trace header " + THN + " " + str(itrace)  + " of " + str(ntraces) + " " +str(pos)

		printverbose(txt,20);
		thv[itrace-1],index = getValue(data,pos,THformat,endian,1)
		txt="getSegyTraceHeader : " + THN + "=" + str(thv[itrace-1])
		printverbose(txt,30);
	
	return thv

def getAllSegyTraceHeaders(SH,data='none'):
	SegyTraceHeaders = {'filename': SH["filename"]}

        printverbose('getAllSegyTraceHeaders : trying to get all segy trace headers',2)


	if (data=='none'):
		data = open(SH["filename"]).read()
			
	for key in STH_def.keys(): 	 

		sth = getSegyTraceHeader(SH,key,data) 	 
		SegyTraceHeaders[key]=sth 	 

		txt =  "getAllSegyTraceHeaders :  " + key 	 
		printverbose(txt,10) 	 

	return SegyTraceHeaders
	


def readSegy(filename)	:
	"""
	Data,SegyHeader,SegyTraceHeaders=getSegyHeader(filename)
	"""
	
	printverbose("readSegy : Trying to read "+filename,0)

	data = open(filename).read()

	filesize=len(data)

	SH=getSegyHeader(filename)

	bps=getBytePerSample(SH)

	ntraces = (filesize-3600)/(SH['ns']*bps+240)
#	ntraces = 100

	printverbose("readSegy : Length of data : " + str(filesize),2)

	SH["ntraces"]=ntraces;

	ndummy_samples=240/bps
	printverbose("readSegy : ndummy_samples="+str(ndummy_samples),6)
	printverbose("readSegy : ntraces=" + str(ntraces) + " nsamples="+str(SH['ns']),2)


	# GET TRACE
	index=3600;
	nd=(filesize-3600)/bps 
		
	# READ ALL SEGY TRACE HEADRES
	SegyTraceHeaders = getAllSegyTraceHeaders(SH,data)

	printverbose("readSegy : reading segy data",2)

	# READ ALL DATA EXCEPT FOR SEGY HEADER
	#Data = zeros((SH['ns'],ntraces))

	revision=SH["SegyFormatRevisionNumber"]
	if (revision==100):
		revision=1
	dsf=SH["DataSampleFormat"]

	DataDescr=SH_def["DataSampleFormat"]["descr"][revision][dsf]

	printverbose("readSegy : SEG-Y revision = "+str(revision),1)
	printverbose("readSegy : DataSampleFormat="+str(dsf)+"("+DataDescr+")",1)

	if (SH["DataSampleFormat"]==1):
		printverbose("readSegy : Assuming DSF=1, IBM FLOATS",2)
		Data1 = getValue(data,index,'ibm',endian,nd)
	elif (SH["DataSampleFormat"]==2):
		printverbose("readSegy : Assuming DSF=" + str(SH["DataSampleFormat"]) + ", 32bit INT",2)		
		Data1 = getValue(data,index,'l',endian,nd)
	elif (SH["DataSampleFormat"]==3):
		printverbose("readSegy : Assuming DSF=" + str(SH["DataSampleFormat"]) + ", 16bit INT",2)		
		Data1 = getValue(data,index,'h',endian,nd)
	elif (SH["DataSampleFormat"]==5):
		printverbose("readSegy : Assuming DSF=" + str(SH["DataSampleFormat"]) + ", IEEE",2)		
		Data1 = getValue(data,index,'float',endian,nd)
	elif (SH["DataSampleFormat"]==8):
		printverbose("readSegy : Assuming DSF=" + str(SH["DataSampleFormat"]) + ", 8bit CHAR",2)		
		Data1 = getValue(data,index,'B',endian,nd)
	else:
		printverbose("readSegy : DSF=" + str(SH["DataSampleFormat"]) + ", NOT SUPORTED",2)		

	Data = Data1[0]


	printverbose("readSegy : - reshaping",2)
	Data=reshape(Data,(ntraces,SH['ns']+ndummy_samples))
	printverbose("readSegy : - stripping header dummy data",2)
	Data=Data[:,ndummy_samples:(SH['ns']+ndummy_samples)]
	printverbose("readSegy : - transposing",2)
	Data=transpose(Data)
	
	# SOMEONE NEEDS TO IMPLEMENT A NICER WAY DO DEAL WITH DSF=8
	if (SH["DataSampleFormat"]==8):
		for i in arange(ntraces):
			for j in arange(SH['ns']):
				if Data[i][j]>128:
					Data[i][j]=Data[i][j]-256


	

	printverbose("readSegy :  read data",2)
	
	return Data,SH,SegyTraceHeaders	


def getSegyTrace(SH,itrace):
	"""
	SegyTraceHeader,SegyTraceData=getSegyTrace(SegyHeader,itrace)
		itrace : trace number to read
		THIS DEF IS NOT UPDATED. NOT READY TO USE
	"""	
	data = open(SH["filename"]).read()

	bps=getBytePerSample(SH)


	# GET TRACE HEADER
	index=3200+(itrace-1)*(240+SH['ns']*bps)
	SegyTraceHeader=[];
	#print index

	# GET TRACE
	index=3200+(itrace-1)*(240+SH['ns']*bps)+240
	SegyTraceData = getValue(data,index,'float',endian,SH['ns'])
	return SegyTraceHeader,SegyTraceData

def getSegyHeader(filename):
	"""
	SegyHeader=getSegyHeader(filename)
	"""
	data = open(filename).read()

	SegyHeader = {'filename': filename}
 	for key in SH_def.keys(): 
		pos=SH_def[key]["pos"]
		format=SH_def[key]["type"]

		SegyHeader[key],index = getValue(data,pos,format,endian);	

		txt =  str(pos) + " " + str(format) + "  Reading " + key +"="+str(SegyHeader[key])
	        printverbose(txt,10)
	
	# SET NUMBER OF BYTES PER DATA SAMPLE
	bps=getBytePerSample(SegyHeader)

	filesize=len(data)
	ntraces = (filesize-3600)/(SegyHeader['ns']*bps+240)
	SegyHeader["ntraces"]=ntraces;

        printverbose('getSegyHeader : succesfully read '+filename,1)

	
	return SegyHeader

def writeSegy(filename,Data,dt=.001,STHin={}):
	"""
	writeSegy(filename,Data,dt)

	Write SEGY 

	See also readSegy

	(c) 2005, Thomas Mejer Hansen

	MAKE OPTIONAL INPUT FOR ALL SEGYHTRACEHEADER VALUES
	
	"""

	printverbose("writeSegy : Trying to write "+filename,0)

	N=Data.shape
	ns=N[0]
	ntraces=N[1]
	print ntraces,ns

	SH = getDefaultSegyHeader(ntraces,ns);
	STH = getDefaultSegyTraceHeaders(ntraces,ns,dt)

	# ADD STHin, if exists...
	for key in STHin.keys():
		print key
		for a in range(ntraces):
			STH[key]=STHin[key][a]
	

	writeSegyStructure(filename,Data,SH,STH)
	

def writeSegyStructure(filename,Data,SH,STH):
	"""
	writeSegyHeader(filename,Data,SegyHeader,SegyTraceHeaders)

	Write SEGY file using SegyPy data structures

	See also readSegy

	(c) 2005, Thomas Mejer Hansen
	
	"""

	printverbose("writeSegyStructure : Trying to write "+filename,0)
	
	f = open(filename,'w')

	# VERBOSE INF
	revision=SH["SegyFormatRevisionNumber"]
	dsf=SH["DataSampleFormat"]
	if (revision==100):
		revision=1
	DataDescr=SH_def["DataSampleFormat"]["descr"][revision][dsf]

	printverbose("writeSegyStructure : SEG-Y revision = "+str(revision),1)
	printverbose("writeSegyStructure : DataSampleFormat="+str(dsf)+"("+DataDescr+")",1)

	# WRITE SEGY HEADER

	for key in SH_def.keys(): 	
		pos=SH_def[key]["pos"]
		format=SH_def[key]["type"]
		value=SH[key]

#		SegyHeader[key],index = putValue(value,f,pos,format,endian);	
		putValue(value,f,pos,format,endian);	
		
		txt =  str(pos) + " " + str(format) + "  Reading " + key + "=" + str(value)
#+"="+str(SegyHeader[key])
	        # printverbose(txt,-1)

	
	# SEGY TRACES


	ctype=SH_def['DataSampleFormat']['datatype'][revision][dsf]
	bps=SH_def['DataSampleFormat']['bps'][revision][dsf]
	

	sizeT = 240 + SH['ns']*bps;

	for itrace in range(SH['ntraces']):		
		index=3600+itrace*sizeT
	 	printverbose('Writing Trace #'+str(itrace+1)+'/'+str(SH['ntraces']),10)
		# WRITE SEGY TRACE HEADER
		for key in STH_def.keys(): 	
			pos=index+STH_def[key]["pos"]
			format=STH_def[key]["type"]
			value=STH[key][itrace]
			txt =  str(pos) + " " + str(format) + "  Writing " + key + "=" + str(value)
	        	printverbose(txt,40)
			putValue(value,f,pos,format,endian);	
	         
		# Write Data	
		cformat=endian + ctype
		for s in range(SH['ns']):
			strVal=struct.pack(cformat, Data[s,itrace])
			f.seek(index+240+s*struct.calcsize(cformat))
			f.write(strVal);



	f.close

	#return segybuffer
	
def putValue(value,fileid,index,ctype='l',endian='>',number=1):
	"""
	putValue(data,index,ctype,endian,number)
	"""
	if (ctype=='l')|(ctype=='long')|(ctype=='int32'):
		size=l_long
	        ctype='l'
        elif (ctype=='L')|(ctype=='ulong')|(ctype=='uint32'):
		size=l_ulong
		ctype='L'
        elif (ctype=='h')|(ctype=='short')|(ctype=='int16'):
		size=l_short
		ctype='h'
        elif (ctype=='H')|(ctype=='ushort')|(ctype=='uint16'):
		size=l_ushort
		ctype='H'
        elif (ctype=='c')|(ctype=='char'):
		size=l_char
		ctype='c'
        elif (ctype=='B')|(ctype=='uchar'):
		size=l_uchar
		ctype='B'
        elif (ctype=='f')|(ctype=='float'):
		size=l_float
		ctype='f'
        elif (ctype=='ibm'):
		size=l_float
	else:
		printverbose('Bad Ctype : ' +ctype,-1)

	cformat=endian + ctype*number

	printverbose('putValue : cformat :  ' + cformat + ' ctype=' + ctype,40)
	
	strVal=struct.pack(cformat, value)
	fileid.seek(index)
	fileid.write(strVal);


	return 1


def getValue(data,index,ctype='l',endian='>',number=1):
	"""
	getValue(data,index,ctype,endian,number)
	"""
	if (ctype=='l')|(ctype=='long')|(ctype=='int32'):
		size=l_long
	        ctype='l'
        elif (ctype=='L')|(ctype=='ulong')|(ctype=='uint32'):
		size=l_ulong
		ctype='L'
        elif (ctype=='h')|(ctype=='short')|(ctype=='int16'):
		size=l_short
		ctype='h'
        elif (ctype=='H')|(ctype=='ushort')|(ctype=='uint16'):
		size=l_ushort
		ctype='H'
        elif (ctype=='c')|(ctype=='char'):
		size=l_char
		ctype='c'
        elif (ctype=='B')|(ctype=='uchar'):
		size=l_uchar
		ctype='B'
        elif (ctype=='f')|(ctype=='float'):
		size=l_float
		ctype='f'
        elif (ctype=='ibm'):
		size=l_float
	else:
		printverbose('Bad Ctype : ' +ctype,-1)


	cformat=endian + ctype*number

	printverbose('getValue : cformat :  ' + cformat,40)
	
	index_end=index+size*number

	if (ctype=='ibm'):
		# ASSUME IBM FLOAT DATA
		Value = range(number)		
		for i in arange(number):
			index_ibm=i*4+index
			Value[i] = ibm2ieee2(data[index_ibm:index_ibm+4])
		# this resturn an array as opposed to a tuple	
	else:
		# ALL OTHER TYPES OF DATA
		Value=struct.unpack(cformat, data[index:index_end])

	if (ctype=='B'):
		printverbose('getValue : Ineficient use of 1byte Integer...',-1)
 
	vtxt = 'getValue : '+'start='+str(index)+' size='+str(size)+ ' number='+str(number)+' Value='+str(Value)+' cformat='+str(cformat)
        printverbose(vtxt,20)

	if number==1:
		return Value[0], index_end
	else:
		return Value,index_end



def print_version():
	print 'SegyPY version is ', version

def printverbose(txt,level=1):
        if level<=verbose:
		print 'SegyPY',version,': ',txt


##############
# MISC FUNCTIONS
def ibm2Ieee(ibm_float):
	"""
	ibm2Ieee(ibm_float)
	Used by permission
	(C) Secchi Angelo
	with thanks to Howard Lightstone and Anton Vredegoor. 
	"""
	I = struct.unpack('>I',ibm_float)[0]
	sign = [1,-1][bool(i & 0x100000000L)]
	characteristic = ((i >> 24) & 0x7f) - 64
	fraction = (i & 0xffffff)/float(0x1000000L)
	return sign*16**characteristic*fraction



def ibm2ieee2(ibm_float):
	"""
	ibm2ieee2(ibm_float)
	Used by permission
	(C) Secchi Angelo
	with thanks to Howard Lightstone and Anton Vredegoor. 
	"""
	dividend=float(16**6)
	
	if ibm_float == 0:
		return 0.0
	istic,a,b,c=struct.unpack('>BBBB',ibm_float)
	if istic >= 128:
		sign= -1.0
		istic = istic - 128
	else:
		sign = 1.0
	mant= float(a<<16) + float(b<<8) +float(c)
	return sign* 16**(istic-64)*(mant/dividend)
	

def getBytePerSample(SH):
	revision=SH["SegyFormatRevisionNumber"]
	if (revision==100):
		revision=1
	dsf=SH["DataSampleFormat"]
	
	
	bps=SH_def["DataSampleFormat"]["bps"][revision][dsf]

	printverbose("getBytePerSample :  bps="+str(bps),21);
	
	return bps


##############
# segy class
class SegyTraceheaderClass:
	def __init__(self):
		self.cdp=0

class SegyHeaderClass:
	def __str__(self):
		return "SegyHeaderClass "	
	def __init__(self):	
		self.filename=0
		self.Trace = version

	def cdp(self):
		return "Getting CDP trace header"
	def InlineX(self):
		return "Getting CDP trace header"

	


class SegyClass:
	STH_def=STH_def
	SH_def=SH_def
	STH=SegyTraceheaderClass()
	SH=SegyHeaderClass()


	def __init__(self):
		self.THOMAS='Thomas'
