import unittest

from hypothesis import given, assume, example
from hypothesis.specifiers import integers_in_range
from segpy.util import batched, complementary_intervals, flatten, intervals_are_contiguous, roundrobin
from test.strategies import spaced_ranges


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


class TestComplementaryIntervals(unittest.TestCase):

    @given(spaced_ranges(min_num_ranges=1, max_num_ranges=10,
                         min_interval=0, max_interval=10))
    def test_contiguous(self, intervals):
        complements = complementary_intervals(intervals)
        interleaved = list(roundrobin(complements, intervals))
        self.assertTrue(intervals_are_contiguous(interleaved))

    @given(spaced_ranges(min_num_ranges=1, max_num_ranges=10,
                         min_interval=0, max_interval=10),
           integers_in_range(0, 10))
    def test_contiguous_with_offset_start(self, intervals, start_offset):
        first_interval_start = intervals[0].start
        start_index = first_interval_start - start_offset
        complements = list(complementary_intervals(intervals, start=start_index))
        self.assertEqual(complements[0], range(start_index, first_interval_start))

    @given(spaced_ranges(min_num_ranges=1, max_num_ranges=10,
                         min_interval=0, max_interval=10),
           integers_in_range(0, 10))
    @example(intervals=[range(0, 0)], end_offset=1)
    def test_contiguous_with_offset_end(self, intervals, end_offset):
        last_interval_end = intervals[-1].stop
        end_index = last_interval_end + end_offset
        complements = list(complementary_intervals(intervals, stop=end_index))
        self.assertEqual(complements[-1], range(last_interval_end, end_index))

if __name__ == '__main__':
    unittest.main()