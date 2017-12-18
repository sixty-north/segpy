"""{program} - Interrogation of SEG Y seismic data.

Usage: {program} [options] <command> [<args> ...]

Options:
  -h --help          Show this screen.
  --log-level=LEVEL  One of DEBUG, INFO, WARNING, ERROR
                     or CRITICAL. [default: WARNING]

Commands:
  {available_commands}

See '{program} help <command>' for help on specific commands.
"""

import json
import logging
import os

import segpy
import sys

from docopt_subcommands import Subcommands

from segpy.reader import create_reader


def common_option_handler(config):
    log_level = config['--log-level']
    try:
        segpy.log.setLevel(log_level)
    except ValueError:
        return os.EX_USAGE

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    segpy.log.addHandler(handler)


commands = Subcommands(program='segpy',
                       version='segpy-{}'.format(segpy.__version__),
                       doc_template=__doc__,
                       common_option_handler=common_option_handler)


@commands.command('metadata')
def handle_metadata(args):
    """Usage: {program} {command} <filename>

    Print metadata for a SEGY file.
    """

    result = {}

    filename = args['<filename>']
    with open(filename, 'rb') as fh:
        reader = create_reader(fh)
        result['num_traces'] = reader.num_traces()
        result['dimensionality'] = reader.dimensionality
        result['data_sample_format'] = reader.data_sample_format
        result['max_num_trace_samples'] = reader.max_num_trace_samples()

    print(json.dumps(result))


@commands.command('report')
def report(args):
    """Usage: {program} {command} <filename>

    Print a human-readable report of the file contents.
    """
    filename = args['<filename>']

    with open(filename, 'rb') as segy_file:
        segy_reader = create_reader(segy_file)
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
    commands(argv)


__doc__ = commands.top_level_doc
