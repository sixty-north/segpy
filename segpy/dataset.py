from abc import ABCMeta, abstractmethod


class Dataset(metaclass=ABCMeta):

    @property
    @abstractmethod
    def textual_reel_header(self):
        """The textual real header as an immutable sequence of forty Unicode strings each 80 characters long.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def binary_reel_header(self):
        """The binary reel header.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def extended_textual_header(self):
        raise NotImplementedError

    @property
    def dimensionality(self):
        """The spatial dimensionality of the data: 3 for 3D seismic volumes, 2 for 2D seismic lines, 1 for a
        single trace_samples, otherwise 0.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def trace_indexes(self):
        """An iterator over zero-based trace_samples indexes.

        Returns:
            An iterator which yields integers in the range zero to
            num_traces - 1
        """
        raise NotImplementedError

    @abstractmethod
    def trace_header(self, trace_index):
        """The trace header for a given trace index.

        Args:
            trace_index: An integer in the range zero to num_traces() - 1

        Returns:
            A TraceHeader corresponding to the requested trace_samples.
        """
        raise NotImplementedError

    @abstractmethod
    def trace_samples(self, trace_index, start=None, stop=None):
        """The trace samples for a given trace index.

        Args:
            trace_index: An integer in the range zero to num_traces - 1

            start: Optional zero-based start sample index. The default
                is to read from the first (i.e. zeroth) sample.

            stop: Optional zero-based stop sample index. Following Python
                slice convention this is one beyond the end.

        Returns:
            A sequence of numeric trace_samples samples.
        """
        raise NotImplementedError

