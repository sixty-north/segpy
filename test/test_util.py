import unittest

from hypothesis import given, assume
from hypothesis.descriptors import integers_in_range
from segpy.util import batched


class TestBatched(unittest.TestCase):

    @given([int],
           integers_in_range(1, 1000))
    def test_batch_sizes_unpadded(self, items, batch_size):
        assume(batch_size > 0)
        batches = list(batched(items, batch_size))
        self.assertTrue(all(len(batch) == batch_size for batch in batches[:-1]))

    @given([int],
            integers_in_range(1, 1000))
    def test_final_batch_sizes(self, items, batch_size):
        assume(len(items) > 0)
        assume(batch_size > 0)
        batches = list(batched(items, batch_size))
        self.assertTrue(len(batches[-1]) <= batch_size)

    @given([int],
           integers_in_range(1, 1000),
           int)
    def test_batch_sizes_padded(self, items, batch_size, pad):
        assume(batch_size > 0)
        batches = list(batched(items, batch_size, padding=pad))
        self.assertTrue(all(len(batch) == batch_size for batch in batches))

    @given([int],
           integers_in_range(1, 1000),
           int)
    def test_pad_contents(self, items, batch_size, pad):
        assume(len(items) > 0)
        assume(0 < batch_size < 1000)
        num_left_over = len(items) % batch_size
        pad_length = batch_size - num_left_over if num_left_over != 0 else 0
        assume(pad_length != 0)
        batches = list(batched(items, batch_size, padding=pad))
        self.assertEqual(batches[-1][batch_size - pad_length:], [pad] * pad_length)

    def test_pad(self):
        batches = list(batched([0, 0], 3, 42))
        self.assertEqual(batches[-1], [0, 0, 42])

if __name__ == '__main__':
    unittest.main()