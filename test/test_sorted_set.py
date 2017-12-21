from collections.abc import (Container, Sized, Iterable, Sequence)
import pytest

from segpy.sorted_frozen_set import SortedFrozenSet


class TestConstruction:

    def test_empty(self):
        s = SortedFrozenSet()

    def test_from_sequence(self):
        s = SortedFrozenSet([7, 8, 3, 1])

    def test_with_duplicates(self):
        s = SortedFrozenSet([8, 8, 8])

    def test_from_iterable(self):
        def gen6842():
            yield 6
            yield 8
            yield 4
            yield 2
        g = gen6842()
        s = SortedFrozenSet(g)

    def test_default_empty(self):
        s = SortedFrozenSet()


class TestContainerProtocol:

    @pytest.fixture()
    def s(self):
        return SortedFrozenSet([6, 7, 3, 9])

    def test_positive_contained(self, s):
        assert 6 in s

    def test_negative_contained(self, s):
        assert not 2 in s

    def test_positive_not_contained(self, s):
        assert 5 not in s

    def test_negative_not_contained(self, s):
        assert not 9 not in s

    def test_sequence_protocol(self):
        assert issubclass(SortedFrozenSet, Container)


class TestSizedProtocol:

    def test_empty(self):
        s = SortedFrozenSet()
        assert len(s) == 0

    def test_one(self):
        s = SortedFrozenSet([42])
        assert len(s) == 1

    def test_ten(self):
        s = SortedFrozenSet(range(10))
        assert len(s) == 10

    def test_with_duplicates(self):
        s = SortedFrozenSet([5, 5, 5])
        assert len(s) == 1

    def test_protocol(self):
        assert issubclass(SortedFrozenSet, Sized)


class TestIterableProtocol:

    @pytest.fixture()
    def s(self):
        return SortedFrozenSet([7, 2, 1, 1, 9])

    def test_iter(self, s):
        i = iter(s)
        assert next(i) == 1
        assert next(i) == 2
        assert next(i) == 7
        assert next(i) == 9
        with pytest.raises(StopIteration):
            next(i)

    def test_for_loop(self, s):
        index = 0
        expected = [1, 2, 7, 9]
        for item in s:
            assert item == expected[index]
            index += 1

    def test_protocol(self):
        assert issubclass(SortedFrozenSet, Iterable)


class TestSequenceProtocol:

    @pytest.fixture()
    def s(self):
        return SortedFrozenSet([1, 4, 9, 13, 15])

    def test_index_zero(self, s):
        assert s[0] == 1

    def test_index_four(self, s):
        assert s[4] == 15

    def test_index_one_beyond_the_end(self, s):
        with pytest.raises(IndexError):
            s[5]

    def test_index_minus_one(self, s):
        assert s[-1] == 15

    def test_index_minus_five(self, s):
        assert s[-5] == 1

    def test_index_one_before_the_beginning(self, s):
        with pytest.raises(IndexError):
            s[-6]

    def test_slice_from_start(self, s):
        assert s[:3] == SortedFrozenSet([1, 4, 9])

    def test_slice_to_end(self, s):
        assert s[3:] == SortedFrozenSet([13, 15])

    def test_slice_empty(self, s):
        assert s[10:] == SortedFrozenSet()

    def test_slice_arbitrary(self, s):
        assert s[2:4] == SortedFrozenSet([9, 13])

    def test_slice_full(self, s):
        assert s[:] == s

    def test_reversed(self):
        s = SortedFrozenSet([1, 3, 5, 7])
        r = reversed(s)
        assert next(r) == 7
        assert next(r) == 5
        assert next(r) == 3
        assert next(r) == 1
        with pytest.raises(StopIteration):
            next(r)

    def test_index_positive(self):
        s = SortedFrozenSet([1, 5, 8, 9])
        assert s.index(8) == 2

    def test_index_negative(self):
        s = SortedFrozenSet([1, 5, 8, 9])
        with pytest.raises(ValueError):
            s.index(15)

    def test_count_zero(self):
        s = SortedFrozenSet([1, 5, 7, 9])
        assert s.count(11) == 0

    def test_count_one(self):
        s = SortedFrozenSet([1, 5, 7, 9])
        assert s.count(7) == 1

    def test_protocol(self):
        assert issubclass(SortedFrozenSet, Sequence)

    def test_concatenate_disjoint(self):
        s = SortedFrozenSet([1, 2, 3])
        t = SortedFrozenSet([4, 5, 6])
        assert s + t == SortedFrozenSet([1, 2, 3, 4, 5, 6])

    def test_concatenate_equal(self):
        s = SortedFrozenSet([2, 4, 6])
        assert s + s == s

    def test_concatenate_intersecting(self):
        s = SortedFrozenSet([1, 2, 3])
        t = SortedFrozenSet([3, 4, 5])
        assert s + t == SortedFrozenSet([1, 2, 3, 4, 5])

    def test_repetition_zero_lhs(self):
        s = SortedFrozenSet([4, 5, 6])
        assert 0 * s == SortedFrozenSet()

    def test_repetition_zero_rhs(self):
        s = SortedFrozenSet([4, 5, 6])
        assert s * 0 == SortedFrozenSet()

    def test_repetition_nonzero_lhs(self):
        s = SortedFrozenSet([4, 5, 6])
        assert 100 * s == s

    def test_repetition_nonzero_rhs(self):
        s = SortedFrozenSet([4, 5, 6])
        assert s * 100 == s


class TestReprProtocol:

    def test_repr_empty(self):
        s = SortedFrozenSet()
        assert repr(s) == "SortedFrozenSet()"

    def test_repr_one(self):
        s = SortedFrozenSet([42, 40, 19])
        assert repr(s) == "SortedFrozenSet([19, 40, 42])"


class TestEqualityProtocol:

    def test_positive_equal(self):
        assert SortedFrozenSet([4, 5, 6]) == SortedFrozenSet([6, 5, 4])

    def test_negative_equal(self):
        assert not SortedFrozenSet([4, 5, 6]) == SortedFrozenSet([1, 2, 3])

    def test_type_mismatch(self):
        assert not SortedFrozenSet([4, 5, 6]) == [4, 5, 6]

    def test_identical(self):
        s = SortedFrozenSet([10, 11, 12])
        assert s == s


class TestInequalityProtocol:

    def test_positive_inequal(self):
        assert SortedFrozenSet([4, 5, 6]) != SortedFrozenSet([1, 2, 3])

    def test_negative_inequal(self):
        assert not SortedFrozenSet([4, 5, 6]) != SortedFrozenSet([6, 5, 4])

    def test_type_mismatch(self):
        assert SortedFrozenSet([1, 2, 3]) != [1, 2, 3]

    def test_identical(self):
        s = SortedFrozenSet([10, 11, 12])
        assert not s != s


class TestRelationalSetProtocol:

    def test_lt_positive(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        assert s < t

    def test_lt_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2, 3})
        assert not s < t

    def test_le_lt_positive(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        assert s <= t

    def test_le_eq_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2, 3})
        assert s <= t

    def test_le_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2})
        assert not s <= t

    def test_gt_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2})
        assert s > t

    def test_gt_negative(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        assert not s > t

    def test_ge_gt_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2})
        assert s > t

    def test_ge_eq_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2, 3})
        assert s >= t

    def test_ge_negative(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        assert not s >= t


class TestSetRelationalMethods:

    def test_issubset_proper_positive(self):
        s = SortedFrozenSet({1, 2})
        t = [1, 2, 3]
        assert s.issubset(t)

    def test_issubset_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2, 3]
        assert s.issubset(t)

    def test_issubset_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2]
        assert not s.issubset(t)

    def test_issuperset_proper_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2]
        assert s.issuperset(t)

    def test_issuperset_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2, 3]
        assert s.issuperset(t)

    def test_issuperset_negative(self):
        s = SortedFrozenSet({1, 2})
        t = [1, 2, 3]
        assert not s.issuperset(t)

    def test_isdisjoint_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [4, 5, 6]
        assert s.isdisjoint(t)

    def test_isdisjoint_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [3, 4, 5]
        assert not s.isdisjoint(t)


class TestOperationsSetProtocol:

    def test_intersection(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        assert s & t == SortedFrozenSet({2, 3})

    def test_union(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        assert s | t == SortedFrozenSet({1, 2, 3, 4})

    def test_symmetric_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        assert s ^ t == SortedFrozenSet({1, 4})

    def test_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        assert s - t == SortedFrozenSet({1})


class TestSetOperationsMethods:

    def test_intersection(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        assert s.intersection(t) == SortedFrozenSet({2, 3})

    def test_union(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        assert s.union(t) == SortedFrozenSet({1, 2, 3, 4})

    def test_symmetric_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        assert s.symmetric_difference(t) == SortedFrozenSet({1, 4})

    def test_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        assert s.difference(t) == SortedFrozenSet({1})
