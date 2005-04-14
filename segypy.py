"""
A python module for reading/writing/manipuating 
SEG-Y formatted filed

segy.segypy_version 	: The version of SegyPY
segy.segypy_verbose 	: Amount of verbose information to the screen.
segy.getValue 		: Get a value from a binary string
segy.getSegyHeader  	: Get SEGY header form file
segy.readSegy		: Read SEGY file
"""
#
# segypy : A Python module for reading and writing SEG-Y formatted data
#
# (C) Thomas Mejer Hansen, 2005
#

#import struct
from struct import *
from Numeric import *
#from numarray import *

# SOME GLOBAL PARAMETERS
segypy_version=0.1
segypy_verbose=10;

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


def version():
	return segypy_version

def print_version():
	print 'SegyPY version is ', segypy_version

def printverbose(txt,level):
        if level<segypy_verbose:
		print 'SegyPY',segypy_version,': ',txt



#def read(filename):
#	read_segy(filename)
#
#def write(filename):
#	write_segy(filename)
