#!/usr/bin/env python3

"""A simple example which times reading of all traces in a SEG Y file.

Usage:

    timed_reader.py <in.segy>

"""
from __future__ import print_function

import datetime

import os

import sys
import traceback

from segpy.reader import create_reader


def read_traces(in_filename):
    with open(in_filename, 'rb') as in_file:

        t0 = datetime.datetime.now()

        segy_reader = create_reader(in_file)

        t1 = datetime.datetime.now()

        for trace_index in segy_reader.trace_indexes():
            trace = segy_reader.trace_samples(trace_index)

        t2 = datetime.datetime.now()

    time_to_read_header = (t1 - t0).total_seconds()
    time_to_read_traces = (t2 - t1).total_seconds()
    time_to_read_both = (t2 - t0).total_seconds()

    print("Time to read headers : {} seconds", time_to_read_header)
    print("Time to read traces  : {} seconds", time_to_read_traces)
    print("Total time           : {} seconds", time_to_read_both)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        in_filename = argv[0]
    except IndexError:
        print(globals()['__doc__'], file=sys.stderr)
        return os.EX_USAGE

    try:
        read_traces(in_filename)
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
