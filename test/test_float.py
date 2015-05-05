import math
from math import trunc
import unittest

from hypothesis import given, assume
from hypothesis.specifiers import integers_in_range, floats_in_range

from segpy.ibm_float import (ieee2ibm, ibm2ieee, MAX_IBM_FLOAT, SMALLEST_POSITIVE_NORMAL_IBM_FLOAT,
                             LARGEST_NEGATIVE_NORMAL_IBM_FLOAT, MIN_IBM_FLOAT, IBMFloat, EPSILON_IBM_FLOAT,
                             MAX_EXACT_INTEGER_IBM_FLOAT, MIN_EXACT_INTEGER_IBM_FLOAT, EXPONENT_BIAS)
from segpy.util import almost_equal


class Ibm2Ieee(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(ibm2ieee(b'\0\0\0\0'), 0.0)

    def test_positive_half(self):
        self.assertEqual(ibm2ieee(bytes((0b11000000, 0x80, 0x00, 0x00))), -0.5)

    def test_negative_half(self):
        self.assertEqual(ibm2ieee(bytes((0b01000000, 0x80, 0x00, 0x00))), 0.5)

    def test_one(self):
        self.assertEqual(ibm2ieee(b'\x41\x10\x00\x00'), 1.0)

    def test_negative_118_625(self):
        # Example taken from Wikipedia http://en.wikipedia.org/wiki/IBM_Floating_Point_Architecture
        self.assertEqual(ibm2ieee(bytes((0b11000010, 0b01110110, 0b10100000, 0b00000000))), -118.625)

    def test_largest_representable_number(self):
        self.assertEqual(ibm2ieee(bytes((0b01111111, 0b11111111, 0b11111111, 0b11111111))), MAX_IBM_FLOAT)

    def test_smallest_positive_normalised_number(self):
        self.assertEqual(ibm2ieee(bytes((0b00000000, 0b00010000, 0b00000000, 0b00000000))), SMALLEST_POSITIVE_NORMAL_IBM_FLOAT)

    def test_largest_negative_normalised_number(self):
        self.assertEqual(ibm2ieee(bytes((0b10000000, 0b00010000, 0b00000000, 0b00000000))), LARGEST_NEGATIVE_NORMAL_IBM_FLOAT)

    def test_smallest_representable_number(self):
        self.assertEqual(ibm2ieee(bytes((0b11111111, 0b11111111, 0b11111111, 0b11111111))), MIN_IBM_FLOAT)

    def test_error_1(self):
        self.assertEqual(ibm2ieee(bytes((196, 74, 194, 143))), -19138.55859375)

    def test_error_2(self):
        self.assertEqual(ibm2ieee(bytes((191, 128, 0, 0))), -0.03125)

    def test_subnormal(self):
        self.assertEqual(ibm2ieee(bytes((0x00, 0x00, 0x00, 0x20))), 1.6472184286297693e-83)

    def test_subnormal_is_subnormal(self):
        self.assertTrue(0 < ibm2ieee(bytes((0x00, 0x00, 0x00, 0x20))) < SMALLEST_POSITIVE_NORMAL_IBM_FLOAT)

    def test_subnormal_smallest_subnormal(self):
        self.assertEqual(ibm2ieee(bytes((0x00, 0x00, 0x00, 0x01))), 5.147557589468029e-85)


class Ieee2Ibm(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(ieee2ibm(0.0), b'\0\0\0\0')

    def test_positive_half(self):
        self.assertEqual(ieee2ibm(-0.5), bytes((0b11000000, 0x80, 0x00, 0x00)))

    def test_negative_half(self):
        self.assertEqual(ieee2ibm(0.5), bytes((0b01000000, 0x80, 0x00, 0x00)))

    def test_one(self):
        self.assertEqual(ieee2ibm(1.0), b'\x41\x10\x00\x00')

    def test_negative_118_625(self):
        # Example taken from Wikipedia http://en.wikipedia.org/wiki/IBM_Floating_Point_Architecture
        self.assertEqual(ieee2ibm(-118.625), bytes((0b11000010, 0b01110110, 0b10100000, 0b00000000)))

    def test_0_1(self):
        # Note, this is different from the Wikipedia example, because the Wikipedia example does
        # round to nearest, and our routine does round to zero
        self.assertEqual(ieee2ibm(0.1), bytes((0b01000000, 0b00011001, 0b10011001, 0b10011001)))

    def test_subnormal(self):
        self.assertEqual(ieee2ibm(1.6472184286297693e-83), bytes((0x00, 0x00, 0x00, 0x20)))

    def test_smallest_subnormal(self):
        self.assertEqual(ieee2ibm(5.147557589468029e-85), bytes((0x00, 0x00, 0x00, 0x01)))

    def test_too_small_subnormal(self):
        with self.assertRaises(FloatingPointError):
            ieee2ibm(1e-86)

    def test_nan(self):
        with self.assertRaises(ValueError):
            ieee2ibm(float('nan'))

    def test_inf(self):
        with self.assertRaises(ValueError):
            ieee2ibm(float('inf'))

    def test_too_large(self):
        with self.assertRaises(OverflowError):
            ieee2ibm(MAX_IBM_FLOAT * 10)

    def test_too_small(self):
        with self.assertRaises(OverflowError):
            ieee2ibm(MIN_IBM_FLOAT * 10)


class Ibm2IeeeRoundtrip(unittest.TestCase):

    def test_zero(self):
        ibm_start = b'\0\0\0\0'
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)

    def test_positive_half(self):
        ibm_start = bytes((0b11000000, 0x80, 0x00, 0x00))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)

    def test_negative_half(self):
        ibm_start = bytes((0b01000000, 0x80, 0x00, 0x00))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)

    def test_one(self):
        ibm_start = b'\x41\x10\x00\x00'
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)

    def test_subnormal(self):
        ibm_start = bytes((0x00, 0x00, 0x00, 0x20))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)


class TestIBMFloat(unittest.TestCase):

    def test_zero_from_float(self):
        zero = IBMFloat.from_float(0.0)
        self.assertTrue(zero.is_zero())

    def test_zero_from_bytes(self):
        zero = IBMFloat.from_bytes(b'\x00\x00\x00\x00')
        self.assertTrue(zero.is_zero())

    def test_subnormal(self):
        ibm = IBMFloat.from_float(1.6472184286297693e-83)
        self.assertTrue(ibm.is_subnormal())

    def test_smallest_subnormal(self):
        ibm = IBMFloat.from_float(5.147557589468029e-85)
        self.assertEqual(bytes(ibm), bytes((0x00, 0x00, 0x00, 0x01)))

    def test_too_small_subnormal(self):
        with self.assertRaises(FloatingPointError):
            IBMFloat.from_float(1e-86)

    def test_nan(self):
        with self.assertRaises(ValueError):
            IBMFloat.from_float(float('nan'))

    def test_inf(self):
        with self.assertRaises(ValueError):
            IBMFloat.from_float(float('inf'))

    def test_too_large(self):
        with self.assertRaises(OverflowError):
            IBMFloat.from_float(MAX_IBM_FLOAT * 10)

    def test_too_small(self):
        with self.assertRaises(OverflowError):
            IBMFloat.from_float(MIN_IBM_FLOAT * 10)

    @given(floats_in_range(MIN_IBM_FLOAT, MAX_IBM_FLOAT))
    def test_bool(self, f):
        self.assertEqual(bool(IBMFloat.from_float(f)), bool(f))

    @given(integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255))
    def test_bytes_roundtrip(self, a, b, c, d):
        b = bytes((a, b, c, d))
        ibm = IBMFloat.from_bytes(b)
        self.assertEqual(bytes(ibm), b)

    @given(floats_in_range(MIN_IBM_FLOAT, MAX_IBM_FLOAT))
    def test_floats_roundtrip(self, f):
        ibm = IBMFloat.from_float(f)
        self.assertTrue(almost_equal(f, float(ibm), epsilon=EPSILON_IBM_FLOAT))

    @given(integers_in_range(0, MAX_EXACT_INTEGER_IBM_FLOAT - 1),
           floats_in_range(0.0, 1.0))
    def test_trunc_above_zero(self, i, f):
        assume(f != 1.0)
        ieee = i + f
        ibm = IBMFloat.from_float(ieee)
        self.assertEqual(trunc(ibm), i)

    @given(integers_in_range(MIN_EXACT_INTEGER_IBM_FLOAT + 1, 0),
           floats_in_range(0.0, 1.0))
    def test_trunc_below_zero(self, i, f):
        assume(f != 1.0)
        ieee = i - f
        ibm = IBMFloat.from_float(ieee)
        self.assertEqual(trunc(ibm), i)

    @given(integers_in_range(MIN_EXACT_INTEGER_IBM_FLOAT, MAX_EXACT_INTEGER_IBM_FLOAT - 1),
           floats_in_range(0.0, 1.0))
    def test_ceil(self, i, f):
        assume(f != 1.0)
        ieee = i + f
        ibm = IBMFloat.from_float(ieee)
        self.assertEqual(math.ceil(ibm), i + 1)

    @given(integers_in_range(MIN_EXACT_INTEGER_IBM_FLOAT, MAX_EXACT_INTEGER_IBM_FLOAT - 1),
           floats_in_range(0.0, 1.0))
    def test_floor(self, i, f):
        assume(f != 1.0)
        ieee = i + f
        ibm = IBMFloat.from_float(ieee)
        self.assertEqual(math.floor(ibm), i)

    def test_normalise_subnormal_expect_failure(self):
        # This float has an base-16 exponent of -64 (the minimum) and cannot be normalised
        ibm = IBMFloat.from_float(1.6472184286297693e-83)
        assert ibm.is_subnormal()
        with self.assertRaises(FloatingPointError):
            ibm.normalize()

    def test_normalise_subnormal1(self):
        ibm = IBMFloat.from_bytes((0b01000000, 0b00000000, 0b11111111, 0b00000000))
        assert ibm.is_subnormal()
        normalized = ibm.normalize()
        self.assertFalse(normalized.is_subnormal())

    def test_normalise_subnormal2(self):
        ibm = IBMFloat.from_bytes((64, 1, 0, 0))
        assert ibm.is_subnormal()
        normalized = ibm.normalize()
        self.assertFalse(normalized.is_subnormal())

    @given(integers_in_range(128, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(4, 23))
    def test_normalise_subnormal(self, b, c, d, shift):
        mantissa = (b << 16) | (c << 8) | d
        assume(mantissa != 0)
        mantissa >>= shift
        assert mantissa != 0

        sa = EXPONENT_BIAS
        sb = (mantissa >> 16) & 0xff
        sc = (mantissa >> 8) & 0xff
        sd = mantissa & 0xff

        ibm = IBMFloat.from_bytes((sa, sb, sc, sd))
        assert ibm.is_subnormal()
        normalized = ibm.normalize()
        self.assertFalse(normalized.is_subnormal())

    @given(integers_in_range(128, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(4, 23))
    def test_zero_subnormal(self, b, c, d, shift):
        mantissa = (b << 16) | (c << 8) | d
        assume(mantissa != 0)
        mantissa >>= shift
        assert mantissa != 0

        sa = EXPONENT_BIAS
        sb = (mantissa >> 16) & 0xff
        sc = (mantissa >> 8) & 0xff
        sd = mantissa & 0xff

        ibm = IBMFloat.from_bytes((sa, sb, sc, sd))
        assert ibm.is_subnormal()
        z = ibm.zero_subnormal()
        self.assertTrue(z.is_zero())

    @given(integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255))
    def test_abs(self, a, b, c, d):
        ibm = IBMFloat.from_bytes((a, b, c, d))
        abs_ibm = abs(ibm)
        self.assertGreaterEqual(abs_ibm.signbit, 0)

    @given(integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255),
           integers_in_range(0, 255))
    def test_negate_non_zero(self, a, b, c, d):
        ibm = IBMFloat.from_bytes((a, b, c, d))
        assume(not ibm.is_zero())
        negated = -ibm
        self.assertNotEqual(ibm.signbit, negated.signbit)

    def test_negate_zero(self):
        zero = IBMFloat.from_float(0.0)
        negated = -zero
        self.assertTrue(negated.is_zero())

    @given(floats_in_range(MIN_IBM_FLOAT, MAX_IBM_FLOAT))
    def test_signbit(self, f):
        ltz = f < 0
        ibm = IBMFloat.from_float(f)
        self.assertEqual(ltz, ibm.signbit)

    @given(floats_in_range(-1.0, +1.0),
           integers_in_range(-256, 255))
    def test_ldexp_frexp(self, fraction, exponent):
        try:
            ibm = IBMFloat.ldexp(fraction, exponent)
        except OverflowError:
            assume(False)
        else:
            f, e = ibm.frexp()
            self.assertTrue(almost_equal(fraction * 2**exponent, f * 2**e, epsilon=EPSILON_IBM_FLOAT))

    @given(floats_in_range(MIN_IBM_FLOAT, MAX_IBM_FLOAT),
           floats_in_range(0.0, 1.0))
    def test_add(self, f, p):
        a = f * p
        b = f - a

        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ibm_c = ibm_a + ibm_b

        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        ieee_c = ieee_a + ieee_b

        self.assertTrue(almost_equal(ieee_c, ibm_c, epsilon=EPSILON_IBM_FLOAT * 4))

    @given(floats_in_range(0, MAX_IBM_FLOAT),
           floats_in_range(0, MAX_IBM_FLOAT))
    def test_sub(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ibm_c = ibm_a - ibm_b

        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        ieee_c = ieee_a - ieee_b

        self.assertTrue(almost_equal(ieee_c, ibm_c, epsilon=EPSILON_IBM_FLOAT))



if __name__ == '__main__':
    unittest.main()
