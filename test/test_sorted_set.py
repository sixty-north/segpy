import unittest
from collections.abc import (Container, Sized, Iterable, Sequence)

from segpy.sorted_set import SortedFrozenSet


class TestConstruction(unittest.TestCase):

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



class TestContainerProtocol(unittest.TestCase):

    def setUp(self):
        self.s = SortedFrozenSet([6, 7, 3, 9])

    def test_positive_contained(self):
        self.assertTrue(6 in self.s)

    def test_negative_contained(self):
        self.assertFalse(2 in self.s)

    def test_positive_not_contained(self):
        self.assertTrue(5 not in self.s)

    def test_negative_not_contained(self):
        self.assertFalse(9 not in self.s)

    def test_sequence_protocol(self):
        self.assertTrue(issubclass(SortedFrozenSet, Container))


class TestSizedProtocol(unittest.TestCase):

    def test_empty(self):
        s = SortedFrozenSet()
        self.assertEqual(len(s), 0)

    def test_one(self):
        s = SortedFrozenSet([42])
        self.assertEqual(len(s), 1)

    def test_ten(self):
        s = SortedFrozenSet(range(10))
        self.assertEqual(len(s), 10)

    def test_with_duplicates(self):
        s = SortedFrozenSet([5, 5, 5])
        self.assertEqual(len(s), 1)

    def test_protocol(self):
        self.assertTrue(issubclass(SortedFrozenSet, Sized))


class TestIterableProtocol(unittest.TestCase):

    def setUp(self):
        self.s = SortedFrozenSet([7, 2, 1, 1, 9])

    def test_iter(self):
        i = iter(self.s)
        self.assertEqual(next(i), 1)
        self.assertEqual(next(i), 2)
        self.assertEqual(next(i), 7)
        self.assertEqual(next(i), 9)
        self.assertRaises(StopIteration, lambda: next(i))

    def test_for_loop(self):
        index = 0
        expected = [1, 2, 7, 9]
        for item in self.s:
            self.assertEqual(item, expected[index])
            index += 1

    def test_protocol(self):
        self.assertTrue(issubclass(SortedFrozenSet, Iterable))

class TestSequenceProtocol(unittest.TestCase):

    def setUp(self):
        self.s = SortedFrozenSet([1, 4, 9, 13, 15])

    def test_index_zero(self):
        self.assertEqual(self.s[0], 1)

    def test_index_four(self):
        self.assertEqual(self.s[4], 15)

    def test_index_one_beyond_the_end(self):
        self.assertRaises(IndexError, lambda: self.s[5])

    def test_index_minus_one(self):
        self.assertEqual(self.s[-1], 15)

    def test_index_minus_five(self):
        self.assertEqual(self.s[-5], 1)

    def test_index_one_before_the_beginning(self):
        self.assertRaises(IndexError, lambda: self.s[-6])

    def test_slice_from_start(self):
        self.assertEqual(self.s[:3], SortedFrozenSet([1, 4, 9]))

    def test_slice_to_end(self):
        self.assertEqual(self.s[3:], SortedFrozenSet([13, 15]))

    def test_slice_empty(self):
        self.assertEqual(self.s[10:], SortedFrozenSet())

    def test_slice_arbitrary(self):
        self.assertEqual(self.s[2:4], SortedFrozenSet([9, 13]))

    def test_slice_full(self):
        self.assertEqual(self.s[:], self.s)

    def test_reversed(self):
        s = SortedFrozenSet([1, 3, 5, 7])
        r = reversed(s)
        self.assertEqual(next(r), 7)
        self.assertEqual(next(r), 5)
        self.assertEqual(next(r), 3)
        self.assertEqual(next(r), 1)
        self.assertRaises(StopIteration, lambda: next(r))

    def test_index_positive(self):
        s = SortedFrozenSet([1, 5, 8, 9])
        self.assertEqual(s.index(8), 2)

    def test_index_negative(self):
        s = SortedFrozenSet([1, 5, 8, 9])
        self.assertRaises(ValueError, lambda: s.index(15))

    def test_count_zero(self):
        s = SortedFrozenSet([1, 5, 7, 9])
        self.assertEqual(s.count(11), 0)

    def test_count_one(self):
        s = SortedFrozenSet([1, 5, 7, 9])
        self.assertEqual(s.count(7), 1)

    def test_protocol(self):
        self.assertTrue(issubclass(SortedFrozenSet, Sequence))

    def test_concatenate_disjoint(self):
        s = SortedFrozenSet([1, 2, 3])
        t = SortedFrozenSet([4, 5, 6])
        self.assertEqual(s + t, SortedFrozenSet([1, 2, 3, 4, 5, 6]))

    def test_concatenate_equal(self):
        s = SortedFrozenSet([2, 4, 6])
        self.assertEqual(s + s, s)

    def test_concatenate_intersecting(self):
        s = SortedFrozenSet([1, 2, 3])
        t = SortedFrozenSet([3, 4, 5])
        self.assertEqual(s + t, SortedFrozenSet([1, 2, 3, 4, 5]))

    def test_repetition_zero_lhs(self):
        s = SortedFrozenSet([4, 5, 6])
        self.assertEquals(0 * s, SortedFrozenSet())

    def test_repetition_zero_rhs(self):
        s = SortedFrozenSet([4, 5, 6])
        self.assertEquals(s * 0, SortedFrozenSet())

    def test_repetition_nonzero_lhs(self):
        s = SortedFrozenSet([4, 5, 6])
        self.assertEquals(100 * s, s)

    def test_repetition_nonzero_rhs(self):
        s = SortedFrozenSet([4, 5, 6])
        self.assertEquals(s * 100, s)

class TestReprProtocol(unittest.TestCase):

    def test_repr_empty(self):
        s = SortedFrozenSet()
        self.assertEqual(repr(s), "SortedFrozenSet()")

    def test_repr_one(self):
        s = SortedFrozenSet([42, 40, 19])
        self.assertEqual(repr(s), "SortedFrozenSet([19, 40, 42])")


class TestEqualityProtocol(unittest.TestCase):

    def test_positive_equal(self):
        self.assertTrue(SortedFrozenSet([4, 5, 6]) == SortedFrozenSet([6, 5, 4]))

    def test_negative_equal(self):
        self.assertFalse(SortedFrozenSet([4, 5, 6]) == SortedFrozenSet([1, 2, 3]))

    def test_type_mismatch(self):
        self.assertFalse(SortedFrozenSet([4, 5, 6]) == [4, 5, 6])

    def test_identical(self):
        s = SortedFrozenSet([10, 11, 12])
        self.assertTrue(s == s)


class TestInequalityProtocol(unittest.TestCase):

    def test_positive_inequal(self):
        self.assertTrue(SortedFrozenSet([4, 5, 6]) != SortedFrozenSet([1, 2, 3]))

    def test_negative_inequal(self):
        self.assertFalse(SortedFrozenSet([4, 5, 6]) != SortedFrozenSet([6, 5, 4]))

    def test_type_mismatch(self):
        self.assertTrue(SortedFrozenSet([1, 2, 3]) != [1, 2, 3])

    def test_identical(self):
        s = SortedFrozenSet([10, 11, 12])
        self.assertFalse(s != s)


class TestRelationalSetProtocol(unittest.TestCase):

    def test_lt_positive(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        self.assertTrue(s < t)

    def test_lt_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2, 3})
        self.assertFalse(s < t)

    def test_le_lt_positive(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        self.assertTrue(s <= t)

    def test_le_eq_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2, 3})
        self.assertTrue(s <= t)

    def test_le_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2})
        self.assertFalse(s <= t)

    def test_gt_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2})
        self.assertTrue(s > t)

    def test_gt_negative(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        self.assertFalse(s > t)

    def test_ge_gt_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2})
        self.assertTrue(s > t)

    def test_ge_eq_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({1, 2, 3})
        self.assertTrue(s >= t)

    def test_ge_negative(self):
        s = SortedFrozenSet({1, 2})
        t = SortedFrozenSet({1, 2, 3})
        self.assertFalse(s >= t)


class TestSetRelationalMethods(unittest.TestCase):

    def test_issubset_proper_positive(self):
        s = SortedFrozenSet({1, 2})
        t = [1, 2, 3]
        self.assertTrue(s.issubset(t))

    def test_issubset_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2, 3]
        self.assertTrue(s.issubset(t))

    def test_issubset_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2]
        self.assertFalse(s.issubset(t))

    def test_issuperset_proper_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2]
        self.assertTrue(s.issuperset(t))

    def test_issuperset_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [1, 2, 3]
        self.assertTrue(s.issuperset(t))

    def test_issuperset_negative(self):
        s = SortedFrozenSet({1, 2})
        t = [1, 2, 3]
        self.assertFalse(s.issuperset(t))

    def test_isdisjoint_positive(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [4, 5, 6]
        self.assertTrue(s.isdisjoint(t))

    def test_isdisjoint_negative(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [3, 4, 5]
        self.assertFalse(s.isdisjoint(t))


class TestOperationsSetProtocol(unittest.TestCase):

    def test_intersection(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        self.assertEqual(s & t, SortedFrozenSet({2, 3}))

    def test_union(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        self.assertEqual(s | t, SortedFrozenSet({1, 2, 3, 4}))

    def test_symmetric_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        self.assertEqual(s ^ t, SortedFrozenSet({1, 4}))

    def test_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = SortedFrozenSet({2, 3, 4})
        self.assertEqual(s - t, SortedFrozenSet({1}))

class TestSetOperationsMethods(unittest.TestCase):

    def test_intersection(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        self.assertEqual(s.intersection(t), SortedFrozenSet({2, 3}))

    def test_union(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        self.assertEqual(s.union(t), SortedFrozenSet({1, 2, 3, 4}))

    def test_symmetric_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        self.assertEqual(s.symmetric_difference(t), SortedFrozenSet({1, 4}))

    def test_difference(self):
        s = SortedFrozenSet({1, 2, 3})
        t = [2, 3, 4]
        self.assertEqual(s.difference(t), SortedFrozenSet({1}))

if __name__ == '__main__':
    unittest.main()
