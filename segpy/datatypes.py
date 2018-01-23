"""Mappings between the coding systems used for sample types.
"""

# A mapping from data sample format codes to SEG Y types.
from collections import namedtuple
from enum import IntEnum, Enum

from segpy.ibm_float import MIN_IBM_FLOAT, MAX_IBM_FLOAT


class DataSampleFormat(IntEnum):
    """Data sample format code. Mandatory for all data.
    1 = 4-byte IBM floating-point,
    2 = 4-byte, two's complement integer,
    3 = 2-byte, two's complement integer,
    4 = 4-byte fixed-point with gain (obsolete),
    5 = 4-byte IEEE floating-point,
    6 = Not currently used,
    7 = Not currently used,
    8 = 1-byte, two's complement integer."""
    IBM = 1
    INT32 = 2
    INT16 = 3
    FLOAT32 = 5
    INT8 = 8


class SegYType(str, Enum):
    INT32 = 'int32'
    NNINT32 = 'nnint32'
    INT16 = 'int16'
    NNINT16 = 'nnint16'
    INT8 = 'int8'
    NNINT8 = 'nnint8'
    FLOAT32 = 'float32'
    IBM = 'ibm'


DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE = {
    DataSampleFormat.IBM: SegYType.IBM,
    DataSampleFormat.INT32: SegYType.INT32,
    DataSampleFormat.INT16: SegYType.INT16,
    DataSampleFormat.FLOAT32: SegYType.FLOAT32,
    DataSampleFormat.INT8: SegYType.INT8}


SEG_Y_TYPE_TO_DATA_SAMPLE_FORMAT = {v: k for k, v in DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE.items()}


# A mapping from SEG Y data types to format characters used by the
# Python Standard Library struct module
SEG_Y_TYPE_TO_CTYPE = {
    SegYType.INT32:  'i',
    SegYType.NNINT32: 'I',
    SegYType.INT16:  'h',
    SegYType.NNINT16: 'H',
    SegYType.INT8: 'b',
    SegYType.NNINT8: 'B',
    SegYType.FLOAT32:  'f',
    SegYType.IBM: 'ibm'}


# Human readable descriptions of the sample types.
SEG_Y_TYPE_DESCRIPTION = {
    SegYType.IBM: 'IBM 32 bit float',
    SegYType.INT32: '32 bit signed integer',
    SegYType.NNINT32: '32 bit non-negative integer',
    SegYType.INT16: '16 bit signed integer',
    SegYType.NNINT16: '16 bit non-negative integer',
    SegYType.FLOAT32: 'IEEE float32',
    SegYType.INT8: '8 bit signed integer (byte)',
    SegYType.NNINT8: '8 bit unsigned integer (byte)'}


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
    SegYType.IBM: Limits(MIN_IBM_FLOAT, MAX_IBM_FLOAT),
    SegYType.INT32: Limits(-2147483648, 2147483647),
    SegYType.NNINT32: Limits(0, 2147483647),
    SegYType.INT16: Limits(-32768, 32767),
    SegYType.NNINT16: Limits(0, 32767),
    SegYType.FLOAT32: Limits(-3.402823e38, 3.402823e38),
    SegYType.INT8: Limits(-128, 127),
    SegYType.NNINT8: Limits(0, 127)
}

PY_TYPES = {
    SegYType.IBM: float,
    SegYType.INT32: int,
    SegYType.NNINT32: int,
    SegYType.INT16: int,
    SegYType.NNINT16: int,
    SegYType.FLOAT32: float,
    SegYType.INT8: int,
    SegYType.NNINT8: int
}

ENDIAN = {
    '<': 'little',
    '>': 'big'
}
