#
#
# testsegy.py
#
import struct
import segypy

filename='mini.sgy'

data = open(filename).read()

l_long = struct.calcsize('l')
l_ulong = struct.calcsize('L')
l_short = struct.calcsize('h')
l_ushort = struct.calcsize('H')

segypy_version=segypy.version()

print 'filename=',filename


#index=3200;
#Job,size = segypy.getValue(data,index,'l','>')
#Job,size = segypy.getValue(data,index,'long','>')
#index=index+size
#Line,size = segypy.getValue(data,index,'l','>')
#index =index+size
#Reel,size = segypy.getValue(data,index,'l','>')
#index=index+size
#DataTracePerEnsemble, size = segypy.getValue(data,index,'h','>')
#DataTracePerEnsemble, size = segypy.getValue(data,index,'short','>')

print "GET SEGY GEADER"
SH=segypy.getSegyHeader(filename)

print SH
#print SH['Reel']

print "TESTING READING OF SEGY FILE"
segypy.readSegyFast(filename);


