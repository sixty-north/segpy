#!/usr/bin/env python3

"""Scale sample values by a factor.

Usage: scale_samples.py <scale_factor> <input-segy-file> <output-segy-file>

Example:

  scale_samples.py 2.0 stack_final_int8.sgy stack_final_int8_doubled.sgy
"""

import os
import sys
import traceback

from segpy.dataset import DelegatingDataset
from segpy.datatypes import LIMITS, PY_TYPES
from segpy.reader import create_reader
from segpy.writer import write_segy


class DimensionalityError(Exception):
    pass


class ScaledSamplesDataset(DelegatingDataset):

    def __init__(self, source_dataset, scale_factor):
        super().__init__(source_dataset)
        self._scale_factor = scale_factor
        self._limits = LIMITS[source_dataset.data_sample_format]
        self._py_type = PY_TYPES[source_dataset.data_sample_format]

    def _transform(self, sample):
        # Do the transformation
        scaled_sample = sample * self._scale_factor

        # Ensure that we use a Python type compatible with the data sample format
        typed_sample = self._py_type(scaled_sample)

        # Clip to the range supported by the data sample format
        clipped_sample = max(self._limits.min, min(self._limits.max, typed_sample))
        return clipped_sample

    def trace_samples(self, trace_index, start=None, stop=None):
        return [self._transform(sample) for sample in self.source.trace_samples(trace_index, start, stop)]


def transform(scale_factor, in_filename, out_filename):
    with open(in_filename, 'rb') as in_file, \
         open(out_filename, 'wb') as out_file:

        segy_reader = create_reader(in_file)
        transformed_dataset = ScaledSamplesDataset(segy_reader, scale_factor)
        write_segy(out_file, transformed_dataset)


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


