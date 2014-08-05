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


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('filename',
                        help='The SEGY input file')

    parser.add_argument('--output', '-o',
                        dest='outfile',
                        default='',
                        help='The output file (optional).')

    parser.add_argument('--render_test', '-r',
                        dest='render_test',
                        action='store_true',
                        help='Whether to test rendering (only applies if '
                             'output is produced.)')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    read_results = test_read(args.filename)

    if args.outfile:
        write_results = test_write(args.outfile, *read_results)

        if args.render_test:
            test_render(*write_results)
