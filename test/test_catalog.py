import unittest

from hypothesis import given, example
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
        mapping = {key: value for key, value in zip(range(key_start, key_start + num*key_step, key_step),
                                                    range(value_start, value_start + num*value_step, value_step))}
        builder = CatalogBuilder(mapping)
        catalog = builder.create()
        shared_items = set(mapping.items()) & set(catalog.items())
        self.assertEqual(len(shared_items), len(mapping))