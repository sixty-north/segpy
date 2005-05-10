#
#
# testsegy.py
#
import struct
import segypy

filename='mini.sgy'
#filename='lyngbytst1.sgy';
#filename='data_IEEE.segy';
filename='data_IBM_REV1.segy';
#filename='data_IBM_REV0.segy';
#filename='data_1byteINT.segy';
#filename='data_2byteINT.segy';
#filename='data_4byteINT.segy';


# Set verbose level
segypy.verbose=5;

# Read Segy File
Data,SH,STH=segypy.readSegy(filename);


