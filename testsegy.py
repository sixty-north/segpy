#!/usr/bin/env python
#
# testsegy.py
#
import struct

import segypy

filename='ld0057_file_00095.sgy';
#filename='mini.sgy'
#filename='data_IEEE.segy';
#filename='data_IBM_REV1.segy';
#filename='data_IBM_REV0.segy';
#filename='data_1byteINT.segy';
#filename='data_2byteINT.segy';
#filename='data_4byteINT.segy';

# Set verbose level
segypy.verbose=1;

# Read Segy File
Data,SH,STH=segypy.readSegy(filename);



exit


filename_out='testout.segy';
SH['DataSampleFormat']=5;
SH['SegyFormatRevisionNumber']=100;
segypy.writeSegyStructure(filename_out,Data,SH,STH);

segypy.wiggle(Data,SH,2,.1,.1)

f_ieee='data_IEEE.segy';
f_ibm='data_IBM_REV1.segy';
d_ieee,SH,STH=segypy.readSegy(f_ieee);
d_ibm,SH,STH=segypy.readSegy(f_ibm);


import pylab


#imshow(Data)
pylab.figure(1)
pylab.imshow(d_ieee)
pylab.title('ieee')
pylab.show()

pylab.figure(2)
pylab.imshow(d_ibm)
pylab.title('IBM')
pylab.show()

pylab.figure(3)
pylab.imshow(Data)
pylab.title('TEST')
pylab.show()
