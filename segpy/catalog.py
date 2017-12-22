"""Catalogs are immutable mappings useful for building indexes.

This module contains definitions of many different catalog types,
all of which implement the interface defined by the Catalog abstract
base class, which is itself implements the mapping protocol.

Rather than constructing Catalog subtypes directly, prefer to use
the CatalogBuilder class which will analyse the contents of the
mapping to find a space and time efficient representation.
"""
from collections import Mapping, Sequence, OrderedDict, Iterable
from fractions import Fraction
from itertools import product

from segpy.sorted_frozen_set import SortedFrozenSet
from segpy.util import (contains_duplicates, measure_stride, make_sorted_distinct_sequence,
                        is_sorted, first)


class CatalogBuilder(object):
    """Use a catalog builder to construct optimised, immutable mappings.

    A CatalogBuilder is useful when, depending on the particular keys and
    values used, a more compact or efficient representation of the mapping
    is possible than, say, a regular dictionary. The CatalogBuilder
    accumulates values and then, once all values have been added, analyzes
    the keys and values to produce a more optimized representation of the
    mapping.
    """

    def __init__(self, mapping=None):
        """Initialize a Catalog Builder.

        Args:
            mapping: An optional mapping (such as a dictionary) of items, or an
                iterable series of 2-tuples containing keys and values.

        Raises:
            TypeError: If mapping is not None and is neither of mapping nor iterable type.
            ValueError: If mapping is an iterable of tuples, and the tuples are not pairs.
        """
        if mapping is None:
            self._catalog = []
        elif isinstance(mapping, Mapping):
            self._catalog = list(mapping.items())
        elif isinstance(mapping, Iterable):
            self._catalog = []
            for pair in mapping:
                if len(pair) != 2:
                    raise ValueError("{!r} is not a pair. Catalogs can only be constructed "
                                     "from iterable series of 2-tuples.")
                self._catalog.append(pair)
        else:
            raise TypeError("Mapping must be either a mapping (e.g. dict), or an iterable "
                            "series of 2-tuples. {!r} does not qualify.")

    def add(self, index, value):
        """Add an item.

        Each index must be unique if create() is to be subsequently
        called successfully, although duplicate index values will be
        accepted by this call without complaint.

        """
        self._catalog.append((index, value))

    def create(self):
        """Create a possibly more optimized representation of the mapping.

        In this worst case, this method returns an object which is
        essentially an immutable dictionary. In the best case, the
        space savings can be vast.

        Returns:
            A mapping, if a unique mapping from indexes to values is
            possible, otherwise None.

        """

        # This method examines the contents of the mapping using
        # various heuristics to come up with a better representation.

        # In-place sort by index
        self._catalog.sort(key=first)

        if contains_duplicates(index for index, value in self._catalog):
            return None

        if all(isinstance(index, Sequence) and (len(index) == 2)
               for index, value in self._catalog):
            return self._create_catalog_2()

        return self._create_catalog_1()

    def _create_catalog_1(self):
        """Create a catalog for one-dimensional integer keys (i.e. scalars)
        """
        if len(self._catalog) <= 1:
            return DictionaryCatalog(self._catalog)

        index_min = self._catalog[0][0]
        index_max = self._catalog[-1][0]
        index_stride = measure_stride(index for index, value in self._catalog)
        assert index_stride != 0

        value_start = self._catalog[0][1]
        value_stop = self._catalog[-1][1]
        value_stride = measure_stride(value for index, value in self._catalog)

        if index_stride is not None and value_stride == 0:
            assert value_start == value_stop
            return RegularConstantCatalog(index_min,
                                          index_max,
                                          index_stride,
                                          value_start)

        if index_stride is None and value_stride == 0:
            assert value_start == value_stop
            return ConstantCatalog(
                    (index for index, value in self._catalog),
                    value_start)

        if index_stride is not None and value_stride is None:
            # Regular index - regular keys and arbitrary values
            return RegularCatalog(index_min,
                                  index_max,
                                  index_stride,
                                  (value for index, value in self._catalog))

        if (index_stride is not None) and (value_stride is not None):
            assert value_stride != 0
            return LinearRegularCatalog(index_min,
                                        index_max,
                                        index_stride,
                                        value_start,
                                        value_stop,
                                        value_stride)

        return DictionaryCatalog(self._catalog)

    def _create_catalog_2(self):
        """Create a catalog for two-dimensional integer keys.

        Each key must be a two-element sequence.
        """
        return (self.make_last_index_varies_quickest_catalog_2d()
             or self.make_first_index_varies_quickest_catalog_2d()
             or self.make_dictionary_catalog_2d())

    def make_last_index_varies_quickest_catalog_2d(self):
        self._catalog.sort(key=_first_then_second_index)
        sorted_sequences = self.make_sorted_ranges()
        if sorted_sequences is None:
            return None
        return LastIndexVariesQuickestCatalog2D(*sorted_sequences)

    def make_first_index_varies_quickest_catalog_2d(self):
        self._catalog.sort(key=_second_then_first_index)
        sorted_sequences = self.make_sorted_ranges()
        if sorted_sequences is None:
            return None
        return FirstIndexVariesQuickestCatalog2D(*sorted_sequences)

    def make_dictionary_catalog_2d(self):
        self._catalog.sort(key=_first_then_second_index)
        i_sorted = make_sorted_distinct_sequence(i for (i, _), _ in self._catalog)
        j_sorted = make_sorted_distinct_sequence(j for (_, j), _ in self._catalog)
        return DictionaryCatalog2D(i_sorted, j_sorted, self._catalog)

    def make_sorted_ranges(self):
        i_sorted = make_sorted_distinct_sequence(i for (i, _), _ in self._catalog)
        j_sorted = make_sorted_distinct_sequence(j for (_, j), _ in self._catalog)
        if len(i_sorted) * len(j_sorted) != len(self._catalog):
            # The do not match so use a dictionary-based mapping
            return None
        vs = [v for (_, _), v in self._catalog]
        # Are the values unique and in ascending or descending order?
        if not (is_sorted(vs, reverse=False, distinct=True) or is_sorted(vs, reverse=True, distinct=True)):
            # The values are not both unique and sorted, so use a dictionary-based mapping
            return None
        v_sorted = make_sorted_distinct_sequence(vs, sense=None)
        i_is_regular = isinstance(i_sorted, range)
        j_is_regular = isinstance(j_sorted, range)
        v_is_regular = isinstance(v_sorted, range)
        if not (i_is_regular and j_is_regular and v_is_regular):
            # The i, j and v values are not regularly spaced, so use a dictionary-based mapping
            return None
        return i_sorted, j_sorted, v_sorted


class Catalog2D(Mapping):
    """An abstract base class for 2D catalogs.
    """

    def __init__(self, i_range, j_range):
        """Initialize a Catalog2D.

        Args:
            i_range: A range which can generate all and only valid i indexes.
            j_range: A range which can generate all and only valid j indexes.

        Raises:
            ValueError: If either i_range or j_range are not totally sorted.
        """
        if not is_sorted(i_range, distinct=True):
            raise ValueError("i indexes must be sorted and unique")
        if not is_sorted(j_range, distinct=True):
            raise ValueError("j indexes must be sorted and unique")
        self._i_range = i_range
        self._j_range = j_range

    @property
    def i_range(self):
        # TODO: This should be renamed, as it's not necessarily a range - just a sorted container (sequence?)
        return self._i_range

    @property
    def j_range(self):
        # TODO: This should be renamed, as it's not necessarily a range - just a sorted container (sequence?)
        return self._j_range

    @property
    def i_min(self):
        """Minimum i value"""
        return self._i_range[0]

    @property
    def i_max(self):
        """Maximum i value"""
        return self._i_range[-1]

    @property
    def j_min(self):
        """Minimum j value"""
        return self._j_range[0]

    @property
    def j_max(self):
        """Maximum j value"""
        return self._j_range[-1]

    def key_min(self):
        """Minimum (i, j) key"""
        return self.i_min, self.j_min

    def key_max(self):
        """Maximum (i, j) key"""
        return self.i_max, self.j_max

    def value_first(self):
        """Minimum value at key_min"""
        return self[self.key_min()]

    def value_last(self):
        """Maximum value at key_max"""
        return self[self.key_max()]


class LastIndexVariesQuickestCatalog2D(Catalog2D):

    def __init__(self, i_range, j_range, v_range):
        """
        Args:
            i_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid i keys.

            j_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid j keys.

            v_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid values.
        """
        num_indices = len(i_range) * len(j_range)
        if num_indices != len(v_range):
            raise ValueError("i_range={} and j_range={} totalling {} indices are incompatible with "
                             "v_range={} with length {}".format(i_range, j_range, num_indices, v_range, len(v_range)))
        super().__init__(i_range, j_range)
        self._v_range = v_range

    @property
    def v_range(self):
        return self._v_range

    def __getitem__(self, key):
        i, j = key
        if not self._contains(i, j):
            raise KeyError("Key {!r} not in {!r}".format(key, self))
        i_index = self.i_range.index(i)
        j_index = self.j_range.index(j)
        v_index = i_index * len(self.j_range) + j_index
        v = self._v_range[v_index]
        return v

    def __contains__(self, key):
        i, j = key
        return self._contains(i, j)

    def _contains(self, i, j):
        return (i in self.i_range) and (j in self.j_range)

    def __len__(self):
        return len(self.i_range) * len(self.j_range)

    def __iter__(self):
        return product(self.i_range, self.j_range)

    def __repr__(self):
        return '{}(i_range={}, j_range={}, v_range={})'.format(
            self.__class__.__name__,
            self.i_range, self.j_range, self._v_range)

    def key(self, value):
        """Given a value, get the corresponding key.

        Args:
            value: The value for which to find the key.

        Returns:
            A 2-tuple containing the (i, j) values corresponding
            to the given value.

        Raises:
            ValueError: If there is no corresponding key.
        """

        try:
            v_index = self._v_range.index(value)
        except ValueError:
            raise ValueError("{!r} is not a value of {!r}".format(value, self))
        i_index, j_index = divmod(v_index, len(self.j_range))
        i = self.i_range[i_index]
        j = self.j_range[j_index]
        return (i, j)


class FirstIndexVariesQuickestCatalog2D(Catalog2D):

    def __init__(self, i_range, j_range, v_range):
        """
        Args:
            i_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid i keys.

            j_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid j keys.

            v_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid values.
        """
        num_indices = len(i_range) * len(j_range)
        if num_indices != len(v_range):
            raise ValueError("i_range={} and j_range={} totalling {} indices are incompatible with "
                             "v_range={} with length {}".format(i_range, j_range, num_indices, v_range, len(v_range)))
        super().__init__(i_range, j_range)
        self._v_range = v_range

    @property
    def v_range(self):
        return self._v_range

    def __getitem__(self, key):
        i, j = key
        if not self._contains(i, j):
            raise KeyError("Key {!r} not in {!r}".format(key, self))
        i_index = self.i_range.index(i)
        j_index = self.j_range.index(j)
        v_index = j_index * len(self.i_range) + i_index
        v = self._v_range[v_index]
        return v

    def __contains__(self, key):
        i, j = key
        return self._contains(i, j)

    def _contains(self, i, j):
        return (i in self.i_range) and (j in self.j_range)

    def __len__(self):
        return len(self.i_range) * len(self.j_range)

    def __iter__(self):
        return ((i, j) for (j, i) in product(self.j_range, self.i_range))

    def __repr__(self):
        return '{}(i_range={}, j_range={}, v_range={})'.format(
            self.__class__.__name__,
            self.i_range, self.j_range, self._v_range)

    def key(self, value):
        """Given a value, get the corresponding key.

        Args:
            value: The value for which to find the key.

        Returns:
            A 2-tuple containing the (i, j) values corresponding
            to the given value.

        Raises:
            ValueError: If there is no corresponding key.
        """

        try:
            v_index = self._v_range.index(value)
        except ValueError:
            raise ValueError("{!r} is not a value of {!r}".format(value, self))
        j_index, i_index = divmod(v_index, len(self.i_range))
        i = self.i_range[i_index]
        j = self.j_range[j_index]
        return (i, j)


class DictionaryCatalog(Mapping):
    """An immutable, ordered, dictionary mapping.
    """

    def __init__(self, items):
        self._items = OrderedDict(items)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        return item in self._items

    def __repr__(self):
        return '{}(items=[<{} items>])'.format(
            self.__class__.__name__, len(self._items))


class DictionaryCatalog2D(Catalog2D):
    """An immutable, ordered, dictionary mapping for 2D keys.
    """

    def __init__(self, i_range, j_range, items):
        """Initialize a DictionaryCatalog2D.

        Args:
            i_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid i values.

            j_range: An ordered collection of evenly-spaced integers
                which can be used to generate valid j values.

            items: Either a) a mapping (dict) where the keys are 2-tuples containing i and j values
                contained within the respective ranges, and the value is an integer, or b) an
                iterable series of tuple structures ((i, j), v).

        Raises:
            TypeError: If items is not a dictionary or iterable of tuples.
            ValueError: If the i and j components of the keys in items are not contained within
                the respective i_range and j_range collections.
        """
        super().__init__(i_range, j_range)
        self._items = OrderedDict()
        if isinstance(items, Mapping):
            mapping = items.items()
        elif isinstance(items, Iterable):
            mapping = items
        else:
            raise TypeError("{} must be constructed from a mapping or an iterable of ((i, j), v) tuples, "
                            "not {}".format(self.__class__.__name__, items))

        for key, value in mapping:
            i, j = key
            if i not in i_range:
                raise ValueError("i={} not in i_range".format(i))
            if j not in j_range:
                raise ValueError("j={} not in j_range".format(j))
            self._items[key] = value

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        return item in self._items

    def __repr__(self):
        return '{}(i_range={}, j_range={}, items=[<{} items>])'.format(
            self.__class__.__name__,
            self.i_range, self.j_range,
            len(self._items))


class RegularConstantCatalog(Mapping):
    """Mapping with keys ordered with regular spacing along the number line.

    The values associated with the keys are constant.
    """

    def __init__(self, key_min, key_max, key_stride, value):
        """Initialize a RegularConstantCatalog.

        The catalog is initialized by a description of how the keys
        are distributed along the number line, and a value which
        corresponds with all keys.

        Args:
            key_min: The minimum key.
            key_max: The maximum key.
            key_stride: The difference between successive keys.
            value: A value associated with all keys.
        """
        if key_min > key_max:
            raise ValueError("key_min {} is greater than key_max {}, but key_min must be equal or less-than key_max."
                             .format(key_min, key_max))

        key_range = key_max - key_min
        if key_range % key_stride != 0:
            raise ValueError("RegularIndex key range {!r} is not "
                             "a multiple of stride {!r}".format(
                                 key_stride, key_range))

        self._key_min = key_min
        self._key_max = key_max
        self._key_stride = key_stride
        self._value = value

    def __getitem__(self, key):
        if key not in self:
            raise KeyError("{!r} does not contain key {!r}".format(self, key))
        return self._value

    def __len__(self):
        return 1 + (self._key_max - self._key_min) // self._key_stride

    def __contains__(self, key):
        return (self._key_min <= key <= self._key_max) and \
               ((key - self._key_min) % self._key_stride == 0)

    def __iter__(self):
        return iter(range(self._key_min,
                          self._key_max + 1,
                          self._key_stride))

    def __repr__(self):
        return '{}(key_min={}, key_max={}, key_stride={}, value={})'.format(
            self.__class__.__name__,
            self._key_min,
            self._key_max,
            self._key_stride,
            self._value)


class ConstantCatalog(Mapping):
    """Mapping with arbitrary keys and a single constant value.
    """

    def __init__(self, keys, value):
        """Initialize a ConstantCatalog.

        The catalog is initialized by a description with an iterable series of
        keys and a constant value to be associated with all the keys.

        Args:
            keys: An iterable series of keys.
            value: A value associated with all keys.
        """
        self._keys = SortedFrozenSet(keys)
        self._value = value

    def __getitem__(self, key):
        if key not in self:
            raise KeyError("{!r} does not contain key {!r}".format(self, key))
        return self._value

    def __len__(self):
        return len(self._keys)

    def __contains__(self, key):
        return key in self._keys

    def __iter__(self):
        return iter(self._keys)

    def __repr__(self):
        return '{}(keys=[{} items], value={})'.format(
            self.__class__.__name__,
            len(self._keys),
            self._value)


class RegularCatalog(Mapping):
    """Mapping with keys ordered with regular spacing along the number line.

    The values associated with the keys are arbitrary.
    """

    def __init__(self, key_min, key_max, key_stride, values):
        """Initialize a RegularCatalog.

        The catalog is initialized by a description of how the keys
        are distributed along the number line, and an iterable series of
        corresponding values.

        Args:
            key_min: The minimum key.
            key_max: The maximum key.
            key_stride: The difference between successive keys.
            values: An iterable series of values corresponding to the keys.

        Raises:
            ValueError: There is any inconsistency in the keys, stride,
                and/or values.
        """
        if key_min > key_max:
            raise ValueError("key_min {} is greater than key_max {}, but key_min must be equal or less-than key_max."
                             .format(key_min, key_max))

        key_range = key_max - key_min
        if key_range % key_stride != 0:
            raise ValueError("{} key range {!r} is not "
                             "a multiple of stride {!r}".format(self.__class__.__name__,
                                                                key_stride, key_range))
        self._key_min = key_min
        self._key_max = key_max
        self._key_stride = key_stride
        self._values = list(values)
        num_keys = 1 + key_range // key_stride
        if num_keys != len(self._values):
            raise ValueError("{} key range with length {} and values with length {} are inconsistent"
                             .format(self.__class__.__name__, num_keys, len(self._values)))

    def __getitem__(self, key):
        if not (self._key_min <= key <= self._key_max):
            raise KeyError("{!r} key {!r} out of range".format(self, key))
        offset = key - self._key_min
        if offset % self._key_stride != 0:
            raise KeyError("{!r} does not contain key {!r}".format(self, key))
        index = offset // self._key_stride
        return self._values[index]

    def __len__(self):
        return len(self._values)

    def __contains__(self, key):
        return (self._key_min <= key <= self._key_max) and \
               ((key - self._key_min) % self._key_stride == 0)

    def __iter__(self):
        return iter(range(self._key_min,
                          self._key_max + 1,
                          self._key_stride))

    def __repr__(self):
        return '{}(key_min={}, key_max={}, key_stride={}, values=[{} items])'.format(
            self.__class__.__name__,
            self._key_min,
            self._key_max,
            self._key_stride,
            len(self._values))


class LinearRegularCatalog(Mapping):
    """A mapping which assumes a linear relationship between keys and values.

    A LinearRegularCatalog predicts the value v from the key according to the
    following formula:

        v = (value_max - value_min) / (key_max - key_min) * (key - key_min) + value_min
    """

    def __init__(self,
                 key_min,
                 key_max,
                 key_stride,
                 value_start,
                 value_stop,
                 value_stride):
        """Initialize a LinearRegularCatalog.

        The catalog must contain at least two items.

        Args:
            key_min: The minimum key.
            key_max: The maximum key.
            key_stride: The difference between successive keys.
            value_start: The value corresponding to the minimum key.
            value_stop: The value corresponding to the maximum key.
            value_stride:

        Raises:
            ValueError: There is any inconsistency in the keys, strides,
                and/or values.
        """
        if key_min >= key_max:
            raise ValueError("key_min {} is greater-than or equal-to key_max {}, but key_min must be less-than key_max."
                             .format(key_min, key_max))

        if key_stride <= 0:
            raise ValueError("key_stride {} is not positive".format(key_stride))

        key_range = key_max - key_min
        if key_range % key_stride != 0:
            raise ValueError("{} key range {!r} is not "
                             "a multiple of key stride {!r}".format(
                                 self.__class__.__name__,
                                 key_stride,
                                 key_range))
        self._key_stride = key_stride

        if value_stride == 0:
            raise ValueError("value_stride {} cannot be zero".format(value_stride))

        value_range = value_stop - value_start
        if value_range % value_stride != 0:
            raise ValueError("{} value range {!r} is not "
                             "a multiple of value stride {!r}".format(
                                 self.__class__.__name__,
                                 value_stride,
                                 value_range))
        self._value_stride = value_stride

        self._key_min = key_min
        self._key_max = key_max
        self._value_start = value_start
        self._value_stop = value_stop

        num_keys = 1 + (self._key_max - self._key_min) // self._key_stride
        num_values = 1 + (self._value_stop - self._value_start) // self._value_stride
        if num_keys != num_values:
            raise ValueError("{} inconsistent number of "
                             "keys {} and values {}".format(
                                 self.__class__.__name__,
                                 num_keys,
                                 num_values))

        self._m = Fraction(self._value_stop - self._value_start,
                           self._key_max - self._key_min)

    def __getitem__(self, key):
        if not (self._key_min <= key <= self._key_max):
            raise KeyError("{!r} key {!r} out of range".format(self, key))
        offset = key - self._key_min
        if offset % self._key_stride != 0:
            raise KeyError("{!r} does not contain key {!r}".format(self, key))

        v = self._m * (key - self._key_min) + self._value_start
        assert v.denominator == 1
        return v.numerator

    def __len__(self):
        return 1 + (self._key_max - self._key_min) // self._key_stride

    def __contains__(self, key):
        return (self._key_min <= key <= self._key_max) and \
               ((key - self._key_min) % self._key_stride == 0)

    def __iter__(self):
        return iter(range(self._key_min, self._key_max + 1, self._key_stride))

    def __repr__(self):
        return '{}(key_min={}, key_max={}, key_stride={}, value_first={}, value_last={}, value_stride={})'.format(
            self.__class__.__name__,
            self._key_min,
            self._key_max,
            self._key_stride,
            self._value_start,
            self._value_stop,
            self._value_stride)


def _first_then_second_index(key):
    return (key[0][0], key[0][1])


def _second_then_first_index(key):
    return (key[0][1], key[0][0])