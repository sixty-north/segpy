#
#
# testsegy.py
#
import struct
import segypy

filename='mini.sgy'
#data = open(filename).read()
# reading SEG-Y header
#SH=segypy.getSegyHeader(filename)
#print SH
#print SH['Reel']

# Set verbose level
segypy.verbose=1;

# Read Segy File
Data,SH,STH=segypy.readSegy(filename);


