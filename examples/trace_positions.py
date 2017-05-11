#!/usr/bin/env python3

"""Extract a timeslice from a 3D seismic volume to a Numpy array.

This utility assumes the inline and crossline numbers are evenly spaced.
Each inline of the source data will be represented as a single row, and
each crossline as a single column in the resulting 2D array.

Usage: trace_positions.py [-h] segy-file

Positional arguments:
  segy-file      Path to an existing SEG Y file of 3D seismic data
  npy-file       Path to the Numpy array file to be created for the timeslice
  slice-index    Zero based index of the time slice to be extracted

Optional arguments:
  -h, --help     show this help message and exit
  --dtype DTYPE  Numpy data type. If not provided a dtype compatible with the
                 SEG Y data will be used.
  --null NULL    Sample value to use for missing or short traces.

Example:

  timeslice.py stack_final_int8.sgy slice_800.npy 800 --null=42.0 --dtype=f
"""

import argparse
import os
import sys
import traceback

from segpy.reader import create_reader


class DimensionalityError(Exception):
    pass


def extract_trace_positions(segy_filename):
    """Extract a timeslice from a 3D SEG Y file to a Numpy NPY file.

    Args:
        segy_filename: Filename of a SEG Y file.
    """
    with open(segy_filename, 'rb') as segy_file:

        segy_reader = create_reader(segy_file)

        for trace_index in segy_reader.trace_indexes():
            trace_header = segy_reader.trace_header(trace_index)
            trace_position = (trace_header.cdp_x,
                              trace_header.cdp_y)
            print(trace_index, trace_position)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("segy_file", metavar="segy-file",
                        help="Path to an existing SEG Y file of 3D seismic data")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)

    try:
        extract_trace_positions(args.segy_file)
    except (FileNotFoundError, IsADirectoryError) as e:
        print(e, file=sys.stderr)
        return os.EX_NOINPUT
    except PermissionError as e:
        print(e, file=sys.stderr)
        return os.EX_NOPERM
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return os.EX_SOFTWARE
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())


