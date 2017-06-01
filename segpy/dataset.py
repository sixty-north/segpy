from abc import ABCMeta, abstractmethod

from segpy.datatypes import DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE, SEG_Y_TYPE_DESCRIPTION


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

    @abstractmethod
    def trace_indexes(self):
        """An iterator over zero-based trace_samples indexes.

        Returns:
            An iterator which yields integers in the range zero to
            num_traces - 1
        """
        raise NotImplementedError

    @abstractmethod
    def num_traces(self):
        """The number of traces."""
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

    @property
    def data_sample_format(self):
        """The data type of the samples in machine-readable form. One of the values from datatypes.DATA_SAMPLE_FORMAT.
        """
        return DATA_SAMPLE_FORMAT_TO_SEG_Y_TYPE[self.binary_reel_header.data_sample_format]

    @property
    def data_sample_format_description(self):
        """A descriptive human-readable description of the data sample format
        """
        return SEG_Y_TYPE_DESCRIPTION[self.data_sample_format]


class DelegatingDataset(Dataset):
    """A Dataset which by default forwards to a source Dataset.

    This base class is useful if you only want to override a
    few methods to perform transformations.
    """

    def __init__(self, source_dataset):
        self._source = source_dataset

    @property
    def source(self):
        return self._source

    def trace_samples(self, trace_index, start=None, stop=None):
        return self._source.trace_samples(trace_index, start, stop)

    @property
    def textual_reel_header(self):
        return self._source.textual_reel_header

    def trace_header(self, trace_index):
        return self._source.trace_header(trace_index)

    @property
    def binary_reel_header(self):
        return self._source.binary_reel_header

    def trace_indexes(self):
        return self._source.trace_indexes()

    def num_traces(self):
        """The number of traces."""
        return self._source.num_traces()

    @property
    def dimensionality(self):
        return self._source.dimensionality

    @property
    def extended_textual_header(self):
        return self._source.extended_textual_header

    @property
    def encoding(self):
        return self._source.encoding

    @property
    def endian(self):
        return self._source.endian
