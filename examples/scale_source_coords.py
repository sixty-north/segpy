#!/usr/bin/env python3

"""Scale source coordinates values by a factor.

Usage: scale_source_coords.py <scale_factor> <input-segy-file> <output-segy-file>

Example:

  scale_source_coords.py 2.0 stack_final_int8.sgy stack_final_int8_scaled.sgy
"""

import os
import sys
import traceback

from segpy.dataset import DelegatingDataset
from segpy.reader import create_reader
from segpy.writer import write_segy


def make_progress_indicator(name):

    previous_integer_progress = -1

    def progress(p):
        nonlocal previous_integer_progress
        percent = p * 100.0
        current_integer_progress = int(percent)
        if current_integer_progress != previous_integer_progress:
            print("{} : {}%".format(name, current_integer_progress))
        previous_integer_progress = current_integer_progress

    return progress


class ScaledCoordinatesDataset(DelegatingDataset):

    def __init__(self, source_dataset, scale_factor):
        super().__init__(source_dataset)
        self._scale_factor = scale_factor

    def trace_header(self, trace_index):
        # Load the original trace header into header
        # Note: The meaning of 'source' in the next line
        #       is 'source dataset', i.e. the SEG Y dataset
        #       we are reading
        header = self.source.trace_header(trace_index)

        # Modify the some header values
        header.source_x *= self._scale_factor
        header.source_y *= self._scale_factor

        # Return the modified header
        return header


def transform(scale_factor, in_filename, out_filename):
    with open(in_filename, 'rb') as in_file, \
         open(out_filename, 'wb') as out_file:

        segy_reader = create_reader(in_file, progress=make_progress_indicator("Cataloging"))
        transformed_dataset = ScaledCoordinatesDataset(segy_reader, scale_factor)
        write_segy(out_file, transformed_dataset, progress=make_progress_indicator("Transforming"))


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        scale_factor = float(argv[0])
        in_filename = argv[1]
        out_filename = argv[2]
    except (ValueError, IndexError):
        print(globals()['__doc__'], file=sys.stderr)
        return os.EX_USAGE

    try:
        transform(scale_factor, in_filename, out_filename)
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


