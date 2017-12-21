from collections.abc import Sequence


class ReversedSequenceView(Sequence):

    def __init__(self, sequence):
        self._sequence = sequence

    def __contains__(self, x):
        return x in self._sequence

    def __len__(self):
        return len(self._sequence)

    def __iter__(self):
        return reversed(self._sequence)

    def __getitem__(self, index):
        r = self._reverse_index(index)
        return self._sequence[r]

    def count(self, item):
        return self._sequence.count(item)

    def __reversed__(self):
        return self._sequence

    def index(self, item):
        # TODO: Add support for start and stop
        if self.count(item) == 1:
            return self._reverse_index(self._sequence.index(item))
        for index, value in enumerate(self):
            if value == item:
                return index
        raise ValueError("{} is not in {!r}".format(item, self))

    def _reverse_index(self, index):
        size = len(self)
        i = index + size if index < 0 else index
        if not (0 <= i < size):
            raise IndexError("Index {} out of range for {!r}".format(index, self))
        return size - i - 1

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self._sequence)
