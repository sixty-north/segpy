#!/usr/bin/env python3

"""Demonstrates how to customise a header format.

Standard SEG-Y requires that all header fields are two's complement (i.e. signed)
integers with a width of two or four bytes. In Segpy these are represented by the
types Int16 and Int32 from the field_types module.  For many header fields,
negative values would be nonsensical, so in the header specifications field values
can be further constrained to be non-negative by the use of the NNInt16 and NNInt32
types which require non-negative (NN) values. Note that these are not the same as
*unsigned* two- or four-byte integers, which would have an expanded range.

In this module, we show how to define and use a non-standard UInt16 type which
can accommodate the full unsigned 16-bit range from 0 to 65535.

Usage:

    custom_header.py <in.segy>

"""

import os

import sys
import traceback

from segpy.binary_reel_header import BinaryReelHeader
from segpy.datatypes import SegYType
from segpy.field_types import IntFieldMeta
from segpy.header import field
from segpy.reader import create_reader


# Standard SEG-Y does not support 16-bit unsigned integer values in headers.
# This section customises SEG-Y to support them.

class UInt16(int,
            metaclass=IntFieldMeta,
            min_value=0,       # Use the full-range for unsigned
            max_value=65535,   # 16-bit integers
            seg_y_type=SegYType.NNINT16):   # The underlying NNINT16 type is actually read as an unsigned type.
    """16-bit unsigned integer."""
    pass


# Subclass the standard reel header to specialize one of its fields to have a type of UInt16.

class CustomBinaryReelHeader(BinaryReelHeader):

    num_samples = field(
        UInt16, offset=3221, default=0, documentation=
        """Number of samples per data trace. Mandatory for all types of data.
        Note: The sample interval and number of samples in the Binary File Header should be for the primary set of
        seismic data traces in the file."""
    )


def report_segy(in_filename):
    with open(in_filename, 'rb') as in_file:

        # Create a reader using the CustomBinaryReelHeader format.
        segy_reader = create_reader(
            in_file,
            binary_reel_header_format=CustomBinaryReelHeader)

        print()
        print("Filename:             ", segy_reader.filename)
        print("SEG Y revision:       ", segy_reader.revision)
        print("Number of traces:     ", segy_reader.num_traces())
        print("Data format:          ",
              segy_reader.data_sample_format_description)
        print("Dimensionality:       ", segy_reader.dimensionality)

        try:
            print("Number of CDPs:       ", segy_reader.num_cdps())
        except AttributeError:
            pass

        try:
            print("Number of inlines:    ", segy_reader.num_inlines())
            print("Number of crosslines: ", segy_reader.num_xlines())
        except AttributeError:
            pass

        print("=== BEGIN TEXTUAL REEL HEADER ===")
        for line in segy_reader.textual_reel_header:
            print(line[3:])
        print("=== END TEXTUAL REEL HEADER ===")
        print()
        print("=== BEGIN EXTENDED TEXTUAL HEADER ===")
        print(segy_reader.extended_textual_header)
        print("=== END EXTENDED TEXTUAL_HEADER ===")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        in_filename = argv[0]
    except IndexError:
        print(globals()['__doc__'], file=sys.stderr)
        return os.EX_USAGE

    try:
        report_segy(in_filename)
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