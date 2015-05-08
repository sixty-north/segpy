import unittest

from hypothesis import given, example, assume
from hypothesis.specifiers import dictionary, just, integers_in_range, streaming
from segpy.catalog import CatalogBuilder


class TestCatalogBuilder(unittest.TestCase):

    @given(dictionary(int, int))
    def test_arbitrary_mapping(self, mapping):
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))

    @given(dictionary(int, just(42)))
    def test_constant_mapping(self, mapping):
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))

    @given(start=int,
           num=integers_in_range(0, 10000),
           step=integers_in_range(-10000, 10000),
           value=int)
    def test_regular_constant_mapping(self, start, num, step, value):
        mapping = {key: value for key in range(start, start + num*step, step)}
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))

    @given(start=int,
           num=integers_in_range(0, 10000),
           step=integers_in_range(-10000, 10000),
           values=streaming(int))
    def test_regular_mapping(self, start, num, step, values):
        assume(step != 0)
        mapping = {key: value for key, value in zip(range(start, start + num*step, step), values)}
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))

    @given(num=integers_in_range(0, 10000),
           key_start=int,
           key_step=integers_in_range(-10000, 10000),
           value_start=int,
           value_step=integers_in_range(-10000, 10000))
    def test_linear_regular_mapping(self, num, key_start, key_step, value_start, value_step):
        assume(key_step != 0)
        assume(value_step != 0)
        mapping = {key: value for key, value in zip(range(key_start, key_start + num*key_step, key_step),
                                                    range(value_start, value_start + num*value_step, value_step))}
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))

    @given(dictionary((int, int), int))
    def test_arbitrary_mapping(self, mapping):
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))

    @given(i_start=integers_in_range(0, 10),
           i_num=integers_in_range(1, 10),
           i_step=just(1),
           j_start=integers_in_range(0, 10),
           j_num=integers_in_range(1, 10),
           j_step=just(1),
           c=integers_in_range(1, 10))
    def test_linear_regular_mapping_2d(self, i_start, i_num, i_step, j_start, j_num, j_step, c):
        assume(i_step != 0)
        assume(j_step != 0)

        def v(i, j):
            return (i - i_start) * ((j_start + j_num*j_step) - j_start) + (j - j_start) + c

        mapping = {(i, j): v(i, j)
                   for i in range(i_start, i_start + i_num*i_step, i_step)
                   for j in range(j_start, j_start + j_num*j_step, j_step)}

        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))