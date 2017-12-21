
from bisect import bisect_left
from collections.abc import Sequence, Set
from itertools import chain


class SortedFrozenSet(Sequence, Set):

    def __new__(cls, items=None):
        if type(items) == cls:
            return items
        obj = object.__new__(cls)
        obj._items = sorted(set(items)) if items is not None else []
        return obj

    def __contains__(self, item):
        try:
            self.index(item)
            return True
        except ValueError:
            return False

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        result = self._items[index]
        return SortedFrozenSet(result) if isinstance(index, slice) else result

    def __repr__(self):
        return "SortedFrozenSet({})".format(repr(self._items) if self._items else '')

    def __eq__(self, rhs):
        if not isinstance(rhs, SortedFrozenSet):
            return False
        return self._items == rhs._items

    def index(self, item):
        # TODO: Add support for start and stop
        index = bisect_left(self._items, item)
        if (index != len(self._items)) and self._items[index] == item:
            return index
        raise ValueError("{} not found".format(repr(item)))

    def count(self, item):
        return int(item in self._items)

    def __add__(self, rhs):
        return SortedFrozenSet(chain(self._items, rhs._items))

    def __mul__(self, rhs):
        return SortedFrozenSet(self) if rhs > 0 else SortedFrozenSet()

    def __rmul__(self, lhs):
        return self * lhs

    def issubset(self, iterable):
        return self <= SortedFrozenSet(iterable)

    def issuperset(self, iterable):
        return self >= SortedFrozenSet(iterable)

    def intersection(self, iterable):
        return self & SortedFrozenSet(iterable)

    def union(self, iterable):
        return self | SortedFrozenSet(iterable)

    def symmetric_difference(self, iterable):
        return self ^ SortedFrozenSet(iterable)

    def difference(self, iterable):
        return self - SortedFrozenSet(iterable)
