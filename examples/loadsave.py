#!/usr/bin/env python3

"""A simple example which loads a SEG Y file and saves it again.

Usage:

    loadsave.py <in.segy> <out.segy>

"""

from __future__ import print_function

import os

import sys
import traceback

from segpy.reader import create_reader
from segpy.writer import write_segy


def load_save(in_filename, out_filename):
    with open(in_filename, 'rb') as in_file, \
         open(out_filename, 'wb') as out_file:

        segy_reader = create_reader(in_file)
        write_segy(out_file, segy_reader)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        in_filename = argv[0]
        out_filename = argv[1]
    except IndexError:
        print(globals()['__doc__'], file=sys.stderr)
        return os.EX_USAGE

    try:
        load_save(in_filename, out_filename)
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
