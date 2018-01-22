from itertools import product, count

from hypothesis import given, assume
from hypothesis.strategies import (data, dictionaries, just,
                                   integers, tuples, lists, sets)
from pytest import raises

from segpy.catalog import (CatalogBuilder, DictionaryCatalog, DictionaryCatalog2D, RegularConstantCatalog,
                           ConstantCatalog, RegularCatalog, LinearRegularCatalog, LastIndexVariesQuickestCatalog2D,
                           FirstIndexVariesQuickestCatalog2D)
from segpy.sorted_frozen_set import SortedFrozenSet
from segpy.util import first, last, is_sorted
from test.predicates import check_balanced
from test.strategies import ranges, items2d


class TestCatalogBuilder:

    def test_unspecified_mapping_returns_empty_catalog(self):
        builder = CatalogBuilder()
        catalog = builder.create()
        assert len(catalog) == 0

    def test_empty_mapping_returns_empty_catalog(self):
        builder = CatalogBuilder([])
        catalog = builder.create()
        assert len(catalog) == 0

    def test_mapping_is_neither_dictionary_nor_iterable_raises_type_error(self):
        with raises(TypeError):
            CatalogBuilder(42)

    def test_mapping_iterable_does_not_contain_pairs_raises_value_error(self):
        with raises(ValueError):
            CatalogBuilder([(1, 2, 3)])

    @given(lists(min_size=1, elements=tuples(integers(), integers())))
    def test_duplicate_items_returns_none(self, mapping):
        builder = CatalogBuilder(mapping + mapping)
        catalog = builder.create()
        assert catalog is None

    @given(dictionaries(integers(), integers()))
    def test_arbitrary_mapping(self, mapping):
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        assert len(shared_items) == len(mapping)

    @given(dictionaries(integers(), just(42)))
    def test_constant_mapping(self, mapping):
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        assert len(shared_items) == len(mapping)

    @given(start=integers(),
           num=integers(0, 100),
           step=integers(-100, 100),
           value=integers())
    def test_regular_constant_mapping(self, start, num, step, value):
        assume(step != 0)
        mapping = {key: value for key in range(
            start, start + num * step, step)}
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        assert len(shared_items) == len(mapping)

    @given(start=integers(),
           num=integers(0, 100),
           step=integers(-100, 100),
           values=data())
    def test_regular_mapping(self, start, num, step, values):
        assume(step != 0)
        mapping = {key: values.draw(integers())
                   for key
                   in range(start, start + num * step, step)}
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        assert len(shared_items) == len(mapping)

    @given(num=integers(0, 100),
           key_start=integers(),
           key_step=integers(-100, 100),
           value_start=integers(),
           value_step=integers(-100, 100))
    def test_linear_regular_mapping(self, num, key_start, key_step, value_start, value_step):
        assume(key_step != 0)
        assume(value_step != 0)
        mapping = {key: value for key, value in zip(range(key_start, key_start + num * key_step, key_step),
                                                    range(value_start, value_start + num * value_step, value_step))}
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        assert len(shared_items) == len(mapping)

    @given(dictionaries(tuples(integers(), integers()), integers()))
    def test_arbitrary_mapping_2d(self, mapping):
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        assert len(shared_items) == len(mapping)

    @given(i_start=integers(0, 10),
           i_num=integers(1, 10),
           i_step=just(1),
           j_start=integers(0, 10),
           j_num=integers(1, 10),
           j_step=just(1),
           c=integers(1, 10))
    def test_linear_regular_mapping_2d(self, i_start, i_num, i_step, j_start, j_num, j_step, c):
        assume(i_step != 0)
        assume(j_step != 0)

        def v(i, j):
            return (i - i_start) * ((j_start + j_num * j_step) - j_start) + (j - j_start) + c

        mapping = {(i, j): v(i, j)
                   for i in range(i_start, i_start + i_num * i_step, i_step)
                   for j in range(j_start, j_start + j_num * j_step, j_step)}

        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        assert len(shared_items) == len(mapping)

    @given(mapping=dictionaries(keys=integers(), values=integers()))
    def test_adding_items_puts_them_in_the_catalog(self, mapping):
        builder = CatalogBuilder()
        for key, value in mapping.items():
            builder.add(key, value)
        catalog = builder.create()
        assert all(catalog[key] == value for key, value in mapping.items())

    def test_irregular_mapping_gives_dictionary_catalog(self):
        mapping = {
            1: 2,
            2: 3,
            3: 5,
            5: 7,
            8: 11,
            13: 13,
            21: 17,
            34: 19,
            55: 23,
            89: 29,
            144: 31,
        }
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        assert all(catalog[key] == value for key, value in mapping.items())


class TestLastIndexVariesQuickestCatalog2D:

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_i_range_preserved(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.i_range == i_range

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_j_range_preserved(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.j_range == j_range

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_v_range_preserved(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.v_range == v_range

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_mismatched_ranges_raises_value_error(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges())
        assume(len(v_range) != num_indices)
        with raises(ValueError):
            LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_containment_positive(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert all((i, j) in catalog for (i, j) in product(i_range, j_range))

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_containment_negative_i_out_of_range(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        i = data.draw(integers())
        j = data.draw(integers())
        assume(i not in i_range)
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert (i, j) not in catalog

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_containment_negative_j_out_of_range(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        i = data.draw(integers())
        j = data.draw(integers())
        assume(j not in j_range)
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert (i, j) not in catalog

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_length(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert len(catalog) == num_indices

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_iteration(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert all(a == b for a, b in zip(product(i_range, j_range), iter(catalog)))

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_i_min(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.i_min == i_range.start

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_i_max(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.i_max == i_range.stop - i_range.step

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_j_min(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.j_min == j_range.start

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_j_max(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.j_max == j_range.stop - j_range.step

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_key_min(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.key_min() == (i_range.start, j_range.start)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_key_max(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.key_max() == (i_range.stop - i_range.step,
                                     j_range.stop - j_range.step)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_value_start(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.value_first() == first(v_range)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_value_stop(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.value_last() == last(v_range)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_repr(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        r = repr(catalog)
        assert r.startswith('LastIndexVariesQuickestCatalog2D')
        assert 'i_range={!r}'.format(i_range) in r
        assert 'j_range={!r}'.format(j_range) in r
        assert 'v_range={!r}'.format(v_range) in r
        assert check_balanced(r)

    def test_row_major_example(self):
        d = {
            (0, 4): 8,
            (0, 5): 9,
            (0, 6): 10,
            (1, 4): 11,
            (1, 5): 12,
            (1, 6): 13,
            (2, 4): 14,
            (2, 5): 15,
            (2, 6): 16
        }
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, LastIndexVariesQuickestCatalog2D)
        assert catalog.key_min() == (0, 4)
        assert catalog.key_max() == (2, 6)
        assert catalog.value_first() == 8
        assert catalog.value_last() == 16
        assert catalog.i_min == 0
        assert catalog.i_max == 2
        assert catalog.j_min == 4
        assert catalog.j_max == 6
        assert len(catalog) == 9

        with raises(KeyError):
            _ = catalog[(0, 0)]

        assert all(d[key] == catalog[key] for key in d)

    def test_complex_row_major_example(self):
        i_range = range(1, 31, 3)
        j_range = range(2, 24, 2)
        base = 100
        stride = 4
        d = {k: v for k, v in zip(product(i_range, j_range), count(start=base, step=stride))}
        # The previous line produces a dictionary which looks like this:
        # {(1, 2): 100,
        #  (1, 4): 104,
        #  (1, 6): 108,
        #  (1, 8): 112,
        #  (1, 10): 116,
        #  ...
        #  (28, 14): 520,
        #  (28, 16): 524,
        #  (28, 18): 528,
        #  (28, 20): 532,
        #  (28, 22): 536}

        # The catalog builder needs to be smart enough to recover the i and j ranges, the base
        # value, and the stride from this data.
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, LastIndexVariesQuickestCatalog2D)
        assert catalog.key_min() == (1, 2)
        assert catalog.key_max() == (28, 22)
        assert catalog.value_first() == 100
        assert catalog.value_last() == 536
        assert catalog.i_min == 1
        assert catalog.i_max == 28
        assert catalog.j_min == 2
        assert catalog.j_max == 22
        assert len(catalog) == 110
        assert all(d[key] == catalog[key] for key in d)

    @given(i_range=ranges(min_size=1, max_size=20, min_step_value=1),
           j_range=ranges(min_size=1, max_size=20, min_step_value=1),
           data=data())
    def test_complex_general(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        d = {k: v for k, v in zip(product(i_range, j_range), v_range)}

        # The catalog builder needs to be smart enough to recover the i and j ranges, the base
        # value, and the stride from this data.
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, (LastIndexVariesQuickestCatalog2D, FirstIndexVariesQuickestCatalog2D))
        assert catalog.key_min() == (i_range.start, j_range.start)
        assert catalog.key_max() == (last(i_range), last(j_range))
        assert catalog.value_first() == v_range.start
        assert catalog.value_last() == last(v_range)
        assert catalog.i_min == i_range.start
        assert catalog.i_max == last(i_range)
        assert catalog.j_min == j_range.start
        assert catalog.j_max == last(j_range)
        assert len(catalog) == num_indices
        assert all(d[key] == catalog[key] for key in d)

    @given(i_range=ranges(min_size=2, max_size=20, min_step_value=1),
           j_range=ranges(min_size=2, max_size=20, min_step_value=1),
           data=data())
    def test_complex_always_row_major_general(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        d = {k: v for k, v in zip(product(i_range, j_range), v_range)}

        # The catalog builder needs to be smart enough to recover the i and j ranges, the base
        # value, and the stride from this data.
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, LastIndexVariesQuickestCatalog2D)
        assert catalog.key_min() == (i_range.start, j_range.start)
        assert catalog.key_max() == (last(i_range), last(j_range))
        assert catalog.value_first() == v_range.start
        assert catalog.value_last() == last(v_range)
        assert catalog.i_min == i_range.start
        assert catalog.i_max == last(i_range)
        assert catalog.j_min == j_range.start
        assert catalog.j_max == last(j_range)
        assert len(catalog) == num_indices
        assert all(d[key] == catalog[key] for key in d)

    @given(i_range=ranges(min_size=1, max_size=20, min_step_value=1),
           j_range=ranges(min_size=1, max_size=20, min_step_value=1),
           data=data())
    def test_key(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert all(catalog.key(value) == key for key, value in catalog.items())

    @given(i_range=ranges(min_size=1, max_size=20, min_step_value=1),
           j_range=ranges(min_size=1, max_size=20, min_step_value=1),
           data=data())
    def test_key_missing_raises_value_error(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = LastIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        value = data.draw(integers())
        assume(value not in v_range)
        with raises(ValueError):
            catalog.key(value)


class TestFirstIndexVariesQuickestCatalog2D:

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_i_range_preserved(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.i_range == i_range

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_j_range_preserved(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.j_range == j_range

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_v_range_preserved(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.v_range == v_range

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_mismatched_ranges_raises_value_error(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges())
        assume(len(v_range) != num_indices)
        with raises(ValueError):
            FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_containment_positive(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert all((i, j) in catalog for (i, j) in product(i_range, j_range))

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_containment_negative_i_out_of_range(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        i = data.draw(integers())
        j = data.draw(integers())
        assume(i not in i_range)
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert (i, j) not in catalog

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_containment_negative_j_out_of_range(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        i = data.draw(integers())
        j = data.draw(integers())
        assume(j not in j_range)
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert (i, j) not in catalog

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_length(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert len(catalog) == num_indices

    @given(i_range=ranges(min_size=1, max_size=10, min_step_value=1),
           j_range=ranges(min_size=1, max_size=10, min_step_value=1),
           data=data())
    def test_iteration(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert all(a == b for a, b in zip(((i, j) for (j, i) in product(j_range, i_range)), iter(catalog)))

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_i_min(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.i_min == i_range.start

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_i_max(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.i_max == i_range.stop - i_range.step

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_j_min(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.j_min == j_range.start

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_j_max(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.j_max == j_range.stop - j_range.step

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_key_min(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.key_min() == (i_range.start, j_range.start)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_key_max(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.key_max() == (i_range.stop - i_range.step,
                                     j_range.stop - j_range.step)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_value_start(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.value_first() == first(v_range)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_value_stop(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert catalog.value_last() == last(v_range)

    @given(i_range=ranges(min_size=1, min_step_value=1),
           j_range=ranges(min_size=1, min_step_value=1),
           data=data())
    def test_repr(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        r = repr(catalog)
        assert r.startswith('FirstIndexVariesQuickestCatalog2D')
        assert 'i_range={!r}'.format(i_range) in r
        assert 'j_range={!r}'.format(j_range) in r
        assert 'v_range={!r}'.format(v_range) in r
        assert check_balanced(r)

    def test_column_major_example(self):
        d = {
            (11, 14): 5,
            (13, 14): 10,
            (15, 14): 15,
            (11, 16): 20,
            (13, 16): 25,
            (15, 16): 30,
            (11, 18): 35,
            (13, 18): 40,
            (15, 18): 45
        }
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, FirstIndexVariesQuickestCatalog2D)
        assert catalog.key_min() == (11, 14)
        assert catalog.key_max() == (15, 18)
        assert catalog.value_first() == 5
        assert catalog.value_last() == 45
        assert catalog.i_min == 11
        assert catalog.i_max == 15
        assert catalog.j_min == 14
        assert catalog.j_max == 18
        assert len(catalog) == 9

        with raises(KeyError):
            _ = catalog[(0, 0)]

        assert all(d[key] == catalog[key] for key in d)

    def test_complex_column_major_example(self):
        i_range = range(1, 31, 3)
        j_range = range(2, 24, 2)
        base = 100
        stride = 4
        d = {k: v for k, v in zip(((i, j) for (j, i) in product(j_range, i_range)), count(start=base, step=stride))}
        # The previous line produces a dictionary which looks like this (note that the value here are
        # not consecutive, so while the dictionary is not displayed in column-major (first index varies
        # quickest) order, when sorted by value, it would be:
        # {(1, 2): 100,
        #  (1, 4): 140,
        #  (1, 6): 180,
        #  (1, 8): 220,
        #  (1, 10): 260,
        #  ...
        #  (28, 14): 376,
        #  (28, 16): 416,
        #  (28, 18): 456,
        #  (28, 20): 496,
        #  (28, 22): 536}


        # The catalog builder needs to be smart enough to recover the i and j ranges, the base
        # value, and the stride from this data.
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, FirstIndexVariesQuickestCatalog2D)
        assert catalog.key_min() == (1, 2)
        assert catalog.key_max() == (28, 22)
        assert catalog.value_first() == 100
        assert catalog.value_last() == 536
        assert catalog.i_min == 1
        assert catalog.i_max == 28
        assert catalog.j_min == 2
        assert catalog.j_max == 22
        assert len(catalog) == 110
        assert all(d[key] == catalog[key] for key in d)

    @given(i_range=ranges(min_size=1, max_size=20, min_step_value=1),
           j_range=ranges(min_size=1, max_size=20, min_step_value=1),
           data=data())
    def test_complex_general(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        d = {k: v for k, v in zip(((i, j) for (j, i) in product(j_range, i_range)), v_range)}

        # The catalog builder needs to be smart enough to recover the i and j ranges, the base
        # value, and the stride from this data.
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, (LastIndexVariesQuickestCatalog2D, FirstIndexVariesQuickestCatalog2D))
        assert catalog.key_min() == (i_range.start, j_range.start)
        assert catalog.key_max() == (last(i_range), last(j_range))
        assert catalog.value_first() == v_range.start
        assert catalog.value_last() == last(v_range)
        assert catalog.i_min == i_range.start
        assert catalog.i_max == last(i_range)
        assert catalog.j_min == j_range.start
        assert catalog.j_max == last(j_range)
        assert len(catalog) == num_indices
        assert all(d[key] == catalog[key] for key in d)

    @given(i_range=ranges(min_size=2, max_size=20, min_step_value=1),
           j_range=ranges(min_size=2, max_size=20, min_step_value=1),
           data=data())
    def test_complex_always_column_major_general(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        d = {k: v for k, v in zip(((i, j) for j, i in product(j_range, i_range)), v_range)}

        # The catalog builder needs to be smart enough to recover the i and j ranges, the base
        # value, and the stride from this data.
        catalog_builder = CatalogBuilder(d)
        catalog = catalog_builder.create()
        assert isinstance(catalog, FirstIndexVariesQuickestCatalog2D)
        assert catalog.key_min() == (i_range.start, j_range.start)
        assert catalog.key_max() == (last(i_range), last(j_range))
        assert catalog.value_first() == v_range.start
        assert catalog.value_last() == last(v_range)
        assert catalog.i_min == i_range.start
        assert catalog.i_max == last(i_range)
        assert catalog.j_min == j_range.start
        assert catalog.j_max == last(j_range)
        assert len(catalog) == num_indices
        assert all(d[key] == catalog[key] for key in d)

    @given(i_range=ranges(min_size=1, max_size=20, min_step_value=1),
           j_range=ranges(min_size=1, max_size=20, min_step_value=1),
           data=data())
    def test_key(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        assert all(catalog.key(value) == key for key, value in catalog.items())

    @given(i_range=ranges(min_size=1, max_size=20, min_step_value=1),
           j_range=ranges(min_size=1, max_size=20, min_step_value=1),
           data=data())
    def test_key_missing_raises_value_error(self, i_range, j_range, data):
        num_indices = len(i_range) * len(j_range)
        v_range = data.draw(ranges(min_size=num_indices, max_size=num_indices))
        catalog = FirstIndexVariesQuickestCatalog2D(i_range, j_range, v_range)
        value = data.draw(integers())
        assume(value not in v_range)
        with raises(ValueError):
            catalog.key(value)

class TestDictionaryCatalog:

    @given(dictionaries(integers(), integers()))
    def test_items_keys_are_present(self, items):
        catalog = DictionaryCatalog(items)
        assert all(key in catalog for key in items.keys())

    @given(dictionaries(integers(), integers()))
    def test_items_keys_are_preserved(self, items):
        catalog = DictionaryCatalog(items)
        assert all(catalog[key] == value for key, value in items.items())

    @given(dictionaries(integers(), integers()))
    def test_length(self, items):
        catalog = DictionaryCatalog(items)
        assert len(catalog) == len(items)

    @given(dictionaries(integers(min_value=0, max_value=100), integers(min_value=0, max_value=100)))
    def test_repr(self, items):
        catalog = DictionaryCatalog(items)
        r = repr(catalog)
        assert r.startswith('DictionaryCatalog')
        assert check_balanced(r)


class TestDictionaryCatalog2D:

    @given(items2d(10, 10))
    def test_contruction_from_incorrect_type_raises_type_error(self, items):
        with raises(TypeError):
            DictionaryCatalog2D(items.i_range, items.j_range, 42)

    @given(items2d(10, 10))
    def test_irange_preserved(self, items):
        catalog = DictionaryCatalog2D(items.i_range, items.j_range, items.items)
        assert catalog.i_range == items.i_range

    @given(items2d(10, 10))
    def test_jrange_preserved(self, items):
        catalog = DictionaryCatalog2D(items.i_range, items.j_range, items.items)
        assert catalog.j_range == items.j_range

    @given(i_range=lists(integers(), min_size=2),
           j_range=ranges(min_size=1, max_size=100, min_step_value=1),
           items=dictionaries(integers(min_value=0, max_value=100), integers(min_value=0, max_value=100)))
    def test_unsorted_irange_raises_value_error(self, i_range, j_range, items):
        assume(not is_sorted(i_range))
        with raises(ValueError):
            DictionaryCatalog2D(i_range, j_range, items)

    @given(i_range=ranges(min_size=1, max_size=100, min_step_value=1),
           j_range=lists(integers(), min_size=2),
           items=dictionaries(integers(min_value=0, max_value=100), integers(min_value=0, max_value=100)))
    def test_unsorted_jrange_raises_value_error(self, i_range, j_range, items):
        assume(not is_sorted(j_range))
        with raises(ValueError):
            DictionaryCatalog2D(i_range, j_range, items)

    @given(items2d(10, 10))
    def test_length(self, items):
        catalog = DictionaryCatalog2D(items.i_range, items.j_range, items.items)
        assert len(catalog) == len(items.items)

    @given(items2d(10, 10))
    def test_containment(self, items):
        catalog = DictionaryCatalog2D(items.i_range, items.j_range, items.items)
        assert all(k in catalog for k in items.items.keys())

    @given(items2d(10, 10))
    def test_repr(self, items):
        catalog = DictionaryCatalog2D(items.i_range, items.j_range, items.items)
        r = repr(catalog)
        assert r.startswith('DictionaryCatalog')
        assert 'i_range={!r}'.format(items.i_range) in r
        assert 'j_range={!r}'.format(items.j_range) in r
        assert check_balanced(r)

    def test_illegal_i_key_raises_value_error(self):
        with raises(ValueError):
            DictionaryCatalog2D(range(0, 10, 2),
                                range(0, 10, 1),
                                {(1, 0): 42})

    def test_illegal_j_key_raises_value_error(self):
        with raises(ValueError):
            DictionaryCatalog2D(range(0, 10, 1),
                                range(0, 10, 2),
                                {(0, 1): 42})


class TestRegularConstantCatalog:

    def test_key_min_greater_than_key_max_raises_value_error(self):
        with raises(ValueError):
            RegularConstantCatalog(11, 10, 3, 0)

    def test_illegal_stride_raises_value_error(self):
        with raises(ValueError):
            RegularConstantCatalog(0, 10, 3, 0)

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           c=integers(),
           k=integers())
    def test_missing_key_raises_key_error(self, r, c, k):
        assume(k not in r)
        catalog = RegularConstantCatalog(r.start, r[-1], r.step, c)
        with raises(KeyError):
            catalog[k]

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           c=integers())
    def test_mapping_is_preserved(self, r, c):
        catalog = RegularConstantCatalog(r.start, r[-1], r.step, c)
        assert all(catalog[key] == c for key in r)

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           c=integers())
    def test_length(self, r, c):
        catalog = RegularConstantCatalog(r.start, r[-1], r.step, c)
        assert len(catalog) == len(r)

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           c=integers())
    def test_containment(self, r, c):
        catalog = RegularConstantCatalog(r.start, r[-1], r.step, c)
        assert all(key in catalog for key in r)

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           c=integers())
    def test_iteration(self, r, c):
        catalog = RegularConstantCatalog(r.start, r[-1], r.step, c)
        assert all(k == m for k, m in zip(iter(catalog), r))

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           c=integers())
    def test_repr(self, r, c):
        catalog = RegularConstantCatalog(r.start, r[-1], r.step, c)
        r = repr(catalog)
        assert r.startswith('RegularConstantCatalog')
        assert 'key_min={}'.format(catalog._key_min) in r
        assert 'key_max={}'.format(catalog._key_max) in r
        assert 'key_stride={}'.format(catalog._key_stride) in r
        assert check_balanced(r)


class TestConstantCatalog:

    @given(keys=lists(integers()),
           value=integers(),
           k=integers())
    def test_missing_key_raises_key_error(self, keys, value, k):
        assume(k not in keys)
        catalog = ConstantCatalog(keys, value)
        with raises(KeyError):
            catalog[k]

    @given(keys=lists(integers()),
           value=integers())
    def test_mapping_is_preserved(self, keys, value):
        catalog = ConstantCatalog(keys, value)
        assert all(catalog[key] == value for key in keys)

    @given(keys=sets(integers()),
           value=integers())
    def test_length(self, keys, value):
        catalog = ConstantCatalog(keys, value)
        assert len(catalog) == len(keys)

    @given(keys=lists(integers()),
           value=integers())
    def test_containment(self, keys, value):
        catalog = ConstantCatalog(keys, value)
        assert all(key in catalog for key in keys)

    @given(keys=lists(integers()),
           value=integers())
    def test_iteration(self, keys, value):
        s = SortedFrozenSet(keys)
        catalog = ConstantCatalog(keys, value)
        assert all(k == m for k, m in zip(iter(catalog), s))

    @given(keys=lists(integers()),
           value=integers())
    def test_repr(self, keys, value):
        catalog = ConstantCatalog(keys, value)
        r = repr(catalog)
        assert r.startswith('ConstantCatalog')
        assert 'keys=[{} items]'.format(len(catalog._keys)) in r
        assert 'value={}'.format(catalog._value) in r
        assert check_balanced(r)


class TestRegularCatalog:

    def test_key_min_greater_than_key_max_raises_value_error(self):
        with raises(ValueError):
            RegularCatalog(11, 10, 2, [0])

    def test_illegal_stride_raises_value_error(self):
        with raises(ValueError):
            RegularCatalog(0, 10, 3, [0])

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           d=data())
    def test_mismatched_values_length_raises_value_error(self, r, d):
        values = d.draw(lists(integers()))
        assume(len(values) != len(r))
        with raises(ValueError):
            RegularCatalog(r.start, r[-1], r.step, values)

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           d=data())
    def test_missing_key_raises_key_error(self, r, d):
        values = d.draw(lists(integers(), min_size=len(r), max_size=len(r)))
        k = d.draw(integers())
        assume(k not in r)
        catalog = RegularCatalog(r.start, r[-1], r.step, values)
        with raises(KeyError):
            catalog[k]

    def test_missing_key_raises_key_error_2(self):
        catalog = RegularCatalog(0, 6, 2, [0, 2, 4, 6])
        with raises(KeyError):
            catalog[1]

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           d=data())
    def test_mapping_is_preserved(self, r, d):
        values = d.draw(lists(integers(), min_size=len(r), max_size=len(r)))
        catalog = RegularCatalog(r.start, r[-1], r.step, values)
        assert all(catalog[k] == v for k, v in zip(r, values))

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           d=data())
    def test_length(self, r, d):
        values = d.draw(lists(integers(), min_size=len(r), max_size=len(r)))
        catalog = RegularCatalog(r.start, r[-1], r.step, values)
        assert len(catalog) == len(r)

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           d=data())
    def test_containment(self, r, d):
        values = d.draw(lists(integers(), min_size=len(r), max_size=len(r)))
        catalog = RegularCatalog(r.start, r[-1], r.step, values)
        assert all(key in catalog for key in r)

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           d=data())
    def test_iteration(self, r, d):
        values = d.draw(lists(integers(), min_size=len(r), max_size=len(r)))
        catalog = RegularCatalog(r.start, r[-1], r.step, values)
        assert all(k == m for k, m in zip(iter(catalog), r))

    @given(r=ranges(min_size=1, max_size=100, min_step_value=1),
           d=data())
    def test_repr(self, r, d):
        values = d.draw(lists(integers(), min_size=len(r), max_size=len(r)))
        catalog = RegularCatalog(r.start, r[-1], r.step, values)
        r = repr(catalog)
        assert r.startswith('RegularCatalog')
        assert 'key_min={}'.format(catalog._key_min) in r
        assert 'key_max={}'.format(catalog._key_max) in r
        assert 'key_stride={}'.format(catalog._key_stride) in r
        assert 'values=[{} items]'.format(len(catalog._values)) in r
        assert check_balanced(r)


class TestLinearRegularCatalog:

    @given(key_range=ranges(min_size=2, max_size=100, min_step_value=1),
           data=data())
    def test_mapping_preserved(self, key_range, data):
        value_range = data.draw(ranges(min_size=len(key_range), max_size=len(key_range)))
        catalog = LinearRegularCatalog(key_range.start, key_range[-1], key_range.step,
                                       value_range.start, value_range[-1], value_range.step)
        assert all(catalog[k] == v for k, v in zip(key_range, value_range))

    @given(key_range=ranges(min_size=2, max_size=100, min_step_value=1),
           data=data())
    def test_mismatched_value_length_raises_value_error(self, key_range, data):
        value_range = data.draw(ranges(min_size=len(key_range) + 1, max_size=len(key_range) + 1))
        with raises(ValueError):
            LinearRegularCatalog(key_range.start, key_range[-1], key_range.step,
                                           value_range.start, value_range[-1], value_range.step)

    def test_min_key_less_than_max_key_raises_value_error(self):
        with raises(ValueError):
            LinearRegularCatalog(11, 10, 1, 0, 10, 10)

    def test_min_key_equal_to_max_key_raises_value_error(self):
        with raises(ValueError):
            LinearRegularCatalog(10, 10, 1, 0, 10, 10)

    def test_zero_key_stride_raises_value_error(self):
        with raises(ValueError):
            LinearRegularCatalog(0, 10, 0, 0, 10, 10)

    def test_zero_value_stride_raises_value_error(self):
        with raises(ValueError):
            LinearRegularCatalog(0, 10, 1, 0, 10, 0)

    def test_non_multiple_key_stride_raises_value_error(self):
        with raises(ValueError):
            LinearRegularCatalog(0, 10, 3, 0, 10, 2)

    def test_non_multiple_value_stride_raises_value_error(self):
        with raises(ValueError):
            LinearRegularCatalog(0, 10, 2, 0, 10, 3)

    @given(key_range=ranges(min_size=2, max_size=100, min_step_value=1),
           data=data())
    def test_out_of_range_key_raises_value_error(self, key_range, data):
        value_range = data.draw(ranges(min_size=len(key_range), max_size=len(key_range)))
        key = data.draw(integers())
        assume(not (key_range.start <= key <= key_range[-1]))
        catalog = LinearRegularCatalog(key_range.start, key_range[-1], key_range.step,
                                       value_range.start, value_range[-1], value_range.step)
        with raises(KeyError):
            catalog[key]

    def test_key_off_stride_raises_value_error(self):
        catalog = LinearRegularCatalog(0, 10, 2, 0, 20, 4)
        with raises(KeyError):
            catalog[1]

    @given(key_range=ranges(min_size=2, max_size=100, min_step_value=1),
           data=data())
    def test_length(self, key_range, data):
        value_range = data.draw(ranges(min_size=len(key_range), max_size=len(key_range)))
        catalog = LinearRegularCatalog(key_range.start, key_range[-1], key_range.step,
                                       value_range.start, value_range[-1], value_range.step)
        assert len(catalog) == len(key_range)

    @given(key_range=ranges(min_size=2, max_size=100, min_step_value=1),
           data=data())
    def test_containment(self, key_range, data):
        value_range = data.draw(ranges(min_size=len(key_range), max_size=len(key_range)))
        catalog = LinearRegularCatalog(key_range.start, key_range[-1], key_range.step,
                                       value_range.start, value_range[-1], value_range.step)
        assert all(k in catalog for k in key_range)

    @given(key_range=ranges(min_size=2, max_size=100, min_step_value=1),
           data=data())
    def test_iteration(self, key_range, data):
        value_range = data.draw(ranges(min_size=len(key_range), max_size=len(key_range)))
        catalog = LinearRegularCatalog(key_range.start, key_range[-1], key_range.step,
                                       value_range.start, value_range[-1], value_range.step)
        assert all(k == m for k, m in zip(key_range, iter(catalog)))

    @given(key_range=ranges(min_size=2, max_size=100, min_step_value=1),
           data=data())
    def test_repr(self, key_range, data):
        value_range = data.draw(ranges(min_size=len(key_range), max_size=len(key_range)))
        catalog = LinearRegularCatalog(key_range.start, key_range[-1], key_range.step,
                                       value_range.start, value_range[-1], value_range.step)
        r = repr(catalog)
        assert r.startswith('LinearRegularCatalog')
        assert 'key_min={}'.format(catalog._key_min) in r
        assert 'key_max={}'.format(catalog._key_max) in r
        assert 'key_stride={}'.format(catalog._key_stride) in r
        assert 'value_first={}'.format(catalog._value_start) in r
        assert 'value_last={}'.format(catalog._value_stop) in r
        assert 'value_stride={}'.format(catalog._value_stride) in r
        assert check_balanced(r)
