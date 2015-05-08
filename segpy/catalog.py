"""Catalogs are immutable mappings useful for building indexes.

This module contains definitions of many different catalog types,
all of which implement the interface defined by the Catalog abstract
base class, which is itself implements the mapping protocol.

Rather than constructing Catalog subtypes directly, prefer to use
the CatalogBuilder class which will analyse the contents of the
mapping to find a space and time efficient representation.
"""

from collections import Mapping, Sequence, OrderedDict
from fractions import Fraction
import reprlib
from segpy.sorted_set import SortedFrozenSet

from segpy.util import contains_duplicates, measure_stride, make_sorted_distinct_sequence


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
            mapping: An optional mapping (such as a dictionary) of items.
        """
        self._catalog = []
        if mapping is not None:
            for key, value in mapping.items():
                self.add(key, value)

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

        if len(self._catalog) < 2:
            return DictionaryCatalog(self._catalog)

        # In-place sort by index
        self._catalog.sort(key=lambda index_value: index_value[0])

        if contains_duplicates(index for index, value in self._catalog):
            return None

        if all(isinstance(index, Sequence) and (len(index) == 2)
               for index, value in self._catalog):
            return self._create_catalog_2()

        return self._create_catalog_1()

    def _create_catalog_1(self):
        """Create a catalog for one-dimensional integer keys (i.e. scalars)
        """
        index_min = self._catalog[0][0]
        index_max = self._catalog[-1][0]
        index_stride = measure_stride(index for index, value in self._catalog)
        assert index_stride != 0

        value_start = self._catalog[0][1]
        value_stop = self._catalog[-1][1]
        value_stride = measure_stride(value for index, value in self._catalog)

        if index_stride is None and value_stride is None:
            # Dictionary strategy - arbitrary keys and values
            return DictionaryCatalog(self._catalog)

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
        i_sorted = make_sorted_distinct_sequence(i for (i, j), value in self._catalog)
        j_sorted = make_sorted_distinct_sequence(j for (i, j), value in self._catalog)

        i_is_regular = isinstance(i_sorted, range)
        j_is_regular = isinstance(j_sorted, range)

        if i_is_regular and j_is_regular:
            is_rm, diff = self._is_row_major(i_sorted, j_sorted)
            if is_rm:
                return RowMajorCatalog2D(i_sorted, j_sorted, diff)

        return DictionaryCatalog2D(i_sorted, j_sorted, self._catalog)

    def _is_row_major(self, i_sorted, j_sorted):
        i_min = i_sorted[0]
        j_min = j_sorted[0]
        j_max = j_sorted[-1]
        diff = None
        for (i, j), actual_value in self._catalog:
            proposed_value = (i - i_min) * (j_max + 1 - j_min) + (j - j_min)
            current_diff = actual_value - proposed_value
            if diff is None:
                diff = current_diff
            if current_diff != diff:
                return False, None
        return True, diff


class Catalog2D(Mapping):
    """An abstract base class for 2D catalogs.
    """

    def __init__(self, i_range, j_range):
        """Initialize a Catalog2D.

        Args:
            i_range: A range which can generate all and only valid i indexes.
            j_range: A range which can generate all and only valid j indexes.
        """
        self._i_range = i_range
        self._j_range = j_range

    @property
    def i_range(self):
        return self._i_range

    @property
    def j_range(self):
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

    def value_start(self):
        """Minimum value at key_min"""
        return self[self.key_min()]

    def value_stop(self):
        """Maximum value at key_max"""
        return self[self.key_max()]


class RowMajorCatalog2D(Catalog2D):
    """A mapping which assumes a row-major ordering of a two-dimensional matrix.

    This is the ordering of items in a two-dimensional matrix where in
    the (i, j) key tuple the j value changes fastest when iterating
    through the items in order.

    A RowMajorCatalog predicts the value v from the key (i, j) according to the
    following formula:

        v = (i - i_min) * j_max + (j - j_min) + c

    for
        i_min <= i <= i_max
        j_min <= j <= j_max

    and where c is an integer constant to allow zero- or one-based indexing.
    """

    def __init__(self, i_range, j_range, constant):
        """Initialize a RowMajorCatalog2D.

        Args:
            i_range: A range which can generate all and only valid i indexes.
            j_range: A range which can generate all and only valid j indexes.
            constant: The constant offset used to produce the value.
        """
        super().__init__(i_range, j_range)
        self._c = constant

    @property
    def constant(self):
        return self._c

    def __getitem__(self, key):
        if key not in self:
            raise KeyError("{!r} key {!r} out of range".format(self, key))
        i, j = key
        value = (i - self.i_min) * (self.j_max + 1 - self.j_min) + (j - self.j_min) + self._c
        return value

    def __contains__(self, key):
        return (key[0] in self._i_range) and \
               (key[1] in self._j_range)

    def __len__(self):
        return len(self._i_range) * len(self._j_range)

    def __iter__(self):
        yield from ((i, j) for i in self._i_range for j in self._j_range)

    def __repr__(self):
        return '{}(i_range={}, j_range={}, c={})'.format(
            self.__class__.__name__,
            self.i_range, self.j_range, self._c)


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
        return '{}(items={})'.format(
            self.__class__.__name__, reprlib.repr(self._items.items()))


class DictionaryCatalog2D(Catalog2D):
    """An immutable, ordered, dictionary mapping for 2D keys.
    """

    def __init__(self, i_range, j_range, items):
        super().__init__(i_range, j_range)
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
        return '{}(i_range={}, j_range={}, items={})'.format(
            self.j_range, self.j_range,
            self.__class__.__name__, reprlib.repr(self._items.items()))


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
        return 1 + (self._key_max - self._key_min) / self._key_stride

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
        """Initialize a RegularConstantCatalog.

        The catalog is initialized by a description with an iterable series of
        keys and a constant value to be associated with all the keys.

        Args:
            keys: An iterable series of distinct keys.
            key_max: The maximum key.
            key_stride: The difference between successive keys.
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
        return '{}(keys={}, value={})'.format(
            self.__class__.__name__,
            reprlib.repr(self._keys),
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
            raise ValueError("{} key range and values inconsistent".format(self.__class__.__name__))

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
        return '{}(key_min={}, key_max={}, key_stride={}, values={})'.format(
            self.__class__.__name__,
            self._key_min,
            self._key_max,
            self._key_stride,
            reprlib.repr(self._values))


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

        Args:
            key_min: The minimum key.
            key_max: The maximum key.
            key_stride: The difference between successive keys.
            value_start: The value corresponding to the minimum key.
            value_max: The value corresponding to the maximum key.

        Raises:
            ValueError: There is any inconsistency in the keys, strides,
                and/or values.
        """
        key_range = key_max - key_min
        if key_range % key_stride != 0:
            raise ValueError("{} key range {!r} is not "
                             "a multiple of key stride {!r}".format(
                                 self.__class__.__name__,
                                 key_stride,
                                 key_range))
        self._key_stride = key_stride

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
        return '{}(key_min={}, key_max{}, key_stride={}, value_start={}, value_stop={}, value_stride={})'.format(
            self.__class__.__name__,
            self._key_min,
            self._key_max,
            self._key_stride,
            self._value_start,
            self._value_stop,
            self._value_stride)
