#!/usr/bin/env python3

"""Extract a single field from the trace headers of  3D seismic volume to a 2D Numpy array.

This utility assumes the inline and crossline numbers are evenly spaced.
Each inline of the source data will be represented as a single row, and
each crossline as a single column in the resulting 2D array.

Usage: extract_trace_header_field.py [-h] [--null NULL]
                    segy-file npy-file field-name

Positional arguments:
  segy-file      Path to an existing SEG Y file of 3D seismic data
  npy-file       Path to the Numpy array file to be created for the timeslice
  field-name     Zero based index of the time slice to be extracted

Optional arguments:
  -h, --help     show this help message and exit
  --dtype DTYPE  Numpy data type. If not provided a dtype compatible with the
                 SEG Y data will be used.
  --null NULL    Sample value to use for missing or short traces.

Example:

  extract_trace_header_field.py stack_final_int8.sgy slice_800.npy ensemble_num
"""

import argparse
import os
import sys
import traceback

import numpy as np

from numpy import s_

from segpy.reader import create_reader
from segpy.trace_header import TraceHeaderRev1
from segpy_numpy.dtypes import make_dtype
from segpy_numpy.extract import extract_inline_3d, extract_trace_header_field_3d


class DimensionalityError(Exception):
    pass



def extract_header_field(segy_filename, out_filename, field_name, null=None):
    """Extract a timeslice from a 3D SEG Y file to a Numpy NPY file.

    Args:
        segy_filename: Filename of a SEG Y file.

        out_filename: Filename of the NPY file.

        inline_index: The zero-based index (increasing with depth) of the slice to be extracted.

        null: Optional sample value to use for missing or short traces. Defaults to zero.
    """
    header_field = getattr(TraceHeaderRev1, field_name)

    with open(segy_filename, 'rb') as segy_file:

        segy_reader = create_reader(segy_file)

        header_field_arrays = extract_trace_header_field_3d(segy_reader, [header_field], null)
        return header_field_arrays


def nullable_int(s):
    return None if not bool(s) else int(s)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("segy_file", metavar="segy-file",
                        help="Path to an existing SEG Y file of 3D seismic data")

    parser.add_argument("npy_file", metavar="npy-file",
                        help="Path to the Numpy array file to be created for the timeslice")

    parser.add_argument("field_name", metavar="field-name", type=str,
                        help="Name of the trace header field to be extracted", )

    parser.add_argument("--null",  type=nullable_int, default="",
                        help="Header value to use for missing or short traces.")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)

    try:
        extract_header_field(
            segy_filename=args.segy_file,
            out_filename=args.npy_file,
            field_name=args.field_name,
            null=args.null)
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


