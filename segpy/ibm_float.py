from math import frexp, isnan, isinf, trunc, floor, gcd
from numbers import Real, Rational

from segpy.util import four_bytes


IBM_ZERO_BYTES = b'\x00\x00\x00\x00'
IBM_NEGATIVE_ONE_BYTES = b'\xc1\x10\x00\x00'
IBM_POSITIVE_ONE_BYTES = b'A\x10\x00\x00'

MIN_IBM_FLOAT = -7.2370051459731155e+75
LARGEST_NEGATIVE_NORMAL_IBM_FLOAT = -5.397605346934028e-79
SMALLEST_POSITIVE_NORMAL_IBM_FLOAT = 5.397605346934028e-79
MAX_IBM_FLOAT = 7.2370051459731155e+75

MAX_BITS_PRECISION_IBM_FLOAT = 24
MIN_BITS_PRECISION_IBM_FLOAT = 21  # The first 3 bits of the mantissa may be zero
EPSILON_IBM_FLOAT = pow(2.0, -(MIN_BITS_PRECISION_IBM_FLOAT - 1))
_L24 = 2 ** MAX_BITS_PRECISION_IBM_FLOAT
_F24 = float(pow(2, MAX_BITS_PRECISION_IBM_FLOAT))

_L21 = 2 ** MIN_BITS_PRECISION_IBM_FLOAT

EXPONENT_BASE = 16
EXPONENT_BIAS = 64

MIN_EXACT_INTEGER_IBM_FLOAT = -2**MAX_BITS_PRECISION_IBM_FLOAT
MAX_EXACT_INTEGER_IBM_FLOAT = 2**MIN_BITS_PRECISION_IBM_FLOAT


def ibm2ieee(big_endian_bytes):
    """Interpret a byte string as a big-endian IBM float.

    Args:
        big_endian_bytes (bytes): A byte-string containing at least four bytes.

    Returns:
        The floating point value.
    """
    a, b, c, d = four_bytes(big_endian_bytes)

    if b == c == d == 0:
        return 0.0

    sign = -1 if (a & 0x80) else 1
    exponent_16_biased = a & 0x7f
    mantissa = ((b << 16) | (c << 8) | d) / _F24

    value = sign * mantissa * pow(EXPONENT_BASE, exponent_16_biased - EXPONENT_BIAS)
    return value


BITS_PER_NYBBLE = 4


def ieee2ibm(f):
    """Convert a float to four big-endian bytes representing an IBM float.

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

    mantissa = abs(int(m * _L24))
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
    exponent_16_biased = exponent_16 + EXPONENT_BIAS  # Add the exponent bias of 64

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

    return bytes((a, b, c, d))


class IBMFloat(Real):

    __slots__ = ['_data']

    def __new__(cls, b):
        obj = object.__new__(cls)

        data = bytes(b)
        num_bytes = len(data)
        if num_bytes != 4:
            raise ValueError("{} cannot be constructed from {} values".format(cls.__name__, num_bytes))
        obj._data = data
        return obj

    @classmethod
    def from_float(cls, f):
        """Construct an IBMFloat from an IEEE float.

        Args:
            f (float): The value to be converted.

        Returns:
            An IBMFloat.

        Raises:
            OverflowError: If f is outside the representable range.
            ValueError: If f is NaN or infinite.
            FloatingPointError: If f cannot be represented without total loss of precision.
        """
        if isinstance(f, IBMFloat):
            return f
        return cls(ieee2ibm(f))

    @classmethod
    def from_float_without_underflow(cls, f):
        """Construct an IBMFloat from an IEEE float.

        Args:
            f (float): The value to be converted. If the provided
                IEEE value underflows the smallest representable
                IBM value, this function returns zero.

        Returns:
            An IBMFloat.

        Raises:
            OverflowError: If f is outside the representable range.
            ValueError: If f is NaN or infinite.
        """
        try:
            buffer = ieee2ibm(f)
        except FloatingPointError:  # Underflow
            return IBM_FLOAT_ZERO
        else:
            return cls(buffer)

    @classmethod
    def from_real(cls, f):
        return cls.from_float(f)

    @classmethod
    def from_bytes(cls, b):
        return cls(b)

    @classmethod
    def ldexp(cls, fraction, exponent):
        """Make an IBMFloat from fraction and exponent.

        The is the inverse function of IBMFloat.frexp()

        Args:
            fraction: A Real in the range -1.0 to 1.0.
            exponent: An integer in the range -256 to 255 inclusive.
        """
        if not (-1.0 <= fraction <= 1.0):
            raise ValueError("ldexp fraction {!r} out of range -1.0 to +1.0")

        if not (-256 <= exponent < 256):
            raise ValueError("ldexp exponent {!r} out of range -256 to 256")

        ieee = fraction * 2**exponent
        return IBMFloat.from_float(ieee)

    @property
    def signbit(self):
        """True if the value is negative, otherwise False."""
        return bool(self._data[0] & 0x80)

    def __float__(self):
        return ibm2ieee(self._data)

    def __bytes__(self):
        return self._data

    def __repr__(self):
        return "{}(bytes([{}])) ≈ {!r}".format(
            self.__class__.__name__,
            ', '.join('0x{:02x}'.format(b) for b in self._data),
            float(self))

    def __str__(self):
        return str(float(self))

    def __bool__(self):
        return not self.is_zero()

    def is_zero(self):
        return self.int_mantissa == 0

    def is_subnormal(self):
        if self.is_zero():
            # Only one of the many possible representations of zero is considered 'normal' - all the zeros
            return not all(b == 0 for b in self._data)

        return self._data[1] < 16

    def zero_subnormal(self):
        return IBM_FLOAT_ZERO if self.is_subnormal() else self

    def frexp(self):
        """Obtain the fraction and exponent.

        Returns:
            A pair where the first item is the fraction in the range -1.0 and +1.0 and the
            exponent is an integer such that f = fraction * 2**exponent
        """
        sign = -1 if self.signbit else 1
        mantissa = sign * self.int_mantissa / _F24
        exp_2 = self.exp16 * 4
        return mantissa, exp_2

    def as_integer_ratio(self):
        sign = -1 if self.signbit else 1
        e16 = self.exp16
        if e16 >= 0:
            numerator = self.int_mantissa * EXPONENT_BASE**self.exp16
            denominator = _L24
        else:
            numerator = self.int_mantissa
            denominator = _L24 * EXPONENT_BASE**abs(self.exp16)
        divisor = gcd(numerator, denominator)
        reduced_numerator = sign * numerator // divisor
        reduced_denominator = denominator // divisor
        return reduced_numerator, reduced_denominator

    def __pos__(self):
        return self

    def __neg__(self):
        if self.is_zero():
            return IBM_FLOAT_ZERO

        data = self._data
        return IBMFloat((data[0] ^ 0b10000000,
                         data[1],
                         data[2],
                         data[3]))

    def __abs__(self):
        if self.is_zero():
            return IBM_FLOAT_ZERO

        data = self._data
        return IBMFloat((data[0] & 0b01111111,
                         data[1],
                         data[2],
                         data[3]))

    def __eq__(self, rhs):
        lhs = self

        if lhs is rhs:
            return True

        if isinstance(rhs, float):
            if isnan(rhs) or isinf(rhs):
                return 0.0 == rhs
            lhs_numerator, lhs_denominator = lhs.as_integer_ratio()
            rhs_numerator, rhs_denominator = rhs.as_integer_ratio()
            return (lhs_numerator == rhs_numerator) and (lhs_denominator == rhs_denominator)

        if isinstance(rhs, Rational):
            lhs_numerator, lhs_denominator = lhs.as_integer_ratio()
            return (lhs_numerator == rhs.numerator) and (lhs_denominator == rhs.denominator)

        if not isinstance(rhs, IBMFloat):
            return NotImplemented

        if lhs._data == rhs._data:
            return True

        lhs_sign = lhs.signbit
        rhs_sign = rhs.signbit

        if lhs_sign != rhs_sign:
            return False

        nlhs = lhs.try_normalize()
        nrhs = rhs.try_normalize()

        if not (nlhs.is_subnormal() or nrhs.is_subnormal()):
            # Both of the numbers are normalised
            return nlhs._data == nrhs._data

        # Either or both of the numbers are subnormal
        lhs_exp16 = nlhs.exp16
        rhs_exp16 = nrhs.exp16

        lhs_mantissa = nlhs.int_mantissa
        rhs_mantissa = nrhs.int_mantissa

        if lhs_exp16 < rhs_exp16:
            delta_exp16 = rhs_exp16 - lhs_exp16
            lhs_mantissa >>= 4 * delta_exp16
            lhs_exp16 += delta_exp16

        if lhs_exp16 > rhs_exp16:
            delta_exp16 = lhs_exp16 - rhs_exp16
            rhs_mantissa >>= 4 * delta_exp16
            rhs_exp16 += delta_exp16

        assert lhs_exp16 == rhs_exp16
        return lhs_mantissa == rhs_mantissa

    @property
    def exp16(self):
        """The base 16 exponent."""
        exponent_16_biased = self._data[0] & 0x7f
        exponent_16 = exponent_16_biased - EXPONENT_BIAS
        return exponent_16

    @property
    def int_mantissa(self):
        data = self._data
        return (data[1] << 16) | (data[2] << 8) | data[3]

    def __trunc__(self):
        sign = -1 if self.signbit else 1
        exponent_16 = self.exp16
        mantissa = self.int_mantissa

        num_nybbles_to_preserve = min(exponent_16, MAX_BITS_PRECISION_IBM_FLOAT // BITS_PER_NYBBLE)
        num_bits_to_clear = MAX_BITS_PRECISION_IBM_FLOAT - num_nybbles_to_preserve * BITS_PER_NYBBLE
        clear_mask = 2**num_bits_to_clear - 1
        preserve_mask = (2**MAX_BITS_PRECISION_IBM_FLOAT - 1) & ~clear_mask

        truncated_mantissa = mantissa & preserve_mask
        magnitude = int(truncated_mantissa * pow(EXPONENT_BASE, exponent_16)) >> MAX_BITS_PRECISION_IBM_FLOAT
        return sign * magnitude

    def normalize(self):
        """Normalize the floating point representation.

        Returns:
            A normalized IBMFloat equal in value to this object.

        Raises:
            FloatingPointError: If the number could not be normalized.
        """
        if self.is_zero():
            return IBM_FLOAT_ZERO

        exponent_16 = self.exp16
        mantissa = self.int_mantissa

        while mantissa < (1 << 20):
            new_exponent_16 = exponent_16 - 1
            if not (-64 <= new_exponent_16 < 64):
                raise FloatingPointError("Could not normalize {!r} without causing exponent overflow.".format(self))

            mantissa <<= 4
            exponent_16 = new_exponent_16

        exponent_16_biased = exponent_16 + EXPONENT_BIAS

        sign = int(self.signbit) << 7

        a = sign | exponent_16_biased
        b = (mantissa >> 16) & 0xff
        c = (mantissa >> 8) & 0xff
        d = mantissa & 0xff

        return IBMFloat.from_bytes((a, b, c, d))

    def try_normalize(self):
        """Normalize if possible.

        If it is not possible to normalize the representation,
        it remains unmodified.
        """
        try:
            return self.normalize()
        except FloatingPointError:
            return self

    def __floordiv__(self, rhs):
        return floor(float(self) / float(rhs))

    def __rfloordiv__(self, lhs):
        return floor(float(lhs) / float(self))

    def __truediv__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        q = float(self) / float(rhs)
        return IBMFloat.from_float_without_underflow(q) if isinstance(rhs, IBMFloat) else q

    def __rtruediv__(self, lhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        q = float(lhs) / float(self)
        return IBMFloat.from_float_without_underflow(q) if isinstance(lhs, float) else q

    def __pow__(self, exponent):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        p = pow(float(self), float(exponent))
        if isinstance(p, complex) and p.imag != 0:
            return p
        elif isinstance(exponent, IBMFloat):
            return IBMFloat.from_float_without_underflow(p)
        else:
            return p

    def __rpow__(self, base):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        p = pow(float(base), float(self))
        if isinstance(p, complex) and p.imag != 0:
            return p
        else:
            return p

    def __mod__(self, rhs):
        """a % b"""
        p = float(self) % float(rhs)
        return IBMFloat.from_float_without_underflow(p) if isinstance(rhs, IBMFloat) else p

    def __rmod__(self, lhs):
        """a % b"""
        return float(lhs) % float(self)

    def __mul__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        p = float(self) * float(rhs)
        return IBMFloat.from_float_without_underflow(p) if isinstance(rhs, IBMFloat) else p

    def __rmul__(self, lhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        p = float(lhs) * float(self)
        return IBMFloat.from_float(p) if isinstance(lhs, IBMFloat) else p

    def __add__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        p = float(self) + float(rhs)
        return IBMFloat.from_float_without_underflow(p) if isinstance(rhs, IBMFloat) else p

    def __radd__(self, lhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        return float(lhs) + float(self)

    def __sub__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        p = float(self) - float(rhs)
        return IBMFloat.from_float_without_underflow(p) if isinstance(rhs, IBMFloat) else p

    def __rsub__(self, lhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        return float(lhs) - float(self)

    def __lt__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        return float(self) < float(rhs)

    def __le__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        return float(self) <= float(rhs)

    def __gt__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        return float(self) > float(rhs)

    def __ge__(self, rhs):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        return float(self) >= float(rhs)

    def __ceil__(self):
        t = trunc(self)
        return t if self.signbit else t + 1

    def __floor__(self):
        t = trunc(self)
        return t - 1 if self.signbit else t

    def __round__(self, ndigits=None):
        # Python's 64-bit float has much more precision than this
        # 32-bit IBM float and is much faster, so delegate
        return IBMFloat.from_float_without_underflow(round(float(self), ndigits))

    def __int__(self):
        return trunc(self)


IBM_FLOAT_ZERO = IBMFloat.from_bytes(IBM_ZERO_BYTES)
