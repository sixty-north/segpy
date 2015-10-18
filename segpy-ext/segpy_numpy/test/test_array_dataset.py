import unittest

import numpy

from segpy_numpy.array_dataset import ArrayDataset3d

class MyTestCase(unittest.TestCase):
    def test_construction(self):
        a = numpy.ndarray(shape=(100, 100, 100), dtype=numpy.int32)

        d = ArrayDataset3d(
            binary_reel_header=None,
            textual_reel_header=None,
            extended_textual_header=None,
            trace_header_template=None,
            samples=a)


