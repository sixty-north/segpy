#!/usr/bin/env python3

"""Extract a timeslice from a 3D seismic volume to a Numpy array.

This utility assumes the inline and crossline numbers are evenly spaced.
Each inline of the source data will be represented as a single row, and
each crossline as a single column in the resulting 2D array.

Usage: timeslice.py [-h] [--dtype DTYPE] [--null NULL]
                    segy-file npy-file slice-index

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

import numpy as np

from segpy.reader import create_reader
from segpy_numpy.dtypes import make_dtype


class DimensionalityError(Exception):
    pass


def extract_timeslice(segy_filename, out_filename, slice_index, dtype=None, null=0):
    """Extract a timeslice from a 3D SEG Y file to a Numpy NPY file.

    Args:
        segy_filename: Filename of a SEG Y file.

        out_filename: Filename of the NPY file.

        slice_index: The zero-based index (increasing with depth) of the slice to be extracted.

        dtype: Optional Numpy dtype for the result array. If not provided a dtype compatible with
            the SEG Y data will be used.

        null: Optional sample value to use for missing or short traces. Defaults to zero.
    """
    with open(segy_filename, 'rb') as segy_file:

        segy_reader = create_reader(segy_file)

        if dtype is None:
            dtype = make_dtype(segy_reader.data_sample_format)

        if segy_reader.dimensionality != 3:
            raise DimensionalityError("Cannot slice {n} dimensional seismic.".format(segy_reader.dimensionality))

        i_size = segy_reader.num_inlines()
        x_size = segy_reader.num_xlines()
        t_size = segy_reader.max_num_trace_samples()

        if not (0 <= slice_index < t_size):
            raise ValueError("Time slice index {0} out of range {} to {}".format(slice_index, 0, t_size))

        timeslice = np.full((i_size, x_size), null, dtype)

        for inline_num, xline_num in segy_reader.inline_xline_numbers():
            trace_index = segy_reader.trace_index((inline_num, xline_num))
            trace = segy_reader.trace_samples(trace_index)

            try:
                sample = trace[slice_index]
            except IndexError:
                sample = null

            i_index = segy_reader.inline_numbers().index(inline_num)
            x_index = segy_reader.xline_numbers().index(xline_num)

            timeslice[i_index, x_index] = sample

        np.save(out_filename, timeslice)


def nullable_dtype(s):
    return None if s == "" else np.dtype(s)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("segy_file", metavar="segy-file",
                        help="Path to an existing SEG Y file of 3D seismic data")

    parser.add_argument("npy_file", metavar="npy-file",
                        help="Path to the Numpy array file to be created for the timeslice")

    parser.add_argument("slice_index", metavar="slice-index", type=int,
                        help="Zero based index of the time slice to be extracted", )

    parser.add_argument("--dtype", type=nullable_dtype, default="",
                        help="Numpy data type. If not provided a dtype compatible with the SEG Y data will be used.")

    parser.add_argument("--null",  type=float, default=0.0,
                        help="Sample value to use for missing or short traces.")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)

    try:
        extract_timeslice(args.segy_file,
                          args.npy_file,
                          args.slice_index,
                          args.dtype,
                          args.null)
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

