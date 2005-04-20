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
verbose=12;

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
SH_def["DataTracePerEnsemble"]={"pos": 3212,"type":"int16"}
SH_def["AuxiliaryTracePerEnsemble"]={"pos": 3214,"type":"int16"}
SH_def["dt"]=				{"pos": 3216,"type":"uint16"}
SH_def["dtOrig"]=			{"pos": 3218,"type":"uint16"}

##############
#  Initialize SEGY TRACE HEADER SPECIFICATION
STH_def = {"TraceSequenceLine": {"pos": 0,"type":"int32"}}
STH_def["TraceSequenceFile"]=	{"pos": 4,"type":"int32"}
STH_def["FieldRecord"]=		{"pos": 8, "type":"int32"}
STH_def["TraceNumber"]=		{"pos": 12,"type":"int32"}
STH_def["EnergySourcePoint"]=	{"pos": 16,"type":"int32"} 
STH_def["cdp"]=				{"pos": 20,"type":"int32"}
STH_def["cdpTrace"]=			{"pos": 24,"type":"int32"}
# AND ADD THE REST....



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
	ntraces=SH["ntraces"]
	thv = zeros(ntraces)
	for itrace in range(1,ntraces+1,1):
		i=itrace

		pos=THpos+3600+(SH["ns"]*4+240)*(itrace-1);

		txt="Reading trace header ",itrace," of ",ntraces,pos
		printverbose(txt,10);
		thv[itrace-1],index = getValue(data,pos,'l','>',1)
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
	if (ctype=='l')|(ctype=='long'):
		size=l_long
	        ctype='l'
        elif (ctype=='L')|(ctype=='ulong'):
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
