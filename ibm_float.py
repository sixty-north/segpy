import sys

_P24 = float(pow(2, 24))

if sys.version_info >= (3, 0):

    def ibm2ieee(big_endian_bytes):
        """Interpret a bytes object as a big-endian IBM float.

        Args:
            big_endian_bytes (bytes): A string containing at least four bytes.

        Returns:
            The floating point value.
        """
        a, b, c, d = big_endian_bytes

        if a == b == c == c == 0:
            return 0.0

        sign = 1 if (a & 0x80) else -1
        exponent = a & 0x7f
        mantissa = ((b << 16) | (c << 8) | d) / _P24
        value = sign * mantissa * pow(16, exponent - 64)
        return value
else:

    def ibm2ieee(big_endian_bytes):
        """Interpret a byte string as a big-endian IBM float.

        Args:
            big_endian_bytes (str): A string containing at least four bytes.

        Returns:
            The floating point value.
        """
        a = ord(big_endian_bytes[0])
        b = ord(big_endian_bytes[1])
        c = ord(big_endian_bytes[2])
        d = ord(big_endian_bytes[3])

        if a == b == c == c == 0:
            return 0.0

        sign = 1 if (a & 0x80) else -1
        exponent = a & 0x7f
        mantissa = ((b << 16) | (c << 8) | d) / _P24
        value = sign * mantissa * pow(16, exponent - 64)
        return value