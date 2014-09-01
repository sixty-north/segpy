DATA_SAMPLE_FORMAT = {1: 'ibm',
                      2: 'l',
                      3: 'h',
                      5: 'f',
                      8: 'b'}

# A mapping from SEG Y data types to format characters used by the struct module,
# known a 'ctypes'
CTYPES = {'l': 'l',
          'long':   'l',
          'int32':  'l',

          'L': 'L',
          'ulong':  'L',
          'uint32': 'L',

          'h': 'h',
          'short':  'h',
          'int16':  'h',

          'H': 'H',
          'ushort': 'H',
          'uint16': 'H',

          'c': 'b',
          'char': 'b',
          'b': 'b',

          'B': 'B',
          'uchar':  'B',

          'f': 'f',
          'float':  'f',

          'ibm': 'ibm'}

# TODO This is redundant with data in the SH_def below
CTYPE_DESCRIPTION = {'ibm': 'IBM float',
                     'l':   '32 bit signed integer',
                     'L':   '32 bit unsigned integer',
                     'h':   '16 bit signed integer',
                     'H':   '16 bit unsigned integer',
                     'f':   'IEEE float32',
                     'b':   '8 bit signed char',
                     'B':   '8 bit unsigned char'}


SIZES = dict(l=4,
             L=4,
             h=2,
             H=2,
             b=1,
             B=1,
             f=4,
             ibm=4)


def size_in_bytes(ctype):
    return SIZES[ctype]
