#!/usr/bin/env python
#
# testsegy.py
#

import segypy


def test_read(filename):
    # Read Segy File
    with open(filename, 'rb') as f:
        return segypy.readSegy(f, filename)


def test_write(filename_out, data, sh, sth):
    sh['DataSampleFormat'] = 5
    sh['SegyFormatRevisionNumber'] = 100
    segypy.writeSegyStructure(filename_out, data, sh, sth)

    segypy.wiggle(data, sh, 2, .1, .1)

    f_ieee = 'data_IEEE.segy'
    f_ibm = 'data_IBM_REV1.segy'
    d_ieee, sh, sth = segypy.readSegy(f_ieee)
    d_ibm, sh, sth = segypy.readSegy(f_ibm)

    return d_ieee, d_ibm, data


def test_render(d_ieee, d_ibm, data):
    import pylab

    # imshow(Data)
    pylab.figure(1)
    pylab.imshow(d_ieee)
    pylab.title('ieee')
    pylab.show()

    pylab.figure(2)
    pylab.imshow(d_ibm)
    pylab.title('IBM')
    pylab.show()

    pylab.figure(3)
    pylab.imshow(data)
    pylab.title('TEST')
    pylab.show()

if __name__ == '__main__':
    filename = 'ld0057_file_00095.sgy'
    # filename = 'mini.sgy'
    # filename = 'data_IEEE.segy'
    # filename = 'data_IBM_REV1.segy'
    # filename = 'data_IBM_REV0.segy'
    # filename = 'data_1byteINT.segy'
    # filename = 'data_2byteINT.segy'
    # filename = 'data_4byteINT.segy'

    read_results = test_read(filename)
    # write_results = test_write('testout.segy', *read_results)
    # test_render(*write_results)
