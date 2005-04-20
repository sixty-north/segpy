"""
A python module for reading/writing/manipuating 
SEG-Y formatted filed

segy.version 		: The version of SegyPY
segy.verbose 		: Amount of verbose information to the screen.
segy.getValue 		: Get a value from a binary string
segy.getSegyHeader  	: Get SEGY header form file
segy.readSegy		: Read SEGY file
"""
#
# segypy : A Python module for reading and writing SEG-Y formatted data
#
# (C) Thomas Mejer Hansen, 2005
#


import struct

pref_numeric_module='numarray' # FAST ON LARGE FILES
pref_numeric_module='Numeric' 
if (pref_numeric_module=='Numeric'):
	# IMPORT SEPCIFIC FUNCTIONS FROM Numeric
	print('SegyPY : Using Numeric module')
	from Numeric import transpose
	from Numeric import resize
	from Numeric import zeros
else:
	# IMPORT SEPCIFIC FUNCTIONS FROM numarray
	print('SegyPY : Using numarray module')
	from numarray import transpose
	from numarray import resize
	from numarray import zeros

# SOME GLOBAL PARAMETERS
version=0.1
verbose=1;

#endian='>' # Big Endian
#endian='<' # Little Endian
#endian='=' # Native

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
SH_def = {"Job": {"pos": 3200,"type":"int32"}}
SH_def["Line"]=			{"pos": 3204,"type":"int32"}
SH_def["Line"]=			{"pos": 3208,"type":"int32"}
SH_def["DataTracePerEnsemble"]=	{"pos": 3212,"type":"int16"}
SH_def["AuxiliaryTracePerEnsemble"]={"pos": 3214,"type":"int16"}
SH_def["dt"]=			{"pos": 3216,"type":"uint16"}
SH_def["dtOrig"]=		{"pos": 3218,"type":"uint16"}

##############
#  Initialize SEGY TRACE HEADER SPECIFICATION
STH_def = {"TraceSequenceLine": {"pos": 0,"type":"int32"}}
STH_def["TraceSequenceFile"]=	{"pos": 4,"type":"int32"}
STH_def["FieldRecord"]=		{"pos": 8, "type":"int32"}
STH_def["TraceNumber"]=		{"pos": 12,"type":"int32"}
STH_def["EnergySourcePoint"]=	{"pos": 16,"type":"int32"} 
STH_def["cdp"]=			{"pos": 20,"type":"int32"}
STH_def["cdpTrace"]=		{"pos": 24,"type":"int32"}
# AND ADD THE REST....
STH_def["TraceIdenitifactionCode"]={"pos":28 ,"type":"int16"} #'int16'); % 28
STH_def["NSummedTraces"]={"pos":30 ,"type":"int16"} #'int16'); % 30
STH_def["NStackedTraces"]={"pos":32 ,"type":"int16"} #'int16'); % 32
STH_def["DataUse"]={"pos":34 ,"type":"int16"} #'int16'); % 34
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
STH_def["InstrumentGainConstant"]={"pos":120 ,"type":"int16"} #'int16');  %120
STH_def["InstrumentInitialGain"]={"pos":122 ,"type":"int16"} #'int16');  %%122
STH_def["Correlated"]={"pos":124 ,"type":"int16"} #'int16');  %124
STH_def["SweepFrequenceStart"]={"pos":126 ,"type":"int16"} #'int16');  %126
STH_def["SweepFrequenceEnd"]={"pos":128 ,"type":"int16"} #'int16');  %128
STH_def["SweepLength"]={"pos":130 ,"type":"int16"} #'int16');  %130
STH_def["SweepType"]={"pos":132 ,"type":"int16"} #'int16');  %132
STH_def["SweepTraceTaperLengthStart"]={"pos":134 ,"type":"int16"} #'int16');  %134
STH_def["SweepTraceTaperLengthEnd"]={"pos":136 ,"type":"int16"} #'int16');  %136
STH_def["TaperType"]={"pos":138 ,"type":"int16"} #'int16');  %138
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
STH_def["TimeBaseCode"]["descr"]={
	1: "Local", 
	2: "GMT", 
	3:"Other", 
	4:"UTC"}
STH_def["TraceWeightningFactor"]={"pos":168 ,"type":"int16"} #'int16');  %170
STH_def["GeophoneGroupNumberRoll1"]={"pos":170 ,"type":"int16"} #'int16');  %172
STH_def["GeophoneGroupNumberFirstTraceOrigField"]={"pos":172 ,"type":"int16"} #'int16');  %174
STH_def["GeophoneGroupNumberLastTraceOrigField"]={"pos":174 ,"type":"int16"} #'int16');  %176
STH_def["GapSize"]={"pos":176 ,"type":"int16"} #'int16');  %178
STH_def["OverTravel"]={"pos":178 ,"type":"int16"} #'int16');  %178
STH_def["cdpX"]={"pos":180 ,"type":"int32"} #'int32');  %180
STH_def["cdpY"]={"pos":184 ,"type":"int32"} #'int32');  %184
STH_def["Inline3D"]={"pos":188 ,"type":"int32"} #'int32');  %188
STH_def["Crossline3D"]={"pos":192 ,"type":"int32"} #'int32');  %192
STH_def["ShotPoint"]={"pos":192 ,"type":"int32"} #'int32');  %196
STH_def["ShotPointScalar"]={"pos":200 ,"type":"int16"} #'int16');  %200
STH_def["TraceValueMeasurementUnit"]={"pos":202 ,"type":"int16"} #'int16');  %202
STH_def["TraceValueMeasurementUnit"]["descr"] = {
	-1: "Other", 
	0: "Unknown", 
	1: "Pascal (Pa)", 
	2: "Volts (V)", 
	3: "Millivolts (v)", 
	4: "Amperes (A)", 
	5: "Meters (m)", 
	6: "Meters Per Second (m/s)", 
	7: "Meters Per Second squared (m/&s2)Other", 
	8: "Newton (N)", 
	9: "Watt (W)"}
#if SegyTraceHeader.TraceValueMeasurementUnit==-1, #SegyTraceHeader.TraceValueMeasurementUnitText='Other';
#elseif SegyTraceHeader.TraceValueMeasurementUnit==0, #SegyTraceHeader.TraceValueMeasurementUnitText='Unknown';
#elseif SegyTraceHeader.TraceValueMeasurementUnit==1, #SegyTraceHeader.TraceValueMeasurementUnitText='Pascal (Pa)';
#elseif SegyTraceHeader.TraceValueMeasurementUnit==2, #SegyTraceHeader.TraceValueMeasurementUnitText='Volts (v)';
#elseif SegyTraceHeader.TraceValueMeasurementUnit==3, #SegyTraceHeader.TraceValueMeasurementUnitText='Millivolts (v)';
#elseif SegyTraceHeader.TraceValueMeasurementUnit==4, #SegyTraceHeader.TraceValueMeasurementUnitText='Amperes (A)';  
#elseif SegyTraceHeader.TraceValueMeasurementUnit==5, #SegyTraceHeader.TraceValueMeasurementUnitText='Meters (m)';  
#elseif SegyTraceHeader.TraceValueMeasurementUnit==6, #SegyTraceHeader.TraceValueMeasurementUnitText='Meters Per Second (m/s)';  
#elseif SegyTraceHeader.TraceValueMeasurementUnit==7, #SegyTraceHeader.TraceValueMeasurementUnitText='Meters Per Second squared (m/&s2)Other';  
#elseif SegyTraceHeader.TraceValueMeasurementUnit==8, #SegyTraceHeader.TraceValueMeasurementUnitText='Newton (N)';  
#elseif SegyTraceHeader.TraceValueMeasurementUnit==9, #SegyTraceHeader.TraceValueMeasurementUnitText='Watt (W)';  
#else SegyTraceHeader.TraceValueMeasurementUnitText='Undefined'; end
STH_def["TransductionConstantMantissa"]={"pos":204 ,"type":"int32"} #'int32');  %204
STH_def["TransductionConstantPower"]={"pos":208 ,"type":"int16"} #'int16'); %208
STH_def["TransductionUnit"]={"pos":210 ,"type":"int16"} #'int16');  %210
STH_def["TraceIdentifier"]={"pos":212 ,"type":"int16"} #'int16');  %212
STH_def["ScalarTraceHeader"]={"pos":214 ,"type":"int16"} #'int16');  %214
STH_def["SourceType"]={"pos":216 ,"type":"int16"} #'int16');  %216
STH_def["SourceEnergyDirectionMantissa"]={"pos":218 ,"type":"int32"} #'int32');  %218
STH_def["SourceEnergyDirectionExponent"]={"pos":222 ,"type":"int16"} #'int16');  %222
STH_def["SourceMeasurementMantissa"]={"pos":224 ,"type":"int32"} #'int32');  %224
STH_def["SourceMeasurementExponent"]={"pos":228 ,"type":"int16"} #'int16');  %228
STH_def["SourceMeasurementUnit"]={"pos":230 ,"type":"int16"} #'int16');  %230
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
	imshow(Data)
	title('pymat test')
	grid(True)
	show()

def getSegyTraceHeader(SH,THN='cdp',data='none'):
	"""
	getSegyTraceHeader(SH,TraceHeaderName)
	"""

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

		pos=THpos+3600+(SH["ns"]*4+240)*(itrace-1);

		txt="Reading trace header ",itrace," of ",ntraces,pos
		printverbose(txt,10);
		thv[itrace-1],index = getValue(data,pos,THformat,'>',1)
		txt=THN,"=",thv[itrace-1]
		printverbose(txt,5);
	
	return thv
	


def readSegyFast(filename)	:
	"""
	Data,SegyHeader,SegyTraceHeaders=getSegyHeader(filename)
	"""
	
	printverbose("Trying to read "+filename,0)

	data = open(filename).read()

	filesize=len(data)
        vtxt = "Length of data ; ",filesize
	printverbose(vtxt,2)

	SH=getSegyHeader(filename)

	ntraces = (filesize-3600)/(SH['ns']*4+240)
	printverbose(vtxt,2)
	SH["ntraces"]=ntraces;

	ndummy_samples=240/4

  	vtxt = "readSegyFast :  ntraces=",ntraces,"nsamples=",SH['ns']
	printverbose(vtxt,2)

	index=3600

	Data = zeros((SH['ns'],ntraces))

	printverbose("readSegyFast :  reading data",2)

	# GET TRACE
	index=3200;
	nd=(filesize-3200)/4

	SegyTraceHeader=[]

	# READ ALL DATA EXCEPT FOR SEGY HEADER
	Data1 = getValue(data,index,'float','>',nd)
	Data = Data1[0]
	Data=transpose(resize(Data[0:2240785],(5151,435)))

	# STRIP THE HEADER VALUES FROM THE DATA
	#	
	Data=Data[ndummy_samples:435][:]

	printverbose("readSegyFast :  read data",2)
	
	return Data,SH,SegyTraceHeader	


def readSegy(filename):
	"""
	Data,SegyHeader,SegyTraceHeaders=getSegyHeader(filename)
	"""
        #from numarray import *
	#from pylab import *
	

	data = open(filename).read()

	filesize=len(data)
        vtxt = 'Length of data ; ',filesize
	printverbose(vtxt,2)

	SH=getSegyHeader(filename)

	ntraces = (filesize-3600)/(SH['ns']*4+240)
	printverbose(vtxt,2)

        vtxt = "readSegy :  ntraces=",ntraces,"nsamples=",SH['ns']
	printverbose(vtxt,2)

	index=3600

	ntraces=500;
	Data = zeros((SH['ns'],ntraces))

	printverbose("readSegy :  reading data",2)

	for itrace in range(1,ntraces,1):
		i=itrace
		# print "Reading trace ",itrace," of ",ntraces
		SegyTraceHeader,SegyTraceData=getSegyTrace(SH,itrace)
       
		for iss in range(1,SH['ns'],1):
			#STH((iss))=SegyTraceHeader
			Data[iss-1][itrace-1]=SegyTraceData[0][iss-1]
 		   
	printverbose("readSegy :  read data",2)
	
	#if (segypy_verbose>2):
	#	imshow(Data)
	#	title('pymat test')
	#	grid(True)
	#	show()

	return Data,SH,SegyTraceHeader	

def getSegyTrace(SH,itrace):
	"""
	SegyTraceHeader,SegyTraceData=getSegyTrace(SegyHeader,itrace)
		itrace : trace number to read
	"""	
	data = open(SH["filename"]).read()
	# GET TRACE HEADER
	index=3200+(itrace-1)*(240+SH['ns']*4)
	SegyTraceHeader=[];
	#print index

	# GET TRACE
	index=3200+(itrace-1)*(240+SH['ns']*4)+240
	SegyTraceData = getValue(data,index,'float','>',SH['ns'])
	return SegyTraceHeader,SegyTraceData


def getSegyHeader(filename):
	"""
	SegyHeader=getSegyHeader(filename)
	"""
	data = open(filename).read()

        printverbose('getSegyHeader : trying to read from '+filename,1)
	
	# START INDEX IN FILE
	index=0;

	SegyHeader = {'filename': filename}

	TextualFileHeader,index = getValue(data,index,'c','>',3200);

	SegyHeader['Job'],index = getValue(data,index,'l','>');	
	SegyHeader['Line'],index = getValue(data,index,'l','>')
	SegyHeader['Reel'],index = getValue(data,index,'l','>')
	SegyHeader['DataTracePerEnsemble'],index = getValue(data,index,'h','>')
	SegyHeader['AuxiliaryTracePerEnsemble'],index = getValue(data,index,'short','>')
	SegyHeader['dt'],index = getValue(data,index,'uint16');
	SegyHeader['dtOrig'],index = getValue(data,index,'uint16'); 
	SegyHeader['ns'],index = getValue(data,index,'uint16');       
	SegyHeader['nsOrig'],index = getValue(data,index,'uint16');
	SegyHeader['DataSampleFormat'],index = getValue(data,index,'int16'); 
	SegyHeader['EnsembleFold'],index = getValue(data,index,'int16');                
	SegyHeader['TraceSorting'],index = getValue(data,index,'int16');              
	SegyHeader['VerticalSumCode'],index = getValue(data,index,'int16');      

	SegyHeader['SweepFrequencyStart'],index = getValue(data,index,'int16');   
	SegyHeader['SweepFrequencyEnd'],index = getValue(data,index,'int16');    
	SegyHeader['SweepLength'],index = getValue(data,index,'int16');                
	SegyHeader['SweepType'],index = getValue(data,index,'int16');                 
	SegyHeader['SweepChannel'],index = getValue(data,index,'int16');           
	SegyHeader['SweepTaperlengthStart'],index = getValue(data,index,'int16');             
	SegyHeader['SweepTaperLengthEnd'],index = getValue(data,index,'int16');              
	SegyHeader['TaperType'],index = getValue(data,index,'int16');              
	SegyHeader['CorrelatedDataTraces'],index = getValue(data,index,'int16');
	SegyHeader['BinaryGain'],index = getValue(data,index,'int16');             
	SegyHeader['AmplitudeRecoveryMethod'],index = getValue(data,index,'int16');
	SegyHeader['MeasurementSystem'],index = getValue(data,index,'int16');      
	SegyHeader['ImpulseSignalPolarity'],index = getValue(data,index,'int16');     
	SegyHeader['VibratoryPolarityCode'],index = getValue(data,index,'int16');             

	index=3500;
	SegyHeader['SegyFormatRevisionNumber'],index= getValue(data,index,'uint16');  
	SegyHeader['FixedLengthTraceFlag'],index=getValue(data,index,'uint16');        
	SegyHeader['NumberOfExtTextualHeaders'],index= getValue(data,index,'uint16');


	# CALCULATE NUMBER OF TRACES
	filesize=len(data)
	ntraces = (filesize-3600)/(SegyHeader['ns']*4+240)
	SegyHeader["ntraces"]=ntraces;



        printverbose('getSegyHeader : succesfully read '+filename,1)

	return SegyHeader



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
	else:
		printverbose('Bad Ctype : ' +ctype,-1)

	cformat=endian + ctype*number

	printverbose('cformat :  ' + cformat,20)
	
	index_end=index+size*number
	HeaderValue=struct.unpack(cformat, data[index:index_end])
	
	str = 'getSegyHeaderValue','start=',index,' size=',size, 'number=',number,'Value=',HeaderValue,'cformat=',cformat
        printverbose(str,20)

	if number==1:
		return HeaderValue[0], index_end
	else:
		return HeaderValue,index_end


def print_version():
	print 'SegyPY version is ', version

def printverbose(txt,level=1):
        if level<verbose:
		print 'SegyPY',version,': ',txt



#def read(filename):
#	read_segy(filename)
#
#def write(filename):
#	write_segy(filename)
