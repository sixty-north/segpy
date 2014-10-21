import unittest
from ibm_float import ieee2ibm, ibm2ieee


class Ibm2Ieee(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(ibm2ieee(b'\0\0\0\0'), 0.0)

    def test_positive_half(self):
        self.assertEqual(ibm2ieee((0b11000000, 0x80, 0x00, 0x00)), -0.5)

    def test_negative_half(self):
        self.assertEqual(ibm2ieee((0b01000000, 0x80, 0x00, 0x00)), 0.5)

    def test_one(self):
        self.assertEqual(ibm2ieee(b'\x41\x10\x00\x00'), 1.0)

    def test_negative_118_625(self):
        # Example taken from Wikipedia http://en.wikipedia.org/wiki/IBM_Floating_Point_Architecture
        self.assertEqual(ibm2ieee((0b11000010, 0b01110110, 0b10100000, 0b00000000)), -118.625)



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
        # Note, this is different from the Wikipedia example, but I'll stick my neck out and say
        # Wikipedia is wrong.
        self.assertEqual(ieee2ibm(0.1), bytes((0b01000000, 0b00011001, 0b10011001, 0b10011001)))


if __name__ == '__main__':
    unittest.main()
