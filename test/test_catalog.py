from hypothesis import given, assume
from hypothesis.strategies import (data, dictionaries, just,
                                   integers, tuples, lists)
from pytest import raises

from segpy.catalog import CatalogBuilder, RowMajorCatalog2D
from test.predicates import check_balanced
from test.strategies import ranges


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
           num=integers(0, 1000),
           step=integers(-1000, 1000),
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
           num=integers(0, 1000),
           step=integers(-1000, 1000),
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

    @given(num=integers(0, 1000),
           key_start=integers(),
           key_step=integers(-1000, 1000),
           value_start=integers(),
           value_step=integers(-1000, 1000))
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


class TestRowMajorCatalog2D:

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_irange_preserved(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.i_range == i_range

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_jrange_preserved(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.j_range == j_range

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_constant_preserved(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.constant == constant

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_i_min(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.i_min == i_range.start

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_i_max(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.i_max == i_range.stop - i_range.step

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_j_min(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.j_min == j_range.start

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_j_max(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.j_max == j_range.stop - j_range.step

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_key_min(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.key_min() == (i_range.start, j_range.start)

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_key_max(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.key_max() == (i_range.stop - i_range.step,
                                     j_range.stop - j_range.step)

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_value_start(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        assert catalog.value_start() == constant

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_value_stop(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        # for key, value in catalog.items():
        #     print(key, value)
        # print()
        i_min = i_range.start
        i_max = i_range.stop - i_range.step
        j_min = j_range.start
        j_max = j_range.stop - j_range.step
        assert catalog.value_stop() == (i_max - i_min) * (j_max + 1 - j_min) + (j_max - j_min) + constant

    @given(i_range=ranges(min_size=1),
           j_range=ranges(min_size=1),
           constant=integers())
    def test_repr(self, i_range, j_range, constant):
        catalog = RowMajorCatalog2D(i_range, j_range, constant)
        r = repr(catalog)
        assert r.startswith('RowMajorCatalog2D')
        assert 'i_range={!r}'.format(i_range) in r
        assert 'j_range={!r}'.format(j_range) in r
        assert 'constant={!r}'.format(constant) in r
        assert check_balanced(r)

    def test_row_major_example(self):
        mapping = {
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
        catalog_builder = CatalogBuilder(mapping)
        catalog = catalog_builder.create()
        assert isinstance(catalog, RowMajorCatalog2D)
        assert catalog.key_min() == (0, 4)
        assert catalog.key_max() == (2, 6)
        assert catalog.value_start() == 8
        assert catalog.value_stop() == 16
        assert catalog.constant == 8
        assert catalog.i_min == 0
        assert catalog.i_max == 2
        assert catalog.j_min == 4
        assert catalog.j_max == 6
        assert len(catalog) == 9

        with raises(KeyError):
            catalog[(0, 0)]
