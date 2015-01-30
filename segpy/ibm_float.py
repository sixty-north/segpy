from math import frexp, isnan, isinf

from segpy.portability import long_int, byte_string, four_bytes

MIN_IBM_FLOAT = -7.2370051459731155e+75
LARGEST_NEGATIVE_NORMAL_IBM_FLOAT = -5.397605346934028e-79
SMALLEST_POSITIVE_NORMAL_IBM_FLOAT = 5.397605346934028e-79
MAX_IBM_FLOAT = 7.2370051459731155e+75

_IBM_FLOAT32_BITS_PRECISION = 24
_L24 = long_int(2) ** _IBM_FLOAT32_BITS_PRECISION
_F24 = float(pow(2, _IBM_FLOAT32_BITS_PRECISION))


def ibm2ieee(big_endian_bytes):
    """Interpret a byte string as a big-endian IBM float.

    Args:
        big_endian_bytes (str): A string containing at least four bytes.

    Returns:
        The floating point value.
    """
    a, b, c, d = four_bytes(big_endian_bytes)

    if a == b == c == d == 0:
        return 0.0

    sign = -1 if (a & 0x80) else 1
    exponent = a & 0x7f
    mantissa = ((b << 16) | (c << 8) | d) / _F24

    value = sign * mantissa * pow(16, exponent - 64)
    return value


def ieee2ibm(f):
    """Covert a float to four big-endian bytes representing an IBM float.

    Args:
        f (float): The value to be converted.

    Returns:
        A bytes object (Python 3) or a string (Python 2) containing four
        bytes representing a big-endian IBM float.

    Raises:
        OverflowError: If f is outside the representable range.
        ValueError: If f is NaN or infinite.
        FloatingPointError: If f cannot be represented without total loss of precision.
    """
    if f == 0:
        # There are many potential representations of zero - this is the standard one
        return b'\x00\x00\x00\x00'

    if isnan(f):
        raise ValueError("NaN cannot be represented in IBM floating point")

    if isinf(f):
        raise ValueError("Infinities cannot be represented in IBM floating point")

    if f < MIN_IBM_FLOAT:
        raise OverflowError("IEEE Floating point value {} is less than the "
                            "representable minimum for IBM floats.".format(f))

    if f > MAX_IBM_FLOAT:
        raise OverflowError("IEEE Floating point value {} is greater than the "
                            "representable maximum for IBM floats".format(f))

    # Now compute m and e to satisfy:
    #
    #  f = m * 2^e
    #
    # where 0.5 <= abs(m) < 1
    # except when f == 0 in which case m == 0 and e == 0, which we've already
    # dealt with.
    m, e = frexp(f)

    # Convert the fraction (m) into an integer representation. IEEE float32
    # numbers have 23 explicit (24 implicit) bits of precision.

    mantissa = abs(long_int(m * _L24))
    exponent = e
    sign = 0x80 if f < 0 else 0x00

    # IBM single precision floats are of the form
    # (-1)^sign * 0.significand * 16^(exponent-64)

    # Adjust the exponent, and the mantissa in sympathy so it is
    # a multiple of four, so it can be expressed in base 16
    remainder = exponent % 4
    if remainder != 0:
        shift = 4 - remainder
        mantissa >>= shift
        exponent += shift

    exponent_16 = exponent >> 2            # Divide by four to convert to base 16
    exponent_16_biased = exponent_16 + 64  # Add the exponent bias of 64

    # If the biased exponent is negative, we try to use a subnormal representation
    if exponent_16_biased < 0:
        shift_16 = 0 - exponent_16_biased
        exponent_16_biased += shift_16  # An increment of the base-16 exponent must be balanced by
        mantissa >>= 4 * shift_16       # A division by 16 (four binary places) in the mantissa
        if mantissa == 0:
            raise FloatingPointError("IEEE Floating point value {} is smaller than the "
                                     "smallest subnormal number for IBM floats.".format(f))

    a = sign | exponent_16_biased
    b = (mantissa >> 16) & 0xff
    c = (mantissa >> 8) & 0xff
    d = mantissa & 0xff

    return byte_string((a, b, c, d))
