import time
from hypothesis import given, assume, example
from hypothesis.strategies import integers, lists, booleans, tuples, dictionaries, text, sets
from pytest import raises

from segpy.util import batched, complementary_intervals, intervals_are_contiguous, roundrobin, reversed_range, \
    make_sorted_distinct_sequence, SortSense, sgn, is_sorted, measure_stride, last, first, minmax, \
    intervals_partially_overlap, now_millis, round_up, underscores_to_camelcase, first_sentence, lower_first, \
    is_magic_name, super_class, collect_attributes
from test.strategies import spaced_ranges, ranges, sequences, PRINTABLE_ASCII_ALPHABET


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

    def test_batch_size_less_than_one_raises_value_error(self):
        with raises(ValueError):
            batched([1, 2, 3], 0)


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

    def test_empty_intervals_raises_value_error(self):
        with raises(ValueError):
            complementary_intervals([])


class TestIntervalsAreContiguous:

    def test_intervals_are_contiguous_positive(self):
        assert intervals_are_contiguous([
            range(0, 10),
            range(10, 20),
            range(20, 30),
        ])

    def test_intervals_are_contiguous_negative(self):
        assert not intervals_are_contiguous([
            range(0, 10),
            range(10, 19),
            range(20, 30),
        ])


class TestIntervalsPartiallyOverlap():

    @given(boundaries=sets(elements=integers(), min_size=4, max_size=4))
    def test_intervals_partially_overlap_positive(self, boundaries):
        p, q, r, s = sorted(boundaries)
        interval_a = range(p, r)
        interval_b = range(q, s)
        assert intervals_partially_overlap(interval_a, interval_b)

    @given(boundaries=sets(elements=integers(), min_size=4, max_size=4))
    def test_intervals_partially_overlap_positive_reversed(self, boundaries):
        p, q, r, s = sorted(boundaries)
        interval_a = range(q, s)
        interval_b = range(p, r)
        assert intervals_partially_overlap(interval_a, interval_b)

    @given(boundaries=sets(elements=integers(), min_size=4, max_size=4))
    def test_intervals_partially_overlap_negative_disjoint(self, boundaries):
        p, q, r, s = sorted(boundaries)
        interval_a = range(p, q)
        interval_b = range(r, s)
        assert not intervals_partially_overlap(interval_a, interval_b)

    @given(boundaries=sets(elements=integers(), min_size=2, max_size=2))
    def test_intervals_partially_overlap_negative_equal(self, boundaries):
        p, q = sorted(boundaries)
        interval_a = range(p, q)
        interval_b = range(p, q)
        assert not intervals_partially_overlap(interval_a, interval_b)


class TestNowMillis:

    def test_about_now(self):
        m1 = time.time() * 1000
        time.sleep(0.001)
        m2 = now_millis()
        time.sleep(0.001)
        m3 = time.time() * 1000
        assert m1 <= m2 <= m3


class TestRoundUp:

    @given(integer=integers(),
           multiple=integers(min_value=0))
    def test_rounded_up_is_greater_or_equal(self, integer, multiple):
        assume(multiple != 0)
        r = round_up(integer, multiple)
        assert r >= integer

    @given(integer=integers(),
           multiple=integers(min_value=0))
    def test_rounded_up_is_a_mutiple(self, integer, multiple):
        assume(multiple != 0)
        r = round_up(integer, multiple)
        assert r % multiple == 0

    @given(integer=integers(),
           multiple=integers(max_value=0))
    def test_rounded_up_non_positive_multiple_raises_value_error(self, integer, multiple):
        assume(multiple != 0)
        with raises(ValueError):
            round_up(integer, multiple)


class TestUnderscoresToCamelCase:

    def test_example(self):
        assert underscores_to_camelcase("the_quick_brown_fox") == "TheQuickBrownFox"



PRINTABLE_ASCII_ALPHANUMERIC = [c for c in PRINTABLE_ASCII_ALPHABET if c.isalnum()]


class TestFirstSentence:

    @given(sentence_a=text(alphabet=PRINTABLE_ASCII_ALPHANUMERIC),
           sentence_b=text(alphabet=PRINTABLE_ASCII_ALPHANUMERIC))
    def test_successfully_extracts_first_sentence(self, sentence_a, sentence_b):
        t = sentence_a + '. ' + sentence_b
        assert first_sentence(t) == sentence_a + '.'


class TestLowerFirst:

    def test_first_character_is_lowercased(self):
        assert lower_first("ABCdef") == "aBCdef"


class TestIsMagicName:

    @given(root=text(alphabet=PRINTABLE_ASCII_ALPHABET, min_size=1))
    def test_is_magic_name_positive(self, root):
        magic_name = '__' + root + '__'
        assert is_magic_name(magic_name)

    @given(root=text(alphabet=PRINTABLE_ASCII_ALPHABET, min_size=1))
    def test_is_magic_name_negative(self, root):
        muggle_name = root
        assert not is_magic_name(muggle_name)




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


class TestSuperClass:

    def test_super_class_multiple(self):

        class A:
            pass

        class B:
            pass

        class C(A, B):
            pass

        assert super_class(C) == A
        assert super_class(A) == object
        assert super_class(B) == object

    def test_super_class_single(self):
        assert super_class(object) == object


class TestIsSorted:

    @given(r=sequences(min_size=2, unique=True))
    def test_is_sequence_sorted_ascending_positive(self, r):
        s = sorted(r)
        assert is_sorted(s, reverse=False, distinct=True)

    @given(r=sequences(min_size=2))
    def test_is_sequence_sorted_ascending_negative(self, r):
        s = sorted(r, reverse=True)
        assert not is_sorted(s, reverse=False, distinct=True)

    @given(r=sequences(min_size=2, unique=True))
    def test_is_sequence_sorted_descending_positive(self, r):
        s = sorted(r, reverse=True)
        assert is_sorted(s, reverse=True, distinct=True)

    @given(r=sequences(min_size=2))
    def test_is_sequence_sorted_descending_negative(self, r):
        s = sorted(r, reverse=False)
        assert not is_sorted(s, reverse=True, distinct=True)

    @given(r=sequences(min_size=2, max_size=100))
    def test_is_sequence_sorted_ascending_positive_duplicates(self, r):
        s = sorted(r + r, reverse=False)
        assert is_sorted(s, reverse=False)

    @given(r=sequences(min_size=2, max_size=100, unique=True))
    def test_is_sequence_sorted_ascending_negative_duplicates(self, r):
        s = sorted(r + r, reverse=True)
        assert not is_sorted(s, reverse=False)

    @given(r=sequences(min_size=2, max_size=100))
    def test_is_sequence_sorted_descending_positive_duplicates(self, r):
        s = sorted(r + r, reverse=True)
        assert is_sorted(s, reverse=True)

    @given(r=sequences(min_size=2, max_size=100, unique=True))
    def test_is_sequence_sorted_descending_negative_duplicates(self, r):
        s = sorted(r + r, reverse=False)
        assert not is_sorted(s, reverse=True)

    def test_empty_sequence_is_sorted_ascending(self):
        assert is_sorted([], reverse=False, distinct=True)

    def test_empty_sequence_is_sorted_descending(self):
        assert is_sorted([], reverse=True, distinct=True)

    @given(r=sequences(min_size=1, max_size=1))
    def test_sequence_of_one_is_sorted_ascending(self, r):
        assert is_sorted(r, reverse=False, distinct=True)

    @given(r=sequences(min_size=1, max_size=1))
    def test_sequence_of_one_is_sorted_descending(self, r):
        assert is_sorted(r, reverse=True, distinct=True)

    @given(r=ranges(min_size=2, min_step_value=1))
    def test_is_range_sorted_ascending_positive(self, r):
        assert is_sorted(r, reverse=False, distinct=True)

    @given(r=ranges(min_size=2, max_step_value=-1))
    def test_is_range_sorted_ascending_negative(self, r):
        assert not is_sorted(r, reverse=False, distinct=True)

    @given(r=ranges(min_size=2, max_step_value=-1))
    def test_is_range_sorted_descending_positive(self, r):
        assert is_sorted(r, reverse=True, distinct=True)

    @given(r=ranges(min_size=2, min_step_value=1))
    def test_is_range_sorted_descending_negative(self, r):
        assert not is_sorted(r, reverse=True, distinct=True)

    @given(r=ranges(max_size=0))
    def test_empty_range_is_sorted_ascending(self, r):
        assert is_sorted(r, reverse=False, distinct=True)

    @given(r=ranges(max_size=0))
    def test_empty_range_is_sorted_descending(self, r):
        assert is_sorted(r, reverse=True, distinct=True)

    @given(r=ranges(max_size=1, min_size=1))
    def test_range_of_one_is_sorted_ascending(self, r):
        assert is_sorted(r, reverse=False, distinct=True)

    @given(r=ranges(max_size=1, min_size=1))
    def test_range_of_one_is_sorted_descending(self, r):
        assert is_sorted(r, reverse=True, distinct=True)


class TestMeasureStride:

    @given(r=ranges())
    def test_measure_range_stride(self, r):
        s = measure_stride(r)
        assert s == r.step

    @given(r=ranges(min_size=2, max_size=1000))
    def test_measure_list_stride_regular(self, r):
        t = list(r)
        s = measure_stride(t)
        assert s == r.step

    @given(r=ranges(min_size=2, max_size=1000))
    def test_measure_list_stride_irregular(self, r):
        t = list(r) + list(r)
        s = measure_stride(t)
        assert s is None

    @given(s=sequences(min_size=1, max_size=1))
    def test_stride_of_sequence_of_one_is_none(self, s):
        assert measure_stride(s) is None

    @given(s=sequences(max_size=0))
    def test_stride_of_empty_sequence_is_none(self, s):
        assert measure_stride(s) is None


class TestFirst:

    @given(s=sequences(min_size=1, max_size=100))
    def test_first_sequences(self, s):
        assert first(s) == s[0]

    def test_empty_iterable_raises_value_error(self):
        r = range(0, 0)
        with raises(ValueError):
            first(r)


class TestLast:

    @given(s=sequences(min_size=1, max_size=100))
    def test_last_sequences(self, s):
        assert last(s) == s[-1]

    @given(s=sequences(min_size=1, max_size=100))
    def test_last_iterable(self, s):
        assert last(iter(s)) == s[-1]

    def test_empty_iterable_raises_value_error(self):
        r = range(0, 0)
        with raises(ValueError):
            last(r)


class TestMinMax:

    def test_empty_iterable_raises_value_error(self):
        r = range(0, 0)
        with raises(ValueError):
            minmax(r)

    @given(s=sequences(min_size=1, max_size=100))
    def test_minmax_sequences(self, s):
        a, b = minmax(s)
        assert a == min(s)
        assert b == max(s)

