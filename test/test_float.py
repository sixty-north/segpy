import unittest

from segpy.portability import byte_string
from segpy.ibm_float import (ieee2ibm, ibm2ieee, MAX_IBM_FLOAT, SMALLEST_POSITIVE_NORMAL_IBM_FLOAT,
                             LARGEST_NEGATIVE_NORMAL_IBM_FLOAT, MIN_IBM_FLOAT)


class Ibm2Ieee(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(ibm2ieee(b'\0\0\0\0'), 0.0)

    def test_positive_half(self):
        self.assertEqual(ibm2ieee(byte_string((0b11000000, 0x80, 0x00, 0x00))), -0.5)

    def test_negative_half(self):
        self.assertEqual(ibm2ieee(byte_string((0b01000000, 0x80, 0x00, 0x00))), 0.5)

    def test_one(self):
        self.assertEqual(ibm2ieee(b'\x41\x10\x00\x00'), 1.0)

    def test_negative_118_625(self):
        # Example taken from Wikipedia http://en.wikipedia.org/wiki/IBM_Floating_Point_Architecture
        self.assertEqual(ibm2ieee(byte_string((0b11000010, 0b01110110, 0b10100000, 0b00000000))), -118.625)

    def test_largest_representable_number(self):
        self.assertEqual(ibm2ieee(byte_string((0b01111111, 0b11111111, 0b11111111, 0b11111111))), MAX_IBM_FLOAT)

    def test_smallest_positive_normalised_number(self):
        self.assertEqual(ibm2ieee(byte_string((0b00000000, 0b00010000, 0b00000000, 0b00000000))), SMALLEST_POSITIVE_NORMAL_IBM_FLOAT)

    def test_largest_negative_normalised_number(self):
        self.assertEqual(ibm2ieee(byte_string((0b10000000, 0b00010000, 0b00000000, 0b00000000))), LARGEST_NEGATIVE_NORMAL_IBM_FLOAT)

    def test_smallest_representable_number(self):
        self.assertEqual(ibm2ieee(byte_string((0b11111111, 0b11111111, 0b11111111, 0b11111111))), MIN_IBM_FLOAT)

    def test_error_1(self):
        self.assertEqual(ibm2ieee(byte_string((196, 74, 194, 143))), -19138.55859375)

    def test_error_2(self):
        self.assertEqual(ibm2ieee(byte_string((191, 128, 0, 0))), -0.03125)

    def test_subnormal(self):
        self.assertEqual(ibm2ieee(byte_string((0x00, 0x00, 0x00, 0x20))), 1.6472184286297693e-83)

    def test_subnormal_is_subnormal(self):
        self.assertTrue(0 < ibm2ieee(byte_string((0x00, 0x00, 0x00, 0x20))) < SMALLEST_POSITIVE_NORMAL_IBM_FLOAT)

    def test_subnormal_smallest_subnormal(self):
        self.assertEqual(ibm2ieee(byte_string((0x00, 0x00, 0x00, 0x01))), 5.147557589468029e-85)


class Ieee2Ibm(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(ieee2ibm(0.0), b'\0\0\0\0')

    def test_positive_half(self):
        self.assertEqual(ieee2ibm(-0.5), byte_string((0b11000000, 0x80, 0x00, 0x00)))

    def test_negative_half(self):
        self.assertEqual(ieee2ibm(0.5), byte_string((0b01000000, 0x80, 0x00, 0x00)))

    def test_one(self):
        self.assertEqual(ieee2ibm(1.0), b'\x41\x10\x00\x00')

    def test_negative_118_625(self):
        # Example taken from Wikipedia http://en.wikipedia.org/wiki/IBM_Floating_Point_Architecture
        self.assertEqual(ieee2ibm(-118.625), byte_string((0b11000010, 0b01110110, 0b10100000, 0b00000000)))

    def test_0_1(self):
        # Note, this is different from the Wikipedia example, because the Wikipedia example does
        # round to nearest, and our routine does round to zero
        self.assertEqual(ieee2ibm(0.1), byte_string((0b01000000, 0b00011001, 0b10011001, 0b10011001)))

    def test_subnormal(self):
        self.assertEqual(ieee2ibm(1.6472184286297693e-83), byte_string((0x00, 0x00, 0x00, 0x20)))

    def test_smallest_subnormal(self):
        self.assertEqual(ieee2ibm(5.147557589468029e-85), byte_string((0x00, 0x00, 0x00, 0x01)))

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
        ibm_start = byte_string((0b11000000, 0x80, 0x00, 0x00))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)

    def test_negative_half(self):
        ibm_start = byte_string((0b01000000, 0x80, 0x00, 0x00))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)

    def test_one(self):
        ibm_start = b'\x41\x10\x00\x00'
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)

    def test_subnormal(self):
        ibm_start = byte_string((0x00, 0x00, 0x00, 0x20))
        f = ibm2ieee(ibm_start)
        ibm_result = ieee2ibm(f)
        self.assertEqual(ibm_start, ibm_result)


if __name__ == '__main__':
    unittest.main()
