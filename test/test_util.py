from hypothesis import given, assume, example
from hypothesis.strategies import integers, lists, booleans
from pytest import raises

from segpy.util import batched, complementary_intervals, flatten, intervals_are_contiguous, roundrobin, reversed_range, \
    make_sorted_distinct_sequence, SortSense, sgn, is_sorted
from test.strategies import spaced_ranges, ranges, sequences


class TestBatched:

    @given(lists(integers()),
           integers(1, 1000))
    def test_batch_sizes_unpadded(self, items, batch_size):
        assume(batch_size > 0)
        batches = list(batched(items, batch_size))
        assert all(len(batch) == batch_size for batch in batches[:-1])

    @given(lists(integers()),
           integers(1, 1000))
    def test_final_batch_sizes(self, items, batch_size):
        assume(len(items) > 0)
        assume(batch_size > 0)
        batches = list(batched(items, batch_size))
        assert len(batches[-1]) <= batch_size

    @given(lists(integers()),
           integers(1, 1000),
           integers())
    def test_batch_sizes_padded(self, items, batch_size, pad):
        assume(batch_size > 0)
        batches = list(batched(items, batch_size, padding=pad))
        assert all(len(batch) == batch_size for batch in batches)

    @given(lists(integers()),
           integers(1, 1000),
           integers())
    def test_pad_contents(self, items, batch_size, pad):
        assume(len(items) > 0)
        assume(0 < batch_size < 1000)
        num_left_over = len(items) % batch_size
        pad_length = batch_size - num_left_over if num_left_over != 0 else 0
        assume(pad_length != 0)
        batches = list(batched(items, batch_size, padding=pad))
        assert batches[-1][batch_size - pad_length:] == [pad] * pad_length

    def test_pad(self):
        batches = list(batched([0, 0], 3, 42))
        assert batches[-1] == [0, 0, 42]


class TestComplementaryIntervals:

    @given(spaced_ranges(min_num_ranges=1, max_num_ranges=10,
                         min_interval=0, max_interval=10))
    def test_contiguous(self, intervals):
        complements = complementary_intervals(intervals)
        interleaved = list(roundrobin(complements, intervals))
        assert intervals_are_contiguous(interleaved)

    @given(spaced_ranges(min_num_ranges=1, max_num_ranges=10,
                         min_interval=0, max_interval=10),
           integers(0, 10))
    def test_contiguous_with_offset_start(self, intervals, start_offset):
        first_interval_start = intervals[0].start
        start_index = first_interval_start - start_offset
        complements = list(complementary_intervals(intervals, start=start_index))
        assert complements[0] == range(start_index, first_interval_start)

    @given(spaced_ranges(min_num_ranges=1, max_num_ranges=10,
                         min_interval=0, max_interval=10),
           integers(0, 10))
    @example(intervals=[range(0, 0)], end_offset=1)
    def test_contiguous_with_offset_end(self, intervals, end_offset):
        last_interval_end = intervals[-1].stop
        end_index = last_interval_end + end_offset
        complements = list(complementary_intervals(intervals, stop=end_index))
        assert complements[-1] == range(last_interval_end, end_index)


class TestReversedRange:

    @given(r=ranges(max_size=100))
    def test_reversed_range_is_equivalent_to_reversed(self, r):
        assert list(reversed_range(r)) == list(reversed(r))

    @given(r=ranges())
    def test_reversed_reversed_is_what_we_began_with(self, r):
        assert reversed_range(reversed_range(r)) == r


class TestMakeSortedDistinctSequence:

    @given(r=ranges(min_step_value=1))
    def test_ascending_range_result_is_ascending(self, r):
        seq = make_sorted_distinct_sequence(r, sense=SortSense.ascending)
        assert seq.step > 0

    @given(r=ranges(min_step_value=1))
    def test_ascending_range_result_is_descending(self, r):
        seq = make_sorted_distinct_sequence(r, sense=SortSense.descending)
        assert seq.step < 0

    @given(r=ranges(max_step_value=-1))
    def test_descending_range_result_is_ascending(self, r):
        seq = make_sorted_distinct_sequence(r, sense=SortSense.ascending)
        assert seq.step > 0

    @given(r=ranges(max_step_value=-1))
    def test_descending_range_result_is_descending(self, r):
        seq = make_sorted_distinct_sequence(r, sense=SortSense.descending)
        assert seq.step < 0

    @given(r=ranges())
    def test_range_sense_is_preserved(self, r):
        seq = make_sorted_distinct_sequence(r, sense=None)
        assert sgn(r.step) == sgn(seq.step)

    def test_range_with_invalid_sense_value_raises_type_error(self):
        with raises(TypeError):
            make_sorted_distinct_sequence(range(1, 2), 42)

    def test_list_with_invalid_sense_value_raises_type_error(self):
        with raises(TypeError):
            make_sorted_distinct_sequence([1, 2], 42)

    @given(r=sequences(min_size=2, unique=True))
    def test_ascending_sequence_result_is_ascending(self, r):
        s = sorted(r)
        seq = make_sorted_distinct_sequence(s, sense=SortSense.ascending)
        assert is_sorted(seq, reverse=False, distinct=True)

    @given(r=sequences(min_size=2, unique=True))
    def test_ascending_sequence_result_is_descending(self, r):
        s = sorted(r)
        seq = make_sorted_distinct_sequence(s, sense=SortSense.descending)
        assert is_sorted(seq, reverse=True, distinct=True)

    @given(r=sequences(min_size=2, unique=True))
    def test_descending_sequence_result_is_ascending(self, r):
        s = sorted(r, reverse=True)
        seq = make_sorted_distinct_sequence(s, sense=SortSense.ascending)
        assert is_sorted(seq, reverse=False, distinct=True)

    @given(r=sequences(min_size=2, unique=True))
    def test_descending_sequence_result_is_descending(self, r):
        s = sorted(r, reverse=True)
        seq = make_sorted_distinct_sequence(s, sense=SortSense.descending)
        assert is_sorted(seq, reverse=True, distinct=True)

    @given(r=sequences(min_size=2, unique=True),
           b=booleans())
    def test_sequence_sense_is_preserved(self, r, b):
        s = sorted(r, reverse=b)
        seq = make_sorted_distinct_sequence(s, sense=None)
        ascending = is_sorted(seq, reverse=False, distinct=True)
        descending = is_sorted(seq, reverse=True, distinct=True)
        assert b == descending != ascending

