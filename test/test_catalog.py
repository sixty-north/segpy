import unittest

from hypothesis import given, example
from hypothesis.specifiers import dictionary, just
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
