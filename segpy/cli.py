import json

import docopt_subcommands as dsc
import segpy
from segpy.reader import create_reader


@dsc.command('metadata')
def handle_metadata(args):
    """usage: {program} {command} <filename>

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


def main(argv=None):
    dsc.main(
        'segpy',
        'segpy-{}'.format(segpy.__version__))
