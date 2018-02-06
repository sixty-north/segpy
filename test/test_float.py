import math
from fractions import Fraction
from math import trunc
import pytest

from hypothesis import given, assume, settings, HealthCheck, Phase
from hypothesis.errors import UnsatisfiedAssumption
from hypothesis.strategies import integers, floats, one_of, just, composite
from pytest import raises

from segpy.ibm_float import (ieee2ibm, ibm2ieee, MAX_IBM_FLOAT, SMALLEST_POSITIVE_NORMAL_IBM_FLOAT,
                             LARGEST_NEGATIVE_NORMAL_IBM_FLOAT, MIN_IBM_FLOAT, IBMFloat, EPSILON_IBM_FLOAT,
                             MAX_EXACT_INTEGER_IBM_FLOAT, MIN_EXACT_INTEGER_IBM_FLOAT, EXPONENT_BIAS, _L21)

from segpy.util import almost_equal
from test.predicates import check_balanced


@composite
def ibm_compatible_negative_floats(draw):
    return draw(floats(MIN_IBM_FLOAT, LARGEST_NEGATIVE_NORMAL_IBM_FLOAT))


@composite
def ibm_compatible_positive_floats(draw):
    return draw(floats(SMALLEST_POSITIVE_NORMAL_IBM_FLOAT, MAX_IBM_FLOAT))


@composite
def ibm_compatible_non_negative_floats(draw):
    return draw(one_of(
        just(0.0),
        floats(SMALLEST_POSITIVE_NORMAL_IBM_FLOAT, MAX_IBM_FLOAT)))


@composite
def ibm_compatible_non_positive_floats(draw):
    return draw(one_of(
        just(0.0),
        floats(MIN_IBM_FLOAT, LARGEST_NEGATIVE_NORMAL_IBM_FLOAT)))


@composite
def ibm_compatible_floats(draw, min_value=None, max_value=None):
    if min_value is None:
        min_value = MIN_IBM_FLOAT
        
    if max_value is None:
        max_value = MAX_IBM_FLOAT
    
    truncated_min_f = max(min_value, MIN_IBM_FLOAT)
    truncated_max_f = min(max_value, MAX_IBM_FLOAT)

    strategies = []
    if truncated_min_f <= LARGEST_NEGATIVE_NORMAL_IBM_FLOAT <= truncated_max_f:
        strategies.append(floats(truncated_min_f, LARGEST_NEGATIVE_NORMAL_IBM_FLOAT))

    if truncated_min_f <= SMALLEST_POSITIVE_NORMAL_IBM_FLOAT <= truncated_max_f:
        strategies.append(floats(SMALLEST_POSITIVE_NORMAL_IBM_FLOAT, truncated_max_f))

    if truncated_min_f <= 0 <= truncated_max_f:
        strategies.append(just(0.0))

    if len(strategies) == 0:
        strategies.append(floats(truncated_min_f, truncated_max_f))

    ibm = draw(one_of(*strategies))
    return ibm


class TestIbm2Ieee:

    @given(integers(0, 255))
    def test_zero(self, a):
        assert ibm2ieee(bytes([a, 0, 0, 0])) == 0.0

    def test_positive_half(self):
        assert ibm2ieee(bytes((0b11000000, 0x80, 0x00, 0x00))) == -0.5

    def test_negative_half(self):
        assert ibm2ieee(bytes((0b01000000, 0x80, 0x00, 0x00))) == 0.5

    def test_one(self):
        assert ibm2ieee(b'\x41\x10\x00\x00') == 1.0

    def test_negative_118_625(self):
        # Example taken from Wikipedia http://en.wikipedia.org/wiki/IBM_Floating_Point_Architecture
        assert ibm2ieee(bytes((0b11000010, 0b01110110, 0b10100000, 0b00000000))) == -118.625

    def test_largest_representable_number(self):
        assert ibm2ieee(bytes((0b01111111, 0b11111111, 0b11111111, 0b11111111))) == MAX_IBM_FLOAT

    def test_smallest_positive_normalised_number(self):
        assert ibm2ieee(bytes((0b00000000, 0b00010000, 0b00000000, 0b00000000))) == SMALLEST_POSITIVE_NORMAL_IBM_FLOAT

    def test_largest_negative_normalised_number(self):
        assert ibm2ieee(bytes((0b10000000, 0b00010000, 0b00000000, 0b00000000))) == LARGEST_NEGATIVE_NORMAL_IBM_FLOAT

    def test_smallest_representable_number(self):
        assert ibm2ieee(bytes((0b11111111, 0b11111111, 0b11111111, 0b11111111))) == MIN_IBM_FLOAT

    def test_error_1(self):
        assert ibm2ieee(bytes((196, 74, 194, 143))) == -19138.55859375

    def test_error_2(self):
        assert ibm2ieee(bytes((191, 128, 0, 0))) == -0.03125

    def test_subnormal(self):
        assert ibm2ieee(bytes((0x00, 0x00, 0x00, 0x20))) == 1.6472184286297693e-83

    def test_subnormal_is_subnormal(self):
        assert 0 < ibm2ieee(bytes((0x00, 0x00, 0x00, 0x20))) < SMALLEST_POSITIVE_NORMAL_IBM_FLOAT

    def test_subnormal_smallest_subnormal(self):
        assert ibm2ieee(bytes((0x00, 0x00, 0x00, 0x01))) == 5.147557589468029e-85


class TestIeee2Ibm:

    def test_zero(self):
        assert ieee2ibm(0.0) == b'\0\0\0\0'

    def test_positive_half(self):
        assert ieee2ibm(-0.5) == bytes((0b11000000, 0x80, 0x00, 0x00))

    def test_negative_half(self):
        assert ieee2ibm(0.5) == bytes((0b01000000, 0x80, 0x00, 0x00))

    def test_one(self):
        assert ieee2ibm(1.0) == b'\x41\x10\x00\x00'

    def test_negative_118_625(self):
        # Example taken from Wikipedia http://en.wikipedia.org/wiki/IBM_Floating_Point_Architecture
        assert ieee2ibm(-118.625) == bytes((0b11000010, 0b01110110, 0b10100000, 0b00000000))

    def test_0_1(self):
        # Note, this is different from the Wikipedia example, because the Wikipedia example does
        # round to nearest, and our routine does round to zero
        assert ieee2ibm(0.1) == bytes((0b01000000, 0b00011001, 0b10011001, 0b10011001))

    def test_subnormal(self):
        assert ieee2ibm(1.6472184286297693e-83) == bytes((0x00, 0x00, 0x00, 0x20))

    def test_smallest_subnormal(self):
        assert ieee2ibm(5.147557589468029e-85) == bytes((0x00, 0x00, 0x00, 0x01))

    def test_too_small_subnormal(self):
        with pytest.raises(FloatingPointError):
            ieee2ibm(1e-86)

    def test_nan(self):
        with pytest.raises(ValueError):
            ieee2ibm(float('nan'))

    def test_inf(self):
        with pytest.raises(ValueError):
            ieee2ibm(float('inf'))

    def test_too_large(self):
        with pytest.raises(OverflowError):
            ieee2ibm(MAX_IBM_FLOAT * 10)

    def test_too_small(self):
        with pytest.raises(OverflowError):
            ieee2ibm(MIN_IBM_FLOAT * 10)


class TestIbm2IeeeRoundtrip:

    def test_zero(self):
        ibm_start = b'\0\0\0\0'
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        assert ibm_start == ibm_result

    def test_positive_half(self):
        ibm_start = bytes((0b11000000, 0x80, 0x00, 0x00))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        assert ibm_start == ibm_result

    def test_negative_half(self):
        ibm_start = bytes((0b01000000, 0x80, 0x00, 0x00))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        assert ibm_start == ibm_result

    def test_one(self):
        ibm_start = b'\x41\x10\x00\x00'
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        assert ibm_start == ibm_result

    def test_subnormal(self):
        ibm_start = bytes((0x00, 0x00, 0x00, 0x20))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        assert ibm_start == ibm_result


class TestIBMFloat:

    def test_zero_from_float(self):
        zero = IBMFloat.from_float(0.0)
        assert zero.is_zero()

    @given(ibm_compatible_floats())
    def test_zero_from_ibm_float(self, f):
        ibm_a = IBMFloat.from_float(f)
        ibm_b = IBMFloat.from_float(ibm_a)
        assert ibm_a == ibm_b

    def test_zero_from_real_fraction(self):
        zero = IBMFloat.from_real(Fraction(0, 1))
        assert zero.is_zero()

    def test_zero_from_bytes(self):
        zero = IBMFloat.from_bytes(b'\x00\x00\x00\x00')
        assert zero.is_zero()

    def test_incorrect_number_of_bytes_raises_value_error(self):
        with raises(ValueError):
            IBMFloat.from_bytes(b'\x00\x00\x00')

    def test_subnormal(self):
        ibm = IBMFloat.from_float(1.6472184286297693e-83)
        assert ibm.is_subnormal()

    def test_smallest_subnormal(self):
        ibm = IBMFloat.from_float(5.147557589468029e-85)
        assert bytes(ibm) == bytes((0x00, 0x00, 0x00, 0x01))

    def test_too_small_subnormal(self):
        with pytest.raises(FloatingPointError):
            IBMFloat.from_float(1e-86)

    def test_nan(self):
        with pytest.raises(ValueError):
            IBMFloat.from_float(float('nan'))

    def test_inf(self):
        with pytest.raises(ValueError):
            IBMFloat.from_float(float('inf'))

    def test_too_large(self):
        with pytest.raises(OverflowError):
            IBMFloat.from_float(MAX_IBM_FLOAT * 10)

    def test_too_small(self):
        with pytest.raises(OverflowError):
            IBMFloat.from_float(MIN_IBM_FLOAT * 10)

    @given(ibm_compatible_floats())
    def test_bool(self, f):
        assert bool(IBMFloat.from_float(f)) == bool(f)

    @given(integers(0, 255),
           integers(0, 255),
           integers(0, 255),
           integers(0, 255))
    def test_bytes_roundtrip(self, a, b, c, d):
        b = bytes((a, b, c, d))
        ibm = IBMFloat.from_bytes(b)
        assert bytes(ibm) == b

    @given(ibm_compatible_floats())
    def test_floats_roundtrip(self, f):
        ibm = IBMFloat.from_float(f)
        assert almost_equal(f, float(ibm), epsilon=EPSILON_IBM_FLOAT)

    @given(integers(0, MAX_EXACT_INTEGER_IBM_FLOAT - 1),
           ibm_compatible_floats(0.0, 1.0))
    def test_trunc_above_zero(self, i, f):
        assume(f != 1.0)
        ieee = i + f
        ibm = IBMFloat.from_float(ieee)
        assert trunc(ibm) == i

    @given(integers(MIN_EXACT_INTEGER_IBM_FLOAT + 1, 0),
           ibm_compatible_floats(0.0, 1.0))
    def test_trunc_below_zero(self, i, f):
        assume(f != 1.0)
        ieee = i - f
        ibm = IBMFloat.from_float(ieee)
        assert trunc(ibm) == i

    @given(integers(MIN_EXACT_INTEGER_IBM_FLOAT, MAX_EXACT_INTEGER_IBM_FLOAT - 1),
           ibm_compatible_floats(EPSILON_IBM_FLOAT, 1 - EPSILON_IBM_FLOAT))
    def test_ceil(self, i, f):
        ieee = i + f
        ibm = IBMFloat.from_float(ieee)
        assert math.ceil(ibm) == i + 1

    @given(integers(MIN_EXACT_INTEGER_IBM_FLOAT, MAX_EXACT_INTEGER_IBM_FLOAT - 1),
           ibm_compatible_floats(EPSILON_IBM_FLOAT, 1 - EPSILON_IBM_FLOAT))
    def test_floor(self, i, f):
        ieee = i + f
        ibm = IBMFloat.from_float(ieee)
        assert math.floor(ibm) == i

    def test_normalize_zero(self):
        zero = IBMFloat(bytes((0x32, 0x00, 0x00, 0x00)))
        assert zero.is_subnormal()
        nzero = zero.normalize()
        assert bytes(nzero) == bytes((0x00, 0x00, 0x00, 0x00))

    def test_normalise_subnormal_expect_failure(self):
        # This float has an base-16 exponent of -64 (the minimum) and cannot be normalised
        ibm = IBMFloat.from_float(1.6472184286297693e-83)
        assert ibm.is_subnormal()
        with pytest.raises(FloatingPointError):
            ibm.normalize()

    def test_normalise_subnormal1(self):
        ibm = IBMFloat.from_bytes((0b01000000, 0b00000000, 0b11111111, 0b00000000))
        assert ibm.is_subnormal()
        normalized = ibm.normalize()
        assert not normalized.is_subnormal()

    def test_normalise_subnormal2(self):
        ibm = IBMFloat.from_bytes((64, 1, 0, 0))
        assert ibm.is_subnormal()
        normalized = ibm.normalize()
        assert not normalized.is_subnormal()

    @given(integers(128, 255),
           integers(0, 255),
           integers(0, 255),
           integers(4, 23))
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
        assert not normalized.is_subnormal()

    @given(integers(128, 255),
           integers(0, 255),
           integers(0, 255),
           integers(4, 23))
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
        assert z.is_zero()

    @given(integers(0, 255),
           integers(0, 255),
           integers(0, 255),
           integers(0, 255))
    def test_abs(self, a, b, c, d):
        ibm = IBMFloat.from_bytes((a, b, c, d))
        abs_ibm = abs(ibm)
        assert abs_ibm.signbit >= 0

    @given(integers(0, 255),
           integers(0, 255),
           integers(0, 255),
           integers(0, 255))
    def test_negate_non_zero(self, a, b, c, d):
        ibm = IBMFloat.from_bytes((a, b, c, d))
        assume(not ibm.is_zero())
        negated = -ibm
        assert ibm.signbit != negated.signbit

    def test_negate_zero(self):
        zero = IBMFloat.from_float(0.0)
        negated = -zero
        assert negated.is_zero()

    @given(ibm_compatible_floats())
    def test_signbit(self, f):
        ltz = f < 0
        ibm = IBMFloat.from_float(f)
        assert ltz == ibm.signbit

    @given(ibm_compatible_floats(-1.0, +1.0),
           integers(-256, 255))
    def test_ldexp_frexp(self, fraction, exponent):
        try:
            ibm = IBMFloat.ldexp(fraction, exponent)
        except (OverflowError, FloatingPointError):
            raise UnsatisfiedAssumption
        else:
            f, e = ibm.frexp()
            assert almost_equal(fraction * 2**exponent, f * 2**e, epsilon=EPSILON_IBM_FLOAT)

    @given(fraction=one_of(
                ibm_compatible_floats(max_value=-1.0),
                ibm_compatible_floats(min_value=+1.0)),
           exponent=integers(-256, 255))
    def test_ldexp_fraction_out_of_range_raises_value_error(self, fraction, exponent):
        assume(fraction != -1.0 and fraction != +1.0)
        with raises(ValueError):
            IBMFloat.ldexp(fraction, exponent)

    @given(fraction=ibm_compatible_floats(-1.0, +1.0),
           exponent=one_of(
               integers(max_value=-257),
               integers(min_value=256)))
    def test_ldexp_exponent_out_of_range_raises_value_error(self, fraction, exponent):
        with raises(ValueError):
            IBMFloat.ldexp(fraction, exponent)

    @given(f=ibm_compatible_floats())
    def test_str(self, f):
        ibm = IBMFloat.from_float(f)
        g = float(ibm)
        assert str(g) == str(ibm)

    @given(a=integers(min_value=1, max_value=255))
    def test_is_subnormal(self, a):
        buffer = bytes([a, 0, 0, 0])
        ibm = IBMFloat(buffer)
        assert ibm.is_subnormal()

    @given(f=ibm_compatible_floats())
    def test_pos(self, f):
        ibm = IBMFloat.from_float(f)
        assert ibm == +ibm

    def test_zero_equal(self):
        buffer = bytes([0, 0, 0, 0])
        p = IBMFloat(buffer)
        q = IBMFloat(buffer)
        assert p == q

    @given(a=integers(min_value=1, max_value=255))
    def test_subnormal_equal(self, a):
        buffer = bytes([a, 0, 0, 0])
        p = IBMFloat(buffer)
        q = IBMFloat(buffer)
        assert p == q

    def test_positive_half_equal(self):
        buffer = bytes((0b11000000, 0x80, 0x00, 0x00))
        p = IBMFloat(buffer)
        q = IBMFloat(buffer)
        assert p == q

    def test_negative_half_equal(self):
        buffer = bytes((0b01000000, 0x80, 0x00, 0x00))
        p = IBMFloat(buffer)
        q = IBMFloat(buffer)
        assert p == q

    def test_one_equal(self):
        buffer = b'\x41\x10\x00\x00'
        p = IBMFloat(buffer)
        q = IBMFloat(buffer)
        assert p == q

    def test_smallest_subnormal_is_equal(self):
        buffer = bytes((0x00, 0x00, 0x00, 0x01))
        p = IBMFloat(buffer)
        q = IBMFloat(buffer)
        assert p == q

    def test_small_subnormals_are_not_equal(self):
        p = IBMFloat(bytes((0x00, 0x00, 0x00, 0x01)))
        q = IBMFloat(bytes((0x00, 0x00, 0x00, 0x02)))
        assert p != q

    def test_subnormals_lhs_are_not_equal_to_one(self):
        p = IBMFloat(bytes((0x00, 0x00, 0x00, 0x01)))
        q = IBMFloat.from_float(1.0)
        assert p != q

    def test_subnormals_rhs_are_not_equal_to_one(self):
        p = IBMFloat.from_float(1.0)
        q = IBMFloat(bytes((0x00, 0x00, 0x00, 0x01)))
        assert p != q

    def test_equality_different_signs(self):
        p = IBMFloat.from_float(+1.0)
        q = IBMFloat.from_float(-1.0)
        assert p != q

    def test_equality_with_finite_float_positive(self):
        p = IBMFloat.from_float(+1.5)
        q = +1.5
        assert p == q

    def test_equality_with_finite_float_negative(self):
        p = IBMFloat.from_float(+1.5)
        q = +1.6
        assert p != q

    def test_equality_with_infinite_float_negative(self):
        p = IBMFloat.from_float(+1.5)
        q = float("+inf")
        assert p != q

    def test_equality_with_nan_negative(self):
        p = IBMFloat.from_float(+1.5)
        q = float("nan")
        assert p != q

    def test_equality_with_int_positive(self):
        p = IBMFloat.from_float(1234.0)
        q = 1234
        assert p == q

    def test_equality_with_int_negative(self):
        p = IBMFloat.from_float(1234.0)
        q = 4321
        assert p != q

    def test_equality_with_non_comparable_type_is_false(self):
        p = IBMFloat.from_float(1234.0)
        q = None
        assert p != q

    def test_equality_normalizable_subnormal(self):
        p = IBMFloat(bytes((0x10, 0x04, 0x00, 0x00)))
        assert p.is_subnormal()
        q = IBMFloat(bytes((0x10, 0x05, 0x00, 0x00)))
        assert q.is_subnormal()
        assert p != q

    @given(ibm_compatible_floats(),
           ibm_compatible_floats(0.0, 1.0))
    def test_add(self, f, p):
        a = f * p
        b = f - a

        try:
            ibm_a = IBMFloat.from_float(a)
            ibm_b = IBMFloat.from_float(b)
            ibm_c = ibm_a + ibm_b
        except FloatingPointError:
            raise UnsatisfiedAssumption

        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        ieee_c = ieee_a + ieee_b

        assert almost_equal(ieee_c, ibm_c, epsilon=EPSILON_IBM_FLOAT * 4)

    @given(ibm_compatible_non_negative_floats(),
           ibm_compatible_non_negative_floats())
    def test_sub(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        try:
            ibm_c = ibm_a - ibm_b
        except FloatingPointError:
            raise UnsatisfiedAssumption

        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        ieee_c = ieee_a - ieee_b

        assert almost_equal(ieee_c, ibm_c, epsilon=EPSILON_IBM_FLOAT)

    @given(ibm_compatible_floats())
    def test_repr(self, f):
        ibm = IBMFloat.from_float(f)
        r = repr(ibm)
        assert check_balanced(r)

    @given(ibm_compatible_floats(min_value=-2**21, max_value=+2**21))
    def test_conversion_to_int(self, f):
        ibm = IBMFloat.from_float(f)
        assert int(ibm) == int(f)

    @given(ibm_compatible_floats(min_value=-2**21, max_value=+2**21))
    def test_round(self, f):
        ibm = IBMFloat.from_float(f)
        g = float(ibm)
        assert round(ibm) == round(g)

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_floordiv_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        assume(not ibm_b.is_zero())
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        assert ibm_a // ibm_b == ieee_a // ieee_b

    @given(a=ibm_compatible_floats())
    def test_floordiv_ibm_division_by_zero_raises_zero_division_error(self, a):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(0.0)
        with raises(ZeroDivisionError):
            _ = ibm_a // ibm_b

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_rfloordiv_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        assume(not ibm_b.is_zero())
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        assert ieee_a // ibm_b == ieee_a // ieee_b

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_rfloordiv_ibm_division_by_zero_raises_zero_division_error(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(0.0)
        ieee_a = float(ibm_a)
        with raises(ZeroDivisionError):
            _ = ieee_a // ibm_b

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_truediv_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        assume(not ibm_b.is_zero())
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ibm_c = ibm_a / ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c = ieee_a / ieee_b
        assert almost_equal(ibm_c, ieee_c, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats())
    def test_truediv_ibm_by_zero_raises_zero_division_error(self, a):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(0.0)
        with raises(ZeroDivisionError):
            _ = ibm_a / ibm_b

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_rtruediv_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        assume(not ibm_b.is_zero())
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ieee_c1 = ieee_a / ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c2 = ieee_a / ieee_b
        assert almost_equal(ieee_c1, ieee_c2, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats())
    def test_rtruediv_ibm_division_by_zero_raises_zero_division_error(self, a):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(0.0)
        ieee_a = float(ibm_a)
        with raises(ZeroDivisionError):
            _ = ieee_a / ibm_b

    @given(a=ibm_compatible_floats(min_value=0.0),
           b=ibm_compatible_floats())
    def test_pow_ibm(self, a, b):
        assume(a != 0.0)
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ibm_c = ibm_a ** ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c = ieee_a ** ieee_b
        assert almost_equal(ibm_c, ieee_c, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats(max_value=0.0),
           b=ibm_compatible_floats(min_value=0.0, max_value=1.0))
    @settings(
        max_examples=5,
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate),
    )
    def test_pow_ibm_complex_result(self, a, b):
        assume(a != 0.0)
        assume(b != 0.0 and b != 1.0)
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ibm_c = ibm_a ** ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c = ieee_a ** ieee_b
        assert almost_equal(ibm_c, ieee_c, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats(min_value=0.0),
           b=ibm_compatible_floats())
    def test_pow_ibm_ieee_result(self, a, b):
        assume(a != 0.0)
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ieee_c1 = ibm_a ** ieee_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c2 = ieee_a ** ieee_b
        assert almost_equal(ieee_c1, ieee_c2, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats(min_value=0.0),
           b=ibm_compatible_floats())
    def test_rpow_ibm_ieee_results(self, a, b):
        assume(a != 0.0)
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ieee_c1 = ieee_a ** ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c2 = ieee_a ** ieee_b
        assert almost_equal(ieee_c1, ieee_c2, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats(max_value=0.0),
           b=ibm_compatible_floats(min_value=0.0, max_value=1.0))
    @settings(
        max_examples=5,
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate),
    )
    def test_rpow_ibm_complex_result(self, a, b):
        assume(a != 0.0)
        assume(b != 0.0 and b != 1.0)
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ieee_c1 = ieee_a ** ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c2 = ieee_a ** ieee_b
        assert almost_equal(ieee_c1, ieee_c2, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_mod_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        assume(not ibm_b.is_zero())
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ibm_c = ibm_a % ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c = ieee_a % ieee_b
        assert almost_equal(ibm_c, ieee_c, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats())
    def test_mod_ibm_division_by_zero_raises_zero_division_error(self, a):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(0.0)
        with raises(ZeroDivisionError):
            _ = ibm_a % ibm_b

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_rmod_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        assume(not ibm_b.is_zero())
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ieee_c1 = ieee_a % ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c2 = ieee_a % ieee_b
        assert almost_equal(ieee_c1, ieee_c2, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats())
    def test_rmod_ibm_division_by_zero_raises_zero_division_error(self, a):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(0.0)
        ieee_a = float(ibm_a)
        with raises(ZeroDivisionError):
            _ = ieee_a % ibm_b

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_radd_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ieee_c1 = ieee_a + ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c2 = ieee_a + ieee_b
        assert almost_equal(ieee_c1, ieee_c2, epsilon=EPSILON_IBM_FLOAT)

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_lt_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        assert (ibm_a < ibm_b) == (ieee_a < ieee_b)

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_gt_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        assert (ibm_a > ibm_b) == (ieee_a > ieee_b)

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_ge_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        assert (ibm_a >= ibm_b) == (ieee_a >= ieee_b)

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_le_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        assert (ibm_a <= ibm_b) == (ieee_a <= ieee_b)

    @given(a=ibm_compatible_floats(),
           b=ibm_compatible_floats())
    def test_mul_ibm(self, a, b):
        ibm_a = IBMFloat.from_float(a)
        ibm_b = IBMFloat.from_float(b)
        ieee_a = float(ibm_a)
        ieee_b = float(ibm_b)
        try:
            ibm_c = ibm_a * ibm_b
        except OverflowError:
            raise UnsatisfiedAssumption
        ieee_c = ieee_a * ieee_b
        assert almost_equal(ibm_c, ieee_c, epsilon=EPSILON_IBM_FLOAT)