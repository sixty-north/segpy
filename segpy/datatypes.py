"""Mappings between the coding systems used for sample types.
"""

# A mapping from data sample format codes to SEG Y types.
from collections import namedtuple

from segpy.ibm_float import MIN_IBM_FLOAT, MAX_IBM_FLOAT

DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE = {
    1: 'ibm',
    2: 'int32',
    3: 'int16',
    5: 'float32',
    8: 'int8'}

SEG_Y_TYPE_TO_DATA_SAMPLE_FORMAT = {v: k for k, v in DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE.items()}

# A mapping from SEG Y data types to format characters used by the
# Python Standard Library struct module
SEG_Y_TYPE_TO_CTYPE = {
    'int32':  'i',
    'nnint32': 'I',
    'int16':  'h',
    'nnint16': 'H',
    'int8': 'b',
    'nnint8': 'B',
    'float32':  'f',
    'ibm': 'ibm'}


# Human readable descriptions of the sample types.
SEG_Y_TYPE_DESCRIPTION = {
    'ibm': 'IBM 32 bit float',
    'int32': '32 bit signed integer',
    'nnint32': '32 bit non-negative integer',
    'int16': '16 bit signed integer',
    'nnint16': '16 bit unsigned integer',
    'float32': 'IEEE float32',
    'int8': '8 bit signed integer (byte)',
    'nnint8': '8 bit unsigned integer (byte)'}

# Sizes of various ctypes in bytes
CTYPE_TO_SIZE = dict(
    i=4,
    I=4,
    h=2,
    H=2,
    b=1,
    B=1,
    f=4,
    ibm=4)


def size_in_bytes(ctype):
    """The size in bytes of a ctype.
    """
    try:
        return CTYPE_TO_SIZE[ctype]
    except KeyError:
        raise ValueError("No such C-type {!r}".format(ctype))

Limits = namedtuple('Limits', ['min', 'max'])

LIMITS = {
    'ibm': Limits(MIN_IBM_FLOAT, MAX_IBM_FLOAT),
    'int32': Limits(-2147483648, 2147483647),
    'nnint32': Limits(0, 2147483647),
    'int16': Limits(-32768, 32767),
    'nnint16': Limits(0, 32767),
    'float32': Limits(-3.402823e38, 3.402823e38),
    'int8': Limits(-128, 127),
    'nnint8': Limits(0, 127)
}

PY_TYPES = {
    'ibm': float,
    'int32': int,
    'int16': int,
    'float32': float,
    'int8': int
}

ENDIAN = {
    '<': 'little',
    '>': 'big'
}
