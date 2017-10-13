#!/usr/bin/env python3

"""Convert to a given data sample format.

Usage: convert_sample_type.py <data-sample-format> <input-segy-file> <output-segy-file>

Example:

  convert_sample_type.py float32 ibm.sgy ieee.sgy
"""

import os
import sys
import traceback

from segpy.dataset import DelegatingDataset
from segpy.datatypes import LIMITS, PY_TYPES, SEG_Y_TYPE_TO_DATA_SAMPLE_FORMAT, SEG_Y_TYPE_DESCRIPTION
from segpy.reader import create_reader
from segpy.writer import write_segy


class DimensionalityError(Exception):
    pass


class ConvertingDataset(DelegatingDataset):

    def __init__(self, source_dataset, data_sample_format):
        """
        Args:
            source_dataset: A Dataset containing the source data.
            data_sample_format: One of 'ibm', 'int32', 'int16', 'float32', 'int8'
        """
        super().__init__(source_dataset)
        self._limits = LIMITS[data_sample_format]

        self._binary_reel_header = self._source.binary_reel_header.copy(
            data_sample_format=SEG_Y_TYPE_TO_DATA_SAMPLE_FORMAT[data_sample_format])

        self._py_type = PY_TYPES[data_sample_format]

    @property
    def binary_reel_header(self):
        return self._binary_reel_header

    def _transform(self, sample):
        # Ensure that we use a Python type compatible with the data sample format
        typed_sample = self._py_type(sample)

        # Clip to the range supported by the data sample format
        clipped_sample = max(self._limits.min, min(self._limits.max, typed_sample))
        return clipped_sample

    def trace_samples(self, trace_index, start=None, stop=None):
        return [self._transform(sample) for sample in self.source.trace_samples(trace_index, start, stop)]


def transform(data_sample_format, in_filename, out_filename):
    with open(in_filename, 'rb') as in_file, \
         open(out_filename, 'wb') as out_file:

        segy_reader = create_reader(in_file)
        sample_type = segy_reader.data_sample_format
        if sample_type != 'ibm':
            raise RuntimeError("Source file {} has {} sample type".format(in_filename, sample_type))
        transformed_dataset = ConvertingDataset(segy_reader, data_sample_format)
        write_segy(out_file, transformed_dataset)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        data_sample_format = argv[0]
        in_filename = argv[1]
        out_filename = argv[2]
    except (ValueError, IndexError):
        print(globals()['__doc__'], file=sys.stderr)
        return os.EX_USAGE

    if data_sample_format not in SEG_Y_TYPE_DESCRIPTION:
        print("Accepted data sample formats:")
        for name, description in SEG_Y_TYPE_DESCRIPTION.items():
            print("{} : {}".format(name, description))
        return os.EX_USAGE

    if out_filename == in_filename:
        print("Output filename {} is the same as input filename".format(out_filename, in_filename))
        return os.EX_USAGE

    try:
        transform(data_sample_format, in_filename, out_filename)
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


